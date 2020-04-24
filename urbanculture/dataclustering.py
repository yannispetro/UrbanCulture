import heapq

import numpy as np
import pandas as pd
from tqdm.auto import tqdm
from scipy.spatial import ConvexHull
from scipy.spatial.qhull import QhullError
from scipy.stats import multivariate_normal as mvn
from math import radians, sin, cos, acos
from joblib import load

from sklearn.neighbors.kde import KernelDensity
from sklearn.cluster import KMeans

tqdm.pandas()

# from bokeh.palettes import Turbo256 as palette
# colorList = np.array(palette)

def exclude_outliers(dfb0, percent=0.05,plot=True):
    X = np.array(dfb0[['longitude','latitude']])
    kde = KernelDensity(kernel='gaussian', bandwidth=0.2).fit(X)
    scrs = kde.score_samples(X)
    dfb0['scr_0'] = scrs
    threshold = dfb0['scr_0'].quantile(percent)
    X1 = X[scrs < threshold,:]
    X = X[scrs >= threshold,:]
    if plot:
        p = figure(plot_width=400, plot_height=400,title='Outliers',toolbar_location=None)
        p.circle(X[:,0],X[:,1], color="navy", alpha=0.5)
        p.circle(X1[:,0],X1[:,1], alpha = 0.5, color = 'red')
        show(p)

    dfb = dfb0[dfb0.scr_0 >= threshold].copy()
    return X, dfb

def findClosest(X, n, target):
    vals = {}
    i = 10; j = n; mid = 0
    while (i < j):
        mid = (i + j) // 2

        if mid-1 in vals:
            v0 = vals[mid-1]
        else:
            v0 = kmeans_N(X,mid-1)
            vals[mid-1] = v0
        if mid in vals:
            v1 = vals[mid]
        else:
            v1 = kmeans_N(X,mid)
            vals[mid] = v1
        if mid+1 in vals:
            v2 = vals[mid+1]
        else:
            v2 = kmeans_N(X,mid+1)
            vals[mid+1] = v2
        # print(mid,v1)

        if (target > v1) :
            if (mid > 0 and target < v0):
                return getClosest(v0, mid-1, v1, mid, target)
            # Repeat for left half
            j = mid
        # If target is greater than mid
        else :
            if (mid < n - 1 and target > v2):
                return getClosest(v1, mid, v2, mid+1, target)
            i = mid + 1
    return mid

def getClosest(val1, i1, val2, i2, target):
    if (target - val1 >= val2 - target):
        return i2
    else:
        return i1

def distance(points):
    p1, p2 = points[0], points[1]
    slat, slon = radians(p1[1]), radians(p1[0])
    elat, elon = radians(p2[1]), radians(p2[0])
    arg = sin(slat)*sin(elat) + cos(slat)*cos(elat)*cos(slon - elon)
    arg =  1 if arg >  1 else arg
    arg = -1 if arg < -1 else arg
    return 6371.01 * acos(arg)

def kmeans_N(X,N):
    kmeans = KMeans(n_clusters=N, random_state=0).fit(X)
    Y_, centers = kmeans.labels_, kmeans.cluster_centers_
    dists = list(map(distance, zip(X, map(lambda x: centers[x], Y_))))
    [dists.remove(el) for el in heapq.nlargest(len(X)//20,dists)];
    return sum(dists)/len(dists)

def kmeans_(X):
    N_clusters = findClosest(X, min(len(X),1000), 0.2)
    kmeans = KMeans(n_clusters=N_clusters, random_state=0).fit(X)
    print(N_clusters, ' clusters')
    return kmeans, N_clusters

def get_cluster_data( city, X, kmeans, N_clusters, dfb, dfal2 ):
    predict_cluster = lambda x: kmeans.predict(np.array([[x.longitude,x.latitude]]))[0]
    dfb['cluster']       = dfb.apply(predict_cluster, axis=1)
    Y_ = kmeans.predict(X)

    dfc = pd.DataFrame(columns=['cluster','mean','covar','verts_x','verts_y'])
    for i in range(N_clusters):
        Xi = X[Y_ == i, :]
        dfc.loc[i,'cluster'] = i
        dfc.loc[i,'mean']  = [np.mean(Xi[:,0]),np.mean(Xi[:,1])]
        dfc.loc[i,'covar'] = np.cov(np.transpose(Xi))

    def cluster_location_score(row):
        xy = [row.longitude,row.latitude]
        mean  = dfc.loc[row.cluster,'mean']
        covar = dfc.loc[row.cluster,'covar']
        try:
            scr = mvn.pdf(xy,mean,covar)/mvn.pdf(mean,mean,covar)
        except:
            emptyClusters.add(row.cluster)
            scr = 0
        return scr

    emptyClusters = set()
    dfb['cluster_score'] = dfb.apply(cluster_location_score, axis=1)

    threshold = dfb['cluster_score'].quantile(0.05)
    dfb_tmp = dfb[dfb['cluster_score'] >= threshold]

    for i in range(N_clusters):
        Xi = np.array(dfb_tmp[dfb_tmp['cluster'] == i ][['longitude','latitude']])
        if len(Xi[:,0]) > 3:
            try:
                Vs = Xi[ConvexHull(Xi).vertices,:]
                dfc.loc[i,'verts_x'] = list(Vs[:,0])
                dfc.loc[i,'verts_y'] = list(Vs[:,1])
            except QhullError:
                dfc.loc[i,'verts_x'] = list(Xi[:,0])
                dfc.loc[i,'verts_y'] = list(Xi[:,1])
        else:
            emptyClusters.add(i)

    dfc.drop( dfc[ dfc['cluster'].isin(emptyClusters) ].index , inplace=True)
    # print('empty clusters: ',emptyClusters)

    predict_cluster = lambda x: kmeans.predict(np.array([[x.longitude,x.latitude]]))[0]
    sum_text        = lambda x: '%s' % ' '.join(x)
    dfal2['cluster'] = dfal2.apply(predict_cluster, axis=1)
    dfc_tmp = dfal2.groupby('cluster')['stemmed_neighborhood_overview'].apply(sum_text).to_frame(name='text_airbnb')
    dfc_tmp2 = dfal2.groupby('cluster')['stemmed_reviews'].apply(sum_text).to_frame(name='text_reviews')
    dfc_tmp = dfc_tmp.merge(dfc_tmp2, how='left', on='cluster')

    tfidf_airbnb  = load('models/' +  city + '_tfidf_airbnb.joblib')
    tfidf_reviews = load('models/' +  city + '_tfidf_reviews.joblib')
    # print('tfidf vectorization of neighborhood overview -->')
    dfc_tmp['vec_airbnb'] = dfc_tmp.apply(lambda x: tfidf_airbnb.transform([x.text_airbnb]), axis = 1)
    # print('tfidf vectorization of reviews -->')
    dfc_tmp['vec_reviews'] = dfc_tmp.apply(lambda x: tfidf_reviews.transform([x.text_reviews]), axis = 1)

    dfc_tmp = dfc_tmp.drop(columns=['text_airbnb','text_reviews'])
    dfc_tmp.drop( dfc_tmp[ dfc_tmp.index.isin(emptyClusters) ].index , inplace=True)
    dfc = dfc.merge(dfc_tmp, how = 'inner', on ='cluster', left_index=True, right_index=True)

    return dfb, dfc
