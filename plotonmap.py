import os
import itertools

import numpy as np
import pandas as pd
from math import log

from bokeh.resources import INLINE
from bokeh.io import output_file, output_notebook
from bokeh.models import ColumnDataSource, GMapOptions, Ellipse, HoverTool, Patches, Patch
from bokeh.plotting import gmap, figure, show
from bokeh.palettes import Turbo256 as palette

# output_file("gmap.html")
# output_notebook(INLINE)

colorList = np.array(palette)


def plot_clusters(dfc, dfn, streets=False, colorScores=False, hoverCirclesColor=None):
    if 'kws_score' not in dfc:
        dfc['kws_score'] = '-'
        dfc['alpha'] = 0.4
    v_x = list(itertools.chain.from_iterable(list(dfc.verts_x)))
    v_y = list(itertools.chain.from_iterable(list(dfc.verts_y)))
    X = np.array([v_x,v_y]).transpose()
    N_clusters = len(dfc)
    # Y_ = kmeans.predict(X)
    if isinstance(dfn, type(None)):
        TOOLTIPS = None
    else:
        TOOLTIPS = [('kws score', "@score"),('#Listings', "@nlist"),('av. price', "@cprice"),
                    ('n\'hood 1', "@n1data"),('n\'hood 2', "@n2data"),('n\'hood 3', "@n3data")]

    if streets:
        angle = max(X[:,0]) - min(X[:,0])
        angle = angle if angle > 0 else 360 + angle
        zm = int( np.round( log(5.5*96 * 360/angle/256)/log(2) ) )
        map_options = GMapOptions(lat = np.mean(X[:,1]),lng = np.mean(X[:,0]),
                                  map_type="roadmap", zoom=zm )

        api_key = os.environ['GOOGLE_API_KEY']
        p = gmap(api_key, map_options, sizing_mode="scale_both")
        p.add_tools( HoverTool(tooltips=TOOLTIPS) )
    else:
        p = figure(background_fill_color = '#FFFFFF',
                   tooltips=TOOLTIPS,
                   tools='hover,wheel_zoom',
                   sizing_mode="scale_both")


    colorIds = list(np.round(np.linspace(0, len(colorList) - 1, max(dfc.index)+1)).astype(int))
    for i in list(dfc['cluster']):
        mean    = np.array(dfc.loc[i,'mean'])
        covar   = np.array(dfc.loc[i,'covar'])
        verts_x = dfc.loc[i,'verts_x']
        verts_y = dfc.loc[i,'verts_y']
        if colorScores:
            color = "#0275d8"
            fill_alpha = dfc.loc[i,'alpha']
        else:
            color   = colorList[colorIds][i]
            fill_alpha = 0.4

        score,nlist,cprice,n1data,n2data,n3data = ['-'],['-'],['-'],['-'],['-'],['-']
        # centers = np.array(list(dfc['mean']))
        # p.circle(centers[:, 0], centers[:, 1], size=2, color=color, alpha = 0.2)
        dmp = dfn[dfn['cluster']==i]
        dmc = dfc[dfc['cluster']==i]
        if len(dmp) > 0:
            score  = [list(dmc['kws_score'])[0]]
            nlist  = [list(dmp['cluster #listings'])[0]]
            cprice = [list(dmp['cluster av. price'])[0]]
            if len(dmp)>0:
                n1data = [str(dmp.iloc[0,2])+' '+str(dmp.iloc[0,1])+' ('+str(dmp.iloc[0,5])+')']
            if len(dmp)>1:
                n2data = [str(dmp.iloc[1,2])+' '+str(dmp.iloc[1,1])+' ('+str(dmp.iloc[1,5])+')']
            if len(dmp)>2:
                n3data = [str(dmp.iloc[2,2])+' '+str(dmp.iloc[2,1])+' ('+str(dmp.iloc[2,5])+')']

        srcP = ColumnDataSource( dict(x=list(verts_x),y=list(verts_y)) )
        p.patch(x='x',y='y', fill_color=color, fill_alpha=fill_alpha, line_color=None, source=srcP)

        srcC = ColumnDataSource( dict(x=[(max(verts_x)+min(verts_x))/2],
                                      y=[(max(verts_y)+min(verts_y))/2],
                                      score=score,nlist=nlist, cprice=cprice,
                                      n1data=n1data, n2data=n2data, n3data=n3data)
                                )
        cr = max( max(verts_x)-min(verts_x),max(verts_y)-min(verts_y) )
        p.circle(x='x', y='y', radius = cr*50000,
                 fill_color=hoverCirclesColor,
                 fill_alpha=0.5,line_color=None, source=srcC
                 )
        p.axis.visible = False

    # show(p)
    return p
