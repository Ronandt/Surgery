from flask import *
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_socketio import SocketIO
from random import randint

from werkzeug.security import generate_password_hash


app = Flask(__name__, static_url_path="/static")
db = SQLAlchemy()
DB_NAME = "user.db"
socketio = SocketIO(app)

#database intialisation 
def create_app():
    from user_register_login import login_register
    from user_page import user_page
    from utilities import blueprint_utilities
    from models import User
    from staff import staff
    #from models import Staff
    
    app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{DB_NAME}"
    app.config['SECRET_KEY'] = "FDHIfdsfi414fhuf"
  
    db.init_app(app)

    #register blueprint
    app.register_blueprint(blueprint_utilities, url_prefix="/utilities")
    app.register_blueprint(user_page, url_prefix="/")
    app.register_blueprint(staff, url_prefix="/staff")
    app.register_blueprint(login_register, url_prefix = "/")

    with app.app_context():
        db.create_all() #SQLAlchemy does not allow this code to run in a non-app context, hence, you have to create an environment (a function) to do so
        staff = [User(staff = 1, username = "Candice", email="staff@gmail.com", gender="F", money = 10000000000, password = generate_password_hash("bruhhh", method="sha256"), address = "None"), User(staff = 0, username = "Cock", email="cock@gmail.com", gender="F", money = 0,  password = generate_password_hash("bruhhh", method="sha256"), address = "None")]
        for x in staff:
            if not User.query.filter_by(id = x.id).first() and not User.query.filter_by(email = x.email).first() and not User.query.filter_by(username = x.username).first():
               
                print("Staff Added!")
                db.session.add(x)
                db.session.commit()
        #db.session.add(Staff(hacks = str(randint(1, 100000)), staff = 1, username = str(randint(1, 1000000)), email=str(randint(1, 1000000)), gender = str(randint(1, 1000000)), money = randint(1, 1000000), password = str(randint(1, 1000000))))
        #db.session.commit()
    #login initalisation

    login_manager = LoginManager()
    login_manager.init_app(app)
    @login_manager.user_loader #loads the logged in user
    def load_user(id):
        return User.query.get(int(id)) #looks for the id (specific column) of the user
    login_manager.login_view = 'login_register.user_login' #default page if the user is not logged in

    return app

@app.route("/staff")
def staff_html():
    return render_template("utilities-blank-base.html")

@app.errorhandler(404) #404
def page_not_found(e):
    return render_template("utilities-404.html"), 404


