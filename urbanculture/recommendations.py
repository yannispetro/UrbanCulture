import pandas as pd

from joblib import load
from nltk.stem import PorterStemmer

from sklearn.metrics.pairwise import cosine_similarity

import plotonmap as pltmap

ps = PorterStemmer()

def get_plot_handle(city,kws):
    dfc = pd.read_pickle(f'models/{city}_dfc.pkl.gz', compression='gzip')
    dfn = pd.read_pickle(f'models/{city}_dfn.pkl.gz', compression='gzip')
    dfc = keywords_score(kws, dfc, city)
    p = pltmap.plot_clusters(dfc, dfn, streets=True, colorScores=True)
    return p

def keywords_score(kws, dfc, city):
    pipe_airbnb  = load(f'models/world_pipe_airbnb.joblib')
    # pipe_reviews = load(f'models/{city}_pipe_reviews.joblib')
    kws = ' '.join(list(set([ps.stem(kw) for kw in kws])))

    kws_vec_airbnb = pipe_airbnb.transform([kws])
    cs_airbnb = lambda x: cosine_similarity(x.vec_airbnb,kws_vec_airbnb)[0][0]
    dfc['kws_score_airbnb'] = dfc.apply(cs_airbnb, axis=1)
    # dfc['kws_score_airbnb'] = dfc['kws_score_airbnb']/dfc['kws_score_airbnb'].sum()

    # kws_vec_reviews = pipe_reviews.transform([kws])
    # cs_reviews = lambda x: cosine_similarity(x.vec_reviews,kws_vec_reviews)[0][0]
    # dfc['kws_score_reviews'] = dfc.apply(cs_reviews, axis=1)
    # dfc['kws_score_reviews'] = dfc['kws_score_reviews']/dfc['kws_score_reviews'].sum()

    dfc['kws_score'] = dfc['kws_score_airbnb']*100 # + dfc['kws_score_reviews']
    dfc['kws_score_norm'] = dfc['kws_score']/dfc['kws_score'].max()

    dfc['alpha'] = 0.1 + (dfc['kws_score_norm'] - dfc['kws_score_norm'].min())/(dfc['kws_score_norm'].max() - dfc['kws_score_norm'].min())*0.5
    dfc['alpha'].fillna(0.1,inplace=True)

    return dfc
