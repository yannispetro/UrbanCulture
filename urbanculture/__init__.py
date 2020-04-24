import pandas as pd

from flask import Flask, render_template
from flask_wtf import Form
from wtforms import StringField, SelectField
from wtforms.validators import InputRequired, Email, Length, AnyOf
from flask_bootstrap import Bootstrap

from joblib import load
from nltk.stem import PorterStemmer
from sklearn.metrics.pairwise import cosine_similarity
from bokeh.embed import components

import plotonmap
import recommendations as recom

app = Flask(__name__)
Bootstrap(app)
app.config['SECRET_KEY'] = 'PleaseDontTell'

df_url = pd.read_csv('data/allCitiesData.csv.gz', compression='gzip')
cities_alias = list(df_url.city)
cities_names = list(df_url.city_clean)
cities_alias = ['Select a city'] + cities_alias
cities_names = ['Select a city'] + cities_names
cities = list(zip(cities_alias,cities_names))

class CityForm(Form):
    city_form     = SelectField('City',
                           validators=[AnyOf(cities_alias[1:])],
                           coerce=str,
                           choices=cities,
                           )
    keywords_form = StringField(
                           'Keywords',
                           validators=[InputRequired()],
                           render_kw={"placeholder": "Type a few keywords ..."}
                           )

@app.route('/', methods= ['GET', 'POST'])
def index():
    form = CityForm()
    if form.validate_on_submit():
        city = form.city_form.data
        kws = form.keywords_form.data.replace(',','').split()

        dfc = pd.read_pickle('models/' + city + '_dfc.pkl.gz', compression='gzip')
        dfn = pd.read_pickle('models/' + city + '_dfn.pkl.gz', compression='gzip')
        dfc = recom.keywords_score(kws, dfc, city)
        p = plotonmap.plot_clusters(dfc, dfn, streets=True, colorScores = True)
        script, div = components(p)
        return render_template("graph.html", script=script, div=div)
    return render_template('index.html', form=form)

def keywords_score(kws, dfc, city):
    tfidf_airbnb  = load('models/' +  city + '_tfidf_airbnb.joblib')
    tfidf_reviews = load('models/' +  city + '_tfidf_reviews.joblib')
    kws = ' '.join(list(set([ps.stem(kw) for kw in kws])))

    kws_vec_airbnb = tfidf_airbnb.transform([kws])
    cs_airbnb = lambda x: cosine_similarity(x.vec_airbnb,kws_vec_airbnb)[0][0]
    dfc['kws_score_airbnb'] = dfc.apply(cs_airbnb, axis=1)
    dfc['kws_score_airbnb'] = dfc['kws_score_airbnb']/dfc['kws_score_airbnb'].sum()
    #
    kws_vec_reviews = tfidf_reviews.transform([kws])
    cs_reviews = lambda x: cosine_similarity(x.vec_reviews,kws_vec_reviews)[0][0]
    dfc['kws_score_reviews'] = dfc.apply(cs_reviews, axis=1)
    dfc['kws_score_reviews'] = dfc['kws_score_reviews']/dfc['kws_score_reviews'].sum()
    #
    dfc['kws_score'] = dfc['kws_score_airbnb'] + dfc['kws_score_reviews']
    dfc['kws_score'] = dfc['kws_score']/dfc['kws_score'].max()
    # dfc['kws_score'] = dfc['kws_score_airbnb']

    dfc['alpha'] = 0.01 + (dfc['kws_score'] - dfc['kws_score'].min())/(dfc['kws_score'].max() - dfc['kws_score'].min())*0.59

    return dfc

if __name__ == '__main__':
    app.run(debug=True)
