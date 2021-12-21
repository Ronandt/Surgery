from flask import Blueprint
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login.utils import login_required
from Forms import RegisterForm, LoginForm, AddFundsForm
from models import User
from __init__ import db
from werkzeug.security import generate_password_hash,  check_password_hash, gen_salt #trying to salt it later
from flask_login import login_user, login_required, logout_user, current_user
#this will be for slogin in and register 
login_register = Blueprint('login_register', __name__)


    
@login_register.route("/login", methods=["GET", 'POST'])
def user_login():
    login_user_form = LoginForm(request.form)
    if request.method == "POST" and login_user_form.validate():
        user = User.query.filter_by(username = login_user_form.username.data).first()
        if user and check_password_hash(user.password, login_user_form.password.data):
            flash("Login Successful! Welcome!", category = "success")
            login_user(user, remember=True)
            if user.staff == 0:
                return redirect(url_for('user_page.main_html'))
            elif user.staff == 1:
                return redirect(url_for('blueprint_utilities.home_index'))
            else:
                return "how"
        else:
            flash("Wrong credentials!", category = 'error')
    return render_template("page-user-login.html", login_user_form = login_user_form)

@login_register.route("/register", methods=['GET', 'POST'])
def user_register():
    register_user_form = RegisterForm(request.form)
    if request.method == "POST" and register_user_form.validate():
        check_email = User.query.filter_by(email = register_user_form.email.data).first()
        check_username = User.query.filter_by(username = register_user_form.username.data).first()
        print(check_email)
    
        if check_email:
            flash('Email already exists', category='error')
        elif check_username:
            flash ('Username already exists', category = 'error')
        elif register_user_form.password.data != register_user_form.repeat_password.data:
            flash("Password must be equal to the confirmation", category= 'error')
        else:
            new_user = User(staff = 0, money = 0, username = register_user_form.username.data, gender = register_user_form.gender.data, email = register_user_form.email.data, password = generate_password_hash(register_user_form.password.data, method="sha256"))
            db.session.add(new_user)
            db.session.commit()
            flash('Account created!', category='success')
            
            return redirect(url_for('login_register.user_login'))
    return render_template("page-user-register.html", register_user_form = register_user_form)