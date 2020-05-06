import pandas as pd
from flask_wtf import FlaskForm
from wtforms import StringField, SelectField
from wtforms.fields.html5 import EmailField
from wtforms.validators import InputRequired, AnyOf

df_url = pd.read_csv('urbanculture/citydata/cities_names_urls.csv')
cities_alias = ['Select a city'] + list(df_url.city)
cities_names = ['Select a city'] + list(df_url.city_clean)
cities = list(zip(cities_alias,cities_names))
cities_dict = dict(cities)

class CityForm(FlaskForm):
    city_form     = SelectField('City',
                           validators=[AnyOf(cities_alias[1:])],
                           coerce=str,
                           choices=cities,
                           )
    keywords_form = StringField('Keywords',
                           validators=[InputRequired()],
                           render_kw={"placeholder": "Type a few keywords..."}
                           )

class EmailForm(FlaskForm):
    email_form = EmailField('Email',
                           render_kw={"placeholder": "Enter email address..."}
                           )
