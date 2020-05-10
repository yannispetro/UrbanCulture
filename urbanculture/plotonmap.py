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

map_style='[{"featureType":"administrative","elementType":"all","stylers":[{"visibility":"off"}]},{"featureType":"administrative","elementType":"labels.text.fill","stylers":[{"color":"#444444"}]},{"featureType":"landscape","elementType":"all","stylers":[{"color":"#f2f2f2"}]},{"featureType":"poi","elementType":"geometry.fill","stylers":[{"saturation":"-100"},{"lightness":"57"}]},{"featureType":"poi","elementType":"geometry.stroke","stylers":[{"lightness":"1"}]},{"featureType":"poi","elementType":"labels","stylers":[{"visibility":"off"}]},{"featureType":"road","elementType":"all","stylers":[{"saturation":-100},{"lightness":45}]},{"featureType":"road.highway","elementType":"all","stylers":[{"visibility":"simplified"}]},{"featureType":"road.arterial","elementType":"labels.icon","stylers":[{"visibility":"off"}]},{"featureType":"transit","elementType":"all","stylers":[{"visibility":"off"}]},{"featureType":"transit","elementType":"geometry","stylers":[{"visibility":"on"}]},{"featureType":"transit.line","elementType":"geometry","stylers":[{"visibility":"off"}]},{"featureType":"transit","elementType":"labels","stylers":[{"visibility":"off"}]},{"featureType":"transit","elementType":"labels.text","stylers":[{"visibility":"off"}]},{"featureType":"transit","elementType":"labels.text.fill","stylers":[{"visibility":"off"},{"color":"#484848"}]},{"featureType":"transit","elementType":"labels.text.stroke","stylers":[{"visibility":"off"}]},{"featureType":"transit","elementType":"labels.icon","stylers":[{"visibility":"on"}]},{"featureType":"transit.station.bus","elementType":"all","stylers":[{"visibility":"on"}]},{"featureType":"transit.station.bus","elementType":"labels.text.fill","stylers":[{"saturation":"0"},{"lightness":"0"},{"gamma":"1.00"},{"weight":"1"}]},{"featureType":"transit.station.bus","elementType":"labels.icon","stylers":[{"saturation":"-100"},{"weight":"1"},{"lightness":"0"}]},{"featureType":"transit.station.rail","elementType":"all","stylers":[{"visibility":"on"}]},{"featureType":"transit.station.rail","elementType":"labels.text.fill","stylers":[{"gamma":"1"},{"lightness":"40"}]},{"featureType":"transit.station.rail","elementType":"labels.icon","stylers":[{"saturation":"-100"},{"lightness":"30"}]},{"featureType":"water","elementType":"all","stylers":[{"color":"#d2d2d2"},{"visibility":"on"}]}]'

def plot_clusters(dfc, dfn, streets=False, colorScores=False, hoverCirclesColor=None):
    if 'kws_score' not in dfc:
        dfc['kws_score'] = '-'
        dfc['alpha'] = 0.4
    v_x = list(itertools.chain.from_iterable(list(dfc.verts_x)))
    v_y = list(itertools.chain.from_iterable(list(dfc.verts_y)))
    X = np.array([v_x,v_y]).transpose()
    N_clusters = len(dfc)
    if isinstance(dfn, type(None)):
        TOOLTIPS = None
    else:
        TOOLTIPS = [('kws score', "@score"),('#Listings', "@nlist"),('av. price', "@cprice"),
                    ('n\'hood 1', "@n1data"),('n\'hood 2', "@n2data"),('n\'hood 3', "@n3data")]

    if streets:
        angle = max(X[:,0]) - min(X[:,0])
        angle = angle if angle > 0 else 360 + angle
        zm = int( np.round( log(5.5*96 * 360/angle/120)/log(2) ) )
        map_options = GMapOptions(lat = np.mean(X[:,1]),lng = np.mean(X[:,0]),
                                  map_type="roadmap", zoom=zm, styles=map_style )

        api_key = os.environ['GOOGLE_API_KEY']
        p = gmap(api_key, map_options, sizing_mode='scale_both')
        p.add_tools( HoverTool(tooltips=TOOLTIPS) )
        p.toolbar.active_scroll = p.toolbar.tools[1]
        p.toolbar_location = None
    else:
        p = figure(background_fill_color = '#FFFFFF',
                   tooltips=TOOLTIPS,
                   tools='hover,wheel_zoom',
                   aspect_ratio='auto',
                   sizing_mode='scale_both')


    colorIds = list(np.round(np.linspace(0, len(colorList) - 1, max(dfc.index)+1)).astype(int))
    for i in dfc.index:
        verts_x = dfc.loc[i,'verts_x']
        verts_y = dfc.loc[i,'verts_y']
        if colorScores:
            color = "#64a19d"
            fill_alpha = dfc.loc[i,'alpha']
        else:
            color   = colorList[colorIds][i]
            fill_alpha = 0.4

        score,nlist,cprice,n1data,n2data,n3data = ['-'],['-'],['-'],['-'],['-'],['-']
        dmp = dfn[dfn['cluster']==dfc.loc[i,'cluster']]
        dmc = dfc[dfc['cluster']==dfc.loc[i,'cluster']]
        if len(dmp) > 0:
            score  = [list(dmc['kws_score_norm'])[0]]
            nlist  = [list(dmc['cluster #listings'])[0]]
            cprice = [list(dmp['cluster av. price'])[0]]
            if len(dmp)>0:
                n1data = [f'{dmp.iloc[0,2]} {dmp.iloc[0,1]} ({dmp.iloc[0,5]})']
            if len(dmp)>1:
                n2data = [f'{dmp.iloc[1,2]} {dmp.iloc[1,1]} ({dmp.iloc[1,5]})']
            if len(dmp)>2:
                n3data = [f'{dmp.iloc[2,2]} {dmp.iloc[2,1]} ({dmp.iloc[2,5]})']

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
