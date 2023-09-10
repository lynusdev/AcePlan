from . import db
from flask_login import UserMixin

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, unique=True)
    password = db.Column(db.String)
    passwordlength = db.Column(db.Integer)
    klasse = db.Column(db.String)
    kurse = db.Column(db.String)