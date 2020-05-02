import pandas as pd
import numpy as np
import heapq

from joblib import load
from nltk.stem import PorterStemmer

from sklearn.metrics.pairwise import cosine_similarity
from gensim.models import Word2Vec
from gensim.models import KeyedVectors

import urbanculture.plotonmap as pltmap

model_name = 'fasttext'

def get_plot_handle(city,kws):
    dfc = pd.read_pickle(f'urbanculture/citydata/{city}_dfc.pkl.gz', compression='gzip')
    dfn = pd.read_pickle(f'urbanculture/citydata/{city}_dfn.pkl.gz', compression='gzip')

    dfc = keywords_score(kws, dfc, city)
    p = pltmap.plot_clusters(dfc, dfn, streets=True, colorScores=True)
    return p

def keywords_score(kws, dfc, city):
    model = KeyedVectors.load(f'urbanculture/models/{model_name}_{2565472}')

    def calculate_similarities(x):
        score = 0
        count = 0
        for w in most_similar:
            if w in x:
                score += most_similar[w]*x[w]
                count += x[w]
        if count:
            return score/np.log(sum(x.values())/count)
        return 0

    kws = list(set([kw for kw in kws]))
    most_similar = dict(model.wv.most_similar(positive=kws, topn=20))

    # kws_vec_airbnb = model.wv.__getitem__(kws).reshape(len(kws),-1)

    dfc['kws_score_airbnb'] = dfc['freq_dict'].apply(calculate_similarities)

    dfc['kws_score'] = dfc['kws_score_airbnb']*100
    dfc['kws_score'] = dfc['kws_score'] - dfc['kws_score'].min()
    dfc['kws_score_norm'] = dfc['kws_score']/dfc['kws_score'].max()

    dfc['alpha'] = 0.1 + (dfc['kws_score_norm'] - dfc['kws_score_norm'].min())/(dfc['kws_score_norm'].max() - dfc['kws_score_norm'].min())*0.5
    dfc['alpha'].fillna(0.1,inplace=True)

    return dfc
