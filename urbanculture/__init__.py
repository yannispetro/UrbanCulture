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

import urbanculture.recommendations as recom

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

        p = recom.get_plot_handle(city,kws)

        script, div = components(p)
        return render_template("graph.html", script=script, div=div)
    return render_template('index.html', form=form)

if __name__ == '__main__':
    app.run(debug=True)
