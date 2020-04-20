import os
import pandas as pd
import requests
from bs4 import BeautifulSoup

url = 'http://insideairbnb.com/get-the-data.html'
res = requests.get(url)
html_page = res.content

soup = BeautifulSoup(html_page, 'html.parser')
text = soup.find_all(text=True)

df0 = pd.DataFrame(columns = ['city','country','date','url'])
for i, a in enumerate(soup.find_all('a', href=True, text = 'listings.csv.gz')):
    urlComps = a['href'].split('/')
    df0.loc[i] = [urlComps[-4],urlComps[-6],urlComps[-3],a['href']]
df0['date'] = pd.to_datetime(df0['date'])

df_url = df0[df0.groupby(['city','country'])['date'].transform(max) == df0['date']]

city = 'crete'
url = df_url[df_url['city']==city]['url'].values[0]

df_city = pd.read_csv(url,compression='gzip')

df_city[['latitude','longitude']].isna().any()

lats = list(df_city.latitude)
lngs = list(df_city.longitude)

from bokeh.io import output_file, show
from bokeh.models import ColumnDataSource, GMapOptions
from bokeh.plotting import gmap, figure

output_file("gmap.html")

heraklion = (35.334427,25.137239)
map_options = GMapOptions(lat = df_city['latitude'].mean(),
                          lng = df_city['longitude'].mean(),
                          map_type="roadmap", zoom=13)

# # My Google API key from environment variables in ~/.bash_profile
# api_key = os.environ['GOOGLE_API_KEY']
# p = gmap(api_key, map_options, title="Crete")

p = figure(plot_width=1000, plot_height=650,
           title='COVID-19 Daily',
           background_fill_color="#fafafa")

source = ColumnDataSource( data=dict(lat=lats,lon=lngs) )

p.circle(x="lon", y="lat", size=5, fill_color="blue", fill_alpha=0.5, source=source)


show(p)
