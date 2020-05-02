import os
import time

import pandas as pd
from flask import request
from flask_wtf import Form
from wtforms import StringField, SelectField
from wtforms.validators import InputRequired, AnyOf
import ipinfo

df_url = pd.read_csv('urbanculture/citydata/cities_names_urls.csv')
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
    query_info_dict = {'city': form.city_form.data,
                       'keywords': form.keywords_form.data,
                       'date': time.strftime('%Y-%m-%d %H:%M:%S')}

    query_info_dict.update(get_ip_info())

    return query_info_dict


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

    ip_info_dict = {'ip_address': ip_address,
                    'ip_city': ip_city,
                    'ip_region': ip_region,
                    'ip_country': ip_country}

    return ip_info_dict
