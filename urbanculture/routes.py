from flask import Blueprint, render_template
from bokeh.embed import components

from .extensions import db
from .forms import CityForm, EmailForm
from .formdata import get_ip_info, get_query, get_email
import urbanculture.recommendations as recom

main = Blueprint('main', __name__)

@main.route('/', methods= ['GET', 'POST'])
def index():
    form = CityForm()
    emailform = EmailForm()

    ip_info = get_ip_info()
    db.session.add(ip_info)
    db.session.commit()
    ip_address = ip_info.ip_address

    if form.validate_on_submit():
        searchquery = get_query(form, ip_address)
        db.session.add(searchquery)
        db.session.commit()

        city     = query_info_dict['city']
        keywords = query_info_dict['keywords'].lower().split(',')
        p = recom.get_plot_handle(city, keywords )

        script, div = components(p)
        return render_template('graph.html', script=script, div=div)
    if emailform.validate_on_submit():
        emailaddress = get_email(emailform, ip_address)
        db.session.add(emailaddress)
        db.session.commit()

    return render_template('index.html', form=form, emailform=emailform)

@main.route('/about')
def about():
    return render_template('about.html')
