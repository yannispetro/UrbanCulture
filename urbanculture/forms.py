import os
import time

import pandas as pd
from flask import request
from flask_wtf import Form
from wtforms import StringField, SelectField
from wtforms.validators import InputRequired, AnyOf
import ipinfo

exclude = ['antwerp','asheville','barossa-valley','barwon-south-west-vic',
           'beijing','belize','bergamo','bristol','broward-county',
           'cambridge','clark-county-nv','columbus','denver','euskadi','ghent',
           'new-brunswick','northern-rivers','ottawa','pacific-grove','portland',
           'rhode-island','salem-or','tasmania','trentino','twin-cities-msa','vaud']

df_url = pd.read_csv('urbanculture/models/allCitiesData.csv.gz', compression='gzip')
df_url = df_url[~df_url.city.isin(exclude)]
cities_alias = ['Select a city'] + list(df_url.city)
cities_names = ['Select a city'] + list(df_url.city_clean)
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

def get_query_info(form):
    city = form.city_form.data
    keywords = form.keywords_form.data

    date = time.strftime('%Y-%m-%d %H:%M:%S')

    ip_address, ip_city, ip_region, ip_country = get_ip_info()

    return date, ip_address, ip_city, ip_region, ip_country, city, keywords


def get_ip_info():
    if request.environ.get('HTTP_X_FORWARDED_FOR', request.remote_addr) is None:
        ip_address = request.environ.get('HTTP_X_REAL_IP', request.remote_addr)
    else:
        ip_address = request.environ.get('HTTP_X_FORWARDED_FOR', request.remote_addr)

    access_token = os.environ['IPINFO_TOKEN']
    details = ipinfo.getHandler(access_token).getDetails(ip_address)

    if hasattr(details, 'city'):
        ip_city = details.city
    else:
        ip_city = '-'
    if hasattr(details, 'region'):
        ip_region = details.region
    else:
        ip_region = '-'
    if hasattr(details, 'country'):
        ip_country = details.country
    else:
        ip_country = '-'

    return ip_address, ip_city,ip_region,ip_country
