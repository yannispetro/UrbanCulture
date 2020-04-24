from .extensions import db

class SearchQuery(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    city = db.Column(db.String(50))
    keywords = db.Column(db.String(300))
