from flask import Blueprint, render_template, redirect, url_for, request
from flask_login import login_required, current_user
from models import User
from __init__ import db

blueprint_utilities = Blueprint("blueprint_utilities", __name__)
user = current_user

'''routes = {"cards" : "utilities-cards.html", 
"buttons" : "utilities-buttons.html",
"animation" : "utilities-animation.html",
"border" : "utilities-border.html",
"color" : "utilities-color.html",
"other" : "utilities-other.html",
"charts" : "utilities-charts.html",
"home" : "utilities-index.html",
"login" : "utilities-login.html",
"register" : "utilities-register.html",
"forgot" : "utilities-forgot-password.html",
"err" : "utilities-404.html"} '''

@blueprint_utilities.before_request
def before_request():
    if not current_user.is_authenticated or user.staff == 0:
        return redirect(url_for('user_page.main_html'))

@login_required
@blueprint_utilities.route("/cards")
def cards():
    return render_template("utilities-cards.html")


@login_required
@blueprint_utilities.route("/buttons")
def buttons():
    return render_template("utilities-buttons.html")


@login_required  
@blueprint_utilities.route("/animation")    
def animation():
    return render_template("utilities-animation.html")


@login_required
@blueprint_utilities.route("/border")
def border():
    return render_template("utilities-border.html")

@login_required
@blueprint_utilities.route("/color")
def color():
    return render_template("utilities-color.html")

@login_required
@blueprint_utilities.route("/other")
def other():
    return render_template("utilities-other.html")
    
@login_required
@blueprint_utilities.route("/charts")
def charts():
    return render_template("utilities-charts.html")

@login_required
@blueprint_utilities.route("/tables")
def tables():
    users = User.query.all()
    return render_template("utilities-tables.html", users = users)

@login_required
@blueprint_utilities.route("/home")
def home_index():
    return render_template("utilities-index.html")

@login_required
@blueprint_utilities.route("/login")
def login_index():
    return render_template("utilities-login.html")

@login_required
@blueprint_utilities.route("/register")
def register_index():

    return render_template("utilities-register.html")

@login_required
@blueprint_utilities.route("/forgot")
def forgot_index():

    return render_template("utilities-forgot-password.html")

@login_required  
@blueprint_utilities.route("/err")

def err():
    return render_template("utilities-404.html")

@login_required
@blueprint_utilities.route("/blank")
def blank():
     return render_template("utilities-blank-base.html")
