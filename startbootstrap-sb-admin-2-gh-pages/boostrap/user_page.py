from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login.utils import login_required
from Forms import AddFundsForm, TicketForm, FeedbackForm, UpdateUserForm
from models import Ticket
from __init__ import db
from werkzeug.security import generate_password_hash,  check_password_hash, gen_salt #trying to salt it later
from flask_login import login_user, login_required, logout_user, current_user
from datetime import datetime
import shelve


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
 
@user_page.route("/editAccount")
def editAccount():
    update_account_form = UpdateUserForm(request.form)
    update_account_form.username.data = current_user.username
    update_account_form.email.data = current_user.email
    update_account_form.gender.data = current_user.gender
    update_account_form.password.data = current_user.password
    return render_template("page-edit-account.html", update_account_form = update_account_form)

@user_page.route("/feedback")
def feedback():
    feedback_form = FeedbackForm(request.form)
    if request.method == "POST":
        pass
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
    except:
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
        
