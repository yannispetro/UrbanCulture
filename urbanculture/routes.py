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
        query_info_dict = get_query_info(form)
        searchquery = SearchQuery(date=query_info_dict['date'],
                                  ip_address=query_info_dict['ip_address'],
                                  ip_city=query_info_dict['ip_city'],
                                  ip_region=query_info_dict['ip_region'],
                                  ip_country=query_info_dict['ip_country'],
                                  city=query_info_dict['city'],
                                  keywords=query_info_dict['keywords'])
        db.session.add(searchquery)
        db.session.commit()

        city     = query_info_dict['city']
        keywords = query_info_dict['keywords']
        p = recom.get_plot_handle(city, keywords.replace(',','').split() )

        script, div = components(p)
        return render_template("graph.html", script=script, div=div)
    return render_template('index.html', form=form)
