from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login.utils import login_required
from Forms import RegisterForm, LoginForm, AddFundsForm
from models import User
from __init__ import db
from werkzeug.security import generate_password_hash,  check_password_hash, gen_salt #trying to salt it later
from flask_login import login_user, login_required, logout_user, current_user



user_page = Blueprint("user_page", __name__)

@login_required
@user_page.before_request
def before_request():
    pass

@user_page.route("/home")
@user_page.route("/")

def main_html():
    return render_template("page-index-3.html")


@user_page.route("/products")
def products():
    return render_template("page-listing-grid.html")

@user_page.route("/cart")
def cart():
    return render_template("page-shopping-cart.html")



@user_page.route("/account")
def account():
    return render_template("page-profile-main.html")


@user_page.route("/feedback")
def feedback():
    return render_template("page-reports.html")
    
@user_page.route("/funds", methods=["GET", "POST"])
def funds():
    funds_form = AddFundsForm(request.form)
    if request.method == "POST" and funds_form.validate_on_submit():
        if check_password_hash(current_user.password, funds_form.password.data):
            current_user.money += funds_form.amount.data 
            db.session.commit()
            flash(f"${funds_form.amount.data} added!", category="success")
        else:
            flash("Wrong login credentials!", category="error")
    return render_template("page-funds.html", funds_form = funds_form)


@user_page.route("/chatbot")
def chatbot():
    return render_template("page-customer-service.html")


@user_page.route("/about_us")
def about_us():
   
    return render_template("page-content.html")


@user_page.route('/logout')
def logout():
    logout_user()
    return redirect(url_for("login_register.user_login"))
        
