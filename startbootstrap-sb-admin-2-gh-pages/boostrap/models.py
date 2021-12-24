from __init__ import db
from flask_login import UserMixin
from uuid import uuid4
from datetime import datetime

class User(db.Model, UserMixin): #UserMixin for flask login #db model for sqlalchemy 
    id = db.Column(db.Integer, primary_key=True) #unique identifier that represnts the object
    username = db.Column(db.String(150), unique=True)
    email = db.Column(db.String(150), unique=True)
    gender = db.Column(db.String(10))
    password = db.Column(db.String(150))
    staff = db.Column(db.Integer)
    money = db.Column(db.Integer)
    address = db.Column(db.String(100), default="None")
    disabled = db.Column(db.Boolean, default=False)

    #__mapper_args__ = {'polymorphic_identity' : 'user'}

'''class Staff(User):
    __mapper_args__ = {'polymorphic_identity' : 'staff'}
    id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key = True)
    hacks = db.Column(db.String(69))'''

#USE SHELVE PLEASE BECAUSE 5% FOR OOP
class BaseMessage:
    def __init__(self, description):
        self.__id = str(uuid4())
        self.__description = description
    def get_id(self):
        return self.__id
    def get_description(self):
        return self.__description
    def set_description(self, description):
        self.__description = description

class Message(BaseMessage):
    def __init__(self, description, sender):
        super().__init__(description)
        self.__sender = sender
    def get_sender(self):
        return self.__sender
    def set_sender(self, sender):
        self.__sender = sender
class Notes(BaseMessage):
    def __init__(self, description, title, time_added, time_updated):
        super().__init__(description)
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
    

class Ticket(BaseMessage):
    def __init__(self, description, title, issue, severity, sender_id, sender_username):
        super().__init__(description)
        self.__title = title
        self.__issue = issue
        self.__severity = severity
        self.__sender = sender_id
        self.__time_sent = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        self.__status = "Pending"
        self.__reply_title = ""
        self.__reply_description = ""
        self.__reply_time_sent = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        self.__sender_username =  sender_username
        self.__replied_staff = None
        
    def get_title(self):
       return self.__title

    def get_issue(self):
        return self.__issue

    def get_severity(self):
        return self.__severity 

    def get_sender_id(self):
        return self.__sender

    def get_time_sent(self):
        return self.__time_sent

    def get_sender_username(self):
        return self.__sender_username

    def get_reply_title(self):
        return self.__reply_title

    def get_reply_time_sent(self):
        return self.__reply_time_sent

    def get_reply_description(self):
        return self.__reply_description
    
    def get_replied_staff(self):
        return self.__replied_staff

    def get_status(self):
        return self.__status

    def set_title(self, title):
        self.__title = title

    def set_issue(self, issue):
        self.__issue = issue

    def set_severity(self, severity):
        self.__severity = severity

    def set_sender(self, sender):
        self.__sender = sender

    def set_status(self, status):
        self.__status = status

    def set_reply_title(self, reply_title):
        self.__reply_title = reply_title

    def set_reply_description(self, reply_description):
        self.__reply_description = reply_description
        
    def set_reply_time_sent(self):
        self.__reply_time_sent = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    
    def set_replied_staff(self, replied_staff):
        self.__replied_staff = replied_staff
        
#fill in status
class Feedback(BaseMessage):
    def __init__(self, description, rating, favourite, least_favourite, improvement, title, sender):
        super().__init__(description)
        self.__rating = rating
        self.__favourite = favourite
        self.__least_favourite = least_favourite
        self.__improvement = improvement
        self.__title = title
        self.__sender = sender
    def get_rating(self):
        return self.__rating
    def get_favourite(self):
        return self.__favourite
    def get_least_favourite(self):
        return self.__least_favourite
    def get_improvement(self):
        return self.__improvement
    def get_title(self):
        return self.__title
    def get_sender(self):
        return self.__sender
    def set_sender(self):
        return self.__sender
    def set_rating(self, rating):
        self.__rating = rating
    def set_favourite(self, favourite):
        self.__favourite = favourite
    def set_least_favourite(self, least_favourite):
        self.__least_favourite = least_favourite
    def set_improvement(self, improvement):
        self.__improvement = improvement
    def set_title(self, title):
        self.__title = title
    def set_sender(self, sender):
        self.__sender = sender

class Log(BaseMessage):
    def __init__(self, description,log_type, time_logged, title, action_done, user, logged_id):
        super().__init__(description)
        self.__log_type = log_type
        self.__time_logged = time_logged
        self.__title = title
        self.__action_done = action_done
        self.__user = user
        self.__logged_id = logged_id
    def get_log_type(self):
        return self.__log_type
    def get_time_logged(self):
        return self.__time_logged
    def get_title(self):
        return self.__title
    def get_action_done(self):
        return self.__action_done
    def get_user(self):
        return self.__user
    def get_logged_id(self):
        return self.__logged_id
    def set_log_type(self, log_type):
        self.__log_type = log_type
    def set_time_logged(self, time_logged):
        self.__time_logged = time_logged
    def set_title(self, title):
        self.__title = title
    def set_action_done(self, action_done):
        self.__action_done = action_done
    def set_user(self, user):
        self.__user = user
    def set_logged_id(self, logged_id):
        self.__logged_id = logged_id

class Product(BaseMessage):
    def __init__(self, description):
        super().__init__(description)