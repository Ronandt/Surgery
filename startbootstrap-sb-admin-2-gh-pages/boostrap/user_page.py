from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login.utils import login_required
from Forms import AddFundsForm, TicketForm, FeedbackForm, UpdateUserForm
from models import Ticket, Feedback, User
from __init__ import db
from werkzeug.security import generate_password_hash,  check_password_hash, gen_salt #trying to salt it later
from flask_login import login_user, login_required, logout_user, current_user
from datetime import datetime
import shelve


user_page = Blueprint("user_page", __name__)


@user_page.before_request
def before_request():
    if not current_user.is_authenticated:
        return redirect(url_for("login_register.user_login"))
    elif current_user.disabled:
        logout_user()




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

    gender_dict = {"F" : "Female",
    "M" : "Male" }
    return render_template("page-profile-main.html", gender_dict = gender_dict)
 
@user_page.route("/editAccount", methods=["GET", "POST"])
def editAccount():
    update_account_form = UpdateUserForm(request.form)
    gender_dict = {"F" : "Female",
    "M" : "Male" }

    if request.method == "POST":
        if User.query.filter_by(username = update_account_form.username.data).first() and update_account_form.username.data != current_user.username:
            flash("This username is not unique!", category="error")
        elif User.query.filter_by(email = update_account_form.email.data).first() and update_account_form.email.data != current_user.email:
            flash("This email is not unique!", category="error")
        elif (update_account_form.repeat_password.data != update_account_form.password.data) and not check_password_hash(current_user.password, update_account_form.password.data):
            flash("Your repeat password or your password is incorrect. Try again.", category="error")
        else:
            current_user.username = update_account_form.username.data
            current_user.email = update_account_form.email.data
            current_user.gender = update_account_form.gender.data
            current_user.password = generate_password_hash(update_account_form.password.data)
            current_user.address = update_account_form.address.data
            db.session.commit()
            flash("Updating of profile is successful!", category="success")
            return redirect(url_for('user_page.account'))
   
    update_account_form.username.data = current_user.username
    update_account_form.email.data = current_user.email
    update_account_form.gender.data = current_user.gender
    update_account_form.password.data = current_user.password
    update_account_form.address.data = current_user.address

    return render_template("page-edit-account.html", update_account_form = update_account_form, gender_dict = gender_dict)

@user_page.route("/disableAccount", methods=["GET", "POST"])
def disableAccount():
    if request.method == "POST":
        disable = request.form.get('id')
        User.query.filter_by(id = disable).first().disabled = True
        db.session.commit()
        logout_user(disable)
    return redirect(url_for("user_page.main_html"))


@user_page.route("/deleteAccount", methods=["GET", "POST"])
def deleteAccount():
    if request.method=="POST":
        delete = request.form.get('id')
        User.query.filter_by(id = delete).delete()
        db.session.commit()
        return redirect(url_for("login_register.user_register"))
    flash("If you want to delete your account, do it properly!", category='error')
    return redirect(url_for("user_page.main_html"))

@user_page.route("/feedback", methods=["GET", "POST"])
def feedback():
    feedback_form = FeedbackForm(request.form)
    if request.method == "POST":
        try:
            feedback_dict = {}
            feedback_database = shelve.open('feedback.db', 'c')
            if 'feedback' in feedback_database:
                feedback_dict = feedback_database['feedback']
            else:
                feedback_database['feedback'] = feedback_dict
        except Exception as e:
            flash(f"Something unexpected has occurred {e}", category='error')
        else:
            feedback = Feedback(description = feedback_form.remarks.data, rating = int(request.form.get('rate')), favourite = feedback_form.favourite.data, least_favourite = feedback_form.least_favourite.data, improvement = feedback_form.improvement.data, title = feedback_form.title.data, sender = current_user.username)
            feedback_dict[feedback.get_id()] = feedback
            feedback_database['feedback'] = feedback_dict
            flash("Sent a feedback!", category="success")
        feedback_database.close()
        return redirect(url_for('user_page.feedback'))
    return render_template("page-feedback.html", feedback_form = feedback_form)

@user_page.route("/tickets", methods=["GET", "POST"])
def tickets():
    status_dict = {"Pending" : "warning",
    "Resolved" : "success",
    "Unresolved" : "secondary"}
    ticket_form = TicketForm(request.form)
    try:
        ticket_dict = {}
        current_user_dict = {}
          
        ticket_database = shelve.open('ticket.db', 'c')
        if 'ticket' in ticket_database:
            ticket_dict = ticket_database['ticket']
        else:
            ticket_database['ticket'] = ticket_dict
        if str(current_user.id) in ticket_database:
            current_user_dict = ticket_database[str(current_user.id)]
        else:
            ticket_database[str(current_user.id)] = current_user_dict
    except ValueError:
        flash("An unknown error has occurred", category='error')
    if request.method == "POST":
     
            ticket = Ticket(ticket_form.description.data, ticket_form.title.data, ticket_form.issue.data, ticket_form.severity.data, current_user.id ,  current_user.username)
            ticket_dict[ticket.get_id()] = ticket
            current_user_dict[ticket.get_id()] = ticket
            ticket_database['ticket'] = ticket_dict
            ticket_database[str(current_user.id)] = current_user_dict
            flash("Ticket has been sent!", category="success")
            return redirect(url_for('user_page.tickets'))
    current_user_dict =  ticket_dict = dict(sorted(current_user_dict.items(), key=lambda x : x[1].get_reply_time_sent(), reverse=True))
    ticket_database.close()
    print(current_user_dict)
    return render_template("page-reports.html", ticket_form = ticket_form, status_dict = status_dict, current_user_dict = current_user_dict)
    
@user_page.route("/funds", methods=["GET", "POST"])
def funds():
    funds_form = AddFundsForm(request.form)
    if request.method == "POST":
        if check_password_hash(current_user.password, funds_form.password.data):
            current_user.money += funds_form.amount.data 
            db.session.commit()
            flash(f"${funds_form.amount.data} added!", category="success")
        else:
            flash("Wrong login credentials!", category="error")
    return render_template("page-funds.html", funds_form = funds_form)



@user_page.route("/about_us")
def about_us():
   
    return render_template("page-content.html")


@user_page.route('/logout')
def logout():
    logout_user()
    return redirect(url_for("login_register.user_login"))
        
