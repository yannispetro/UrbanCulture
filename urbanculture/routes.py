import time
import pandas as pd

from flask import Blueprint, render_template, request
from flask_wtf import Form
from wtforms import StringField, SelectField
from wtforms.validators import InputRequired, AnyOf
from bokeh.embed import components

from .extensions import db
from .models import SearchQuery
import urbanculture.recommendations as recom

main = Blueprint('main', __name__)

exclude = ['antwerp','asheville','barossa-valley','barwon-south-west-vic',
           'beijing','belize','bergamo','bristol','broward-county',
           'cambridge','clark-county-nv','columbus','denver','euskadi','ghent',
           'new-brunswick','northern-rivers','ottawa','pacific-grove','portland',
           'rhode-island','salem-or','tasmania','trentino','twin-cities-msa','vaud']

df_url = pd.read_csv('data/allCitiesData.csv.gz', compression='gzip')
df_url = df_url[~df_url.city.isin(exclude)]
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

@main.route('/', methods= ['GET', 'POST'])
def index():
    form = CityForm()
    if form.validate_on_submit():
        date = time.strftime('%Y-%m-%d %H:%M:%S')
        ip_address = request.environ.get('HTTP_X_REAL_IP', request.remote_addr)
        city = form.city_form.data
        keywords = form.keywords_form.data

        searchquery = SearchQuery(date=date, ip_address=ip_address, city=city, keywords=keywords)
        db.session.add(searchquery)
        db.session.commit()

        p = recom.get_plot_handle(city, keywords.replace(',','').split() )

        script, div = components(p)
        return render_template("graph.html", script=script, div=div)
    return render_template('index.html', form=form)
