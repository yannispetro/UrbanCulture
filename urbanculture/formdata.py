import os
import time

from flask import request
import ipinfo

from .models import IPAddress, SearchQuery, EmailAddress

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

    ip_info = IPAddress(
                        date=time.strftime('%Y-%m-%d %H:%M:%S'),
                        ip_address=ip_address,
                        ip_city=ip_city,
                        ip_region=ip_region,
                        ip_country=ip_country
                        )
    return ip_info

def get_query(form, ip_address):
    searchquery = SearchQuery(
                              date=time.strftime('%Y-%m-%d %H:%M:%S'),
                              ip_address=ip_address,
                              city=form.city_form.data,
                              keywords=form.keywords_form.data
                              )
    return searchquery

def get_email(form, ip_address):
    emailaddress = EmailAddress(
                                date=time.strftime('%Y-%m-%d %H:%M:%S'),
                                ip_address=ip_address,
                                email=form.email_form.data
                                )
    return emailaddress
