from flask import Blueprint, render_template
from bokeh.embed import components

from .extensions import db
from .models import SearchQuery
from .forms import CityForm, get_query_info
import urbanculture.recommendations as recom

main = Blueprint('main', __name__)

@main.route('/', methods= ['GET', 'POST'])
def index():
    form = CityForm()
    if form.validate_on_submit():

        date,ip_address,ip_city,ip_region,ip_country,city,keywords = get_query_info(form)

        print(get_query_info(form))

        searchquery = SearchQuery(date=date, ip_address=ip_address, city=city, keywords=keywords)
        db.session.add(searchquery)
        db.session.commit()

        p = recom.get_plot_handle(city, keywords.replace(',','').split() )

        script, div = components(p)
        return render_template("graph.html", script=script, div=div)
    return render_template('index.html', form=form)
