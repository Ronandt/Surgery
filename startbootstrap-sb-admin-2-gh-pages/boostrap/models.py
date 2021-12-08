from __init__ import db
from flask_login import UserMixin


class User(db.Model, UserMixin): #UserMixin for flask login #db model for sqlalchemy 
    id = db.Column(db.Integer, primary_key=True) #unique identifier that represnts the object
    username = db.Column(db.String(150), unique=True)
    email = db.Column(db.String(150), unique=True)
    gender = db.Column(db.String(10))
    password = db.Column(db.String(150))
    staff = db.Column(db.Integer)
