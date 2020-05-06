from flask import Blueprint, render_template, redirect, url_for
from bokeh.embed import components

from .extensions import db
from .forms import CityForm, EmailForm, cities_dict
from .formdata import get_ip_info, get_query, get_email
import urbanculture.recommendations as recom

main = Blueprint('main', __name__)

@main.route('/', methods= ['GET', 'POST'])
def index():
    form = CityForm()
    emailform = EmailForm()

    if form.validate_on_submit():
        ip_info = get_ip_info()
        db.session.add(ip_info)
        db.session.commit()
        ip_address = ip_info.ip_address

        searchquery = get_query(form, ip_address)
        db.session.add(searchquery)
        db.session.commit()

        city     = searchquery.city
        keywords = searchquery.keywords
        p = recom.get_plot_handle(city, keywords.lower().split(',') )

        script, div = components(p)
        return render_template('index.html', script=script, div=div, form=form, emailform=emailform, set_tab=1, **{'map_title':f'{cities_dict[city]}: {keywords}'})

        # return redirect(url_for('main.index', script=script, div=div, **{'map_title':f'{cities_dict[city]}: {keywords}'}))
        # return render_template('graph.html', script=script, div=div)

    if emailform.validate_on_submit():
        emailaddress = get_email(emailform, ip_address)
        db.session.add(emailaddress)
        db.session.commit()
        emailform.email_form.data = ""
        return redirect(url_for('main.index', _anchor='signup'))

    return render_template('index.html', form=form, emailform=emailform)
