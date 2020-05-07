from flask import Blueprint, render_template, redirect, url_for, request, session
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

    if 'ip_address' not in session:
        ip_info = get_ip_info()
        db.session.add(ip_info)
        db.session.commit()
        session['ip_address'] = ip_info.ip_address
    elif request.environ.get('HTTP_X_FORWARDED_FOR', request.remote_addr) != session['ip_address']:
        ip_info = get_ip_info()
        db.session.add(ip_info)
        db.session.commit()
        session['ip_address'] = ip_info.ip_address
    ip_address = session['ip_address']

    if form.validate_on_submit():
        searchquery = get_query(form, ip_address)
        db.session.add(searchquery)
        db.session.commit()

        city     = searchquery.city
        keywords = searchquery.keywords
        p = recom.get_plot_handle(city, keywords.lower().split(',') )

        script, div = components(p)
        return render_template('index.html',
                               form=form,
                               emailform=emailform,
                               script=script,
                               div=div,
                               set_tab=1,
                               **{'map_title':f'{cities_dict[city]}: {keywords}'})

    if emailform.validate_on_submit():
        emailaddress = get_email(emailform, ip_address)
        db.session.add(emailaddress)
        db.session.commit()
        emailform.email_form.data = ""
        return redirect(url_for('main.index', set_tab=0, _anchor='signup'))

    return render_template('index.html', form=form, emailform=emailform)
