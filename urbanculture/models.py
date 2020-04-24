from .extensions import db

class SearchQuery(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.String(20))
    ip_address = db.Column(db.String(20))
    city = db.Column(db.String(50))
    keywords = db.Column(db.String(300))
