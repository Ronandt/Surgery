from __init__ import db
from flask_login import UserMixin


class User(db.Model, UserMixin): #UserMixin for flask login #db model for sqlalchemy 
    id = db.Column(db.Integer, primary_key=True) #unique identifier that represnts the object
    username = db.Column(db.String(150), unique=True)
    email = db.Column(db.String(150), unique=True)
    gender = db.Column(db.String(10))
    password = db.Column(db.String(150))
    staff = db.Column(db.Integer)
    money = db.Column(db.Integer)
    #__mapper_args__ = {'polymorphic_identity' : 'user'}

'''class Staff(User):
    __mapper_args__ = {'polymorphic_identity' : 'staff'}
    id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key = True)
    hacks = db.Column(db.String(69))'''

#USE SHELVE PLEASE BECAUSE 5% FOR OOP
class Message:
    def __init__(self, id, description):
        self.__id = id
        self.__description = description
    def get_id(self):
        return self.__id
    def get_description(self):
        return self.__description
    def set_description(self, description):
        self.__description = description

class Notes(Message):
    def __init__(self, id, description, title, time_added, time_updated):
        super().__init__(id, description)
        self.__title = title
        self.__time_added = time_added
        self.__time_updated = time_updated
    def get_title(self):
        return self.__title
    def get_time_added(self):
        return self.__time_added
    def get_time_updated(self):
        return self.__time_updated
    def set_title(self, title):
        self.__title = title
    def set_time_added(self, time_added):
        self.__time_added = time_added
    def set_time_updated(self, time_updated):
        self.__time_updated = time_updated
    
