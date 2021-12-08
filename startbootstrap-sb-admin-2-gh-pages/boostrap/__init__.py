from flask import *
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

from os import path
from werkzeug.security import generate_password_hash


app = Flask(__name__)
db = SQLAlchemy()
DB_NAME = "user.db"
#database intialisation 
def create_app():
    from user_page import user_page
    from utilities import blueprint_utilities
    from models import User

    app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{DB_NAME}"
    app.config['SECRET_KEY'] = "FDHIfdsfi414fhuf"
    db.init_app(app)
    create_database(app)
    #register blueprint
    app.register_blueprint(blueprint_utilities, url_prefix="/utilities")
    app.register_blueprint(user_page, url_prefix="/")

    with app.app_context(): #SQLAlchemy does not allow this code to run in a non-app context, hence, you have to create an environment (a function) to do so
        staff = [User(staff = 1, username = "Candice", email="staff@gmail.com", gender="F",  password = generate_password_hash("bruhhh", method="sha256"))]
        for x in staff:
            if not User.query.filter_by(id = x.id).first() and not User.query.filter_by(email = x.email).first() and not User.query.filter_by(username = x.username).first():
                print("Staff Added!")
                db.session.add(x)
                db.session.commit()
    #login initalisation
    login_manager = LoginManager()
    login_manager.init_app(app)
    @login_manager.user_loader #loads the logged in user
    def load_user(id):
        return User.query.get(int(id)) #looks for the id (specific column) of the user
    login_manager.login_view = 'user_page.user_login' #default page if the user is not logged in

    return app

@app.route("/staff")
def staff_html():
    return render_template("utilities-blank-base.html")

@app.errorhandler(404) #404
def page_not_found(e):
    return render_template("utilities-404.html"), 404



def create_database(app):
    if not path.exists('boostrap/' + DB_NAME):
        db.create_all(app=app)
        print("Database created")


