# from tqdm import tqdm, tqdm_notebook
from collections import Counter

import numpy as np
import pandas as pd
from tqdm.auto import tqdm
from joblib import dump, load
from decimal import Decimal
from re import sub

from nltk.corpus import stopwords
import string
from nltk.stem import PorterStemmer

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

tqdm.pandas()

ps = PorterStemmer()
tfidf_airbnb = TfidfVectorizer(max_features=10000)
sum_text = lambda x: '%s' % ' '.join(x)

def load_data(city):
    dfal = pd.read_csv(f'data/{city}_listings.csv.gz', compression='gzip')
    dfrev = pd.read_csv(f'data/{city}_reviews.csv.gz', compression='gzip')
    dfrev = dfrev.loc[dfrev.comments.apply(type) == str]
    dfrev = dfrev.groupby('listing_id')['comments'].apply(sum_text).to_frame(name='text_reviews')
    dfal = dfal.merge(dfrev, how = 'left', left_on='id', right_on='listing_id')
    return dfal

def stemming(dfal):
    dfal.dropna(subset=['latitude','longitude'],inplace=True)
    dfal['price_float'] = dfal.apply(lambda x: float(Decimal(sub(r'[^\d.]', '', x.price))), axis=1)

    stop_words = set(stopwords.words('english'))
    punct = list(string.punctuation)

    def clean_text(text):
        if isinstance(text, str):
            for ch in punct:
                text = text.replace(ch, '')
            word_tokens = text.lower().split()
            clean_text = [ps.stem(w) for w in word_tokens if not w in stop_words]
            ct = ' '.join(clean_text)
            return ct
        else:
            return None

    # print('stemming neighborhood overview -->')
    dfal['stemmed_neighborhood_overview'] = dfal['neighborhood_overview'].apply(clean_text)
    # print('stemming reviews -->')
    dfal['stemmed_reviews'] = dfal['text_reviews'].progress_apply(clean_text)
    dfal = dfal.drop(columns=['neighborhood_overview','text_reviews'])
    return dfal

def fit_tfidfs(dfal, city):
    dfal2 = dfal.dropna(subset=['stemmed_neighborhood_overview'], how='any').copy()
    dfal2['stemmed_reviews'].fillna(' ', inplace = True)

    tfidf_airbnb = TfidfVectorizer(max_features=10000)
    tfidf_airbnb.fit(list(dfal2.stemmed_neighborhood_overview))

    tfidf_reviews = TfidfVectorizer(max_features=10000)
    tfidf_reviews.fit(list(dfal2.stemmed_reviews))

    dump(tfidf_airbnb,  f'models/{city}_tfidf_airbnb.joblib', compress=9)
    dump(tfidf_reviews, f'models/{city}_tfidf_reviews.joblib', compress=9)

    return dfal2

def extractMostRelevant(dfal2, city, rbc = ['restaurant','bar','coffee'], percent=0.15):
    rbc = ' '.join(list(set([ps.stem(kw) for kw in rbc])))
    tfidf_airbnb = load(f'models/{city}_tfidf_airbnb.joblib')
    rbc_vec_airbnb = tfidf_airbnb.transform([rbc])

    # print('calculating rbc scores -->')
    vectorize = lambda x: tfidf_airbnb.transform([x.stemmed_neighborhood_overview])
    cs_airbnb = lambda x: cosine_similarity(vectorize(x),rbc_vec_airbnb)[0][0]
    dfal2['rbc_score_airbnb'] = dfal2.apply(cs_airbnb, axis=1)

    df_rbc = dfal2[dfal2['rbc_score_airbnb'] > dfal2['rbc_score_airbnb'].quantile(1-percent)].copy()
    return df_rbc

def get_neighborhood_data( dfal, dfc, kmeans ):
    if 'neighbourhood_cleansed' in dfal:
        neigh_column = 'neighbourhood_cleansed'
    else:
        neigh_column = 'neighbourhood'
    predict_cluster = lambda x: kmeans.predict(np.array([[x.longitude,x.latitude]]))[0]
    def cluster_location_score(row):
        xy = [row.longitude,row.latitude]
        mean  = dfc.loc[row.cluster,'mean']
        covar = dfc.loc[row.cluster,'covar']
        return mvn.pdf(xy,mean,covar)/mvn.pdf(mean,mean,covar)

    def nbrhood_freq(row):
        D = row[neigh_column]
        sm = sum(D.values())
        return {x:[y/sm,y] for x, y in D.items() if y/sm > 0.15}

    def neghborhood_dataframe(dfcn,dfal2):
        dfcn['cluster'] = dfcn.index
        dfn = pd.DataFrame(columns=['cluster','neighborhood','membership',
                                    '#listings','cluster #listings','av. price','cluster av. price'])
        for i in dfcn.index:
            cl = dfcn.cluster[i]
            avpc = dfcn.price_float[i]
            nlist = dfcn.id[i]
            D = sorted(dfcn[neigh_column][i].items(), key=lambda kv: kv[1][0], reverse=True)
            for (n, f) in D:
                avp = dfal2[(dfal2['cluster'] == cl) & (dfal2[neigh_column] == n)].price_float.mean()
                row = {'cluster'          : cl,
                       'neighborhood'     : n,
                       'membership'       : '{:.0f}%'.format(f[0]*100),
                       '#listings'        : int(f[1]),
                       'cluster #listings': nlist,
                       'av. price'        : '${:.2f}'.format(avp),
                       'cluster av. price': '${:.2f}'.format(avpc)}
                dfn = dfn.append(row,ignore_index=True)
        return dfn

    # print('assigning clusters -->')
    dfal['cluster'] = dfal.apply(predict_cluster, axis=1)

    dfcn = dfal.groupby('cluster').agg({'id'          : 'count',
                                        'price_float' :'mean',
                                        neigh_column  :lambda x: Counter(x)})

    dfcn[neigh_column] = dfcn.apply(nbrhood_freq,axis = 1)

    dfn = neghborhood_dataframe(dfcn,dfal)
    del dfcn

    return dfn
