def cityDF(self,city):
    url = self.df_url[self.df_url['city']==city]['url'].values[0]
    self.df_city = pd.read_csv(url,compression='gzip')
    return self.df_city

if __name__ == "__main__":
    url = 'http://insideairbnb.com/get-the-data.html'
    res = requests.get(url)
    html_page = res.content

    soup = BeautifulSoup(html_page, 'html.parser')

    df0 = pd.DataFrame(columns = ['city','country','date','url'])
    for i, a in enumerate(soup.find_all('a', href=True, text = 'listings.csv.gz')):
        urlComps = a['href'].split('/')
        df0.loc[i] = [urlComps[-4],urlComps[-6],urlComps[-3],a['href']]

    df0['date'] = pd.to_datetime(df0['date'])
    self.df_url = df0[df0.groupby(['city','country'])['date'].transform(max) == df0['date']]
