from .extensions import db

class IPAddress(db.Model):
    id         = db.Column(db.Integer, primary_key=True)
    date       = db.Column(db.String(20))
    ip_address = db.Column(db.String(20))
    ip_city    = db.Column(db.String(30))
    ip_region  = db.Column(db.String(30))
    ip_country = db.Column(db.String(10))

class SearchQuery(db.Model):
    id         = db.Column(db.Integer, primary_key=True)
    date       = db.Column(db.String(20))
    ip_address = db.Column(db.String(20))
    city       = db.Column(db.String(50))
    keywords   = db.Column(db.Text)

class EmailAddress(db.Model):
    id         = db.Column(db.Integer, primary_key=True)
    date       = db.Column(db.String(20))
    ip_address = db.Column(db.String(20))
    email      = db.Column(db.String(30))
