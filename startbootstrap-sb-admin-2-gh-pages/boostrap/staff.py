from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_required, current_user
from models import User, Notes
from __init__ import db
from Forms import EditUser, AddNotes
from uuid import uuid4
import shelve
from datetime import datetime
from werkzeug.security import generate_password_hash

user = current_user
staff = Blueprint('staff', __name__)


@login_required
@staff.before_request
def before_request():
    if not current_user.is_authenticated or user.staff == 0:
        return redirect(url_for("user_page.main_html"))

@staff.route("/feedback")
def feedback():
    return render_template("staff-feedback.html")
    

@staff.route("/home")
def home():
    return render_template("utilities-index.html")

@staff.route("/inventory")
def inventory():
    return render_template("staff-inventory-management.html")


@staff.route("/messages")
def messages():
    return render_template("staff-messages.html")


@staff.route("/notes", methods=["GET", "POST"])
def notes():
    add_notes_form = AddNotes(request.form)
    notes_database = shelve.open('notes.db', 'c')
    user_notes = {}
    try:
        if str(current_user.id) not in notes_database:
            notes_database[str(current_user.id)] = user_notes
        else:
            user_notes = notes_database[str(current_user.id)]
    except:
        flash("An unknown error has occurred", category="error")
    else:
        if request.method == "POST":
            new_note = Notes(id = str(uuid4()), title = add_notes_form.title.data, description = add_notes_form.description.data, time_added = datetime.now().strftime("%d/%m/%y"), time_updated = datetime.now().strftime("%d/%m/%y"))
            user_notes[new_note.get_id()] = new_note
            print(user_notes)
            notes_database[str(current_user.id)] = user_notes
            notes_database.close()
            return redirect(url_for("staff.notes"))
    return render_template("staff-notes.html", add_notes_form = add_notes_form, user_notes = user_notes)

@staff.route("/deleteNotes", methods=["GET", "POST"])
def deleteNotes():
    if request.method == "POST":
        notes_database = shelve.open('notes.db', 'w')
        user_notes = {}
        try:
            if str(current_user.id) not in notes_database:
                notes_database[str(current_user.id)] = user_notes
            else:
                user_notes = notes_database[str(current_user.id)]
        except KeyError:
            flash("No such note.", category="error")
        else:
            print(user_notes)
            print(request.form.get('uuid'))
            del user_notes[str(request.form.get('uuid'))]
            notes_database[str(current_user.id)] = user_notes
            notes_database.close()        
    return redirect(url_for("staff.notes"))

@staff.route("/updateNotes", methods=["GET", "POST"])
def updateNotes():
    update_notes_form = AddNotes(request.form)
    if request.method == "POST":
        notes_database = shelve.open('notes.db', 'w')
        user_notes = {}
        try:
            if str(current_user.id) not in notes_database:
                notes_database[str(current_user.id)] = user_notes
            else:
                user_notes = notes_database[str(current_user.id)]
        except KeyError:
            flash("No such note.", category="error")
        current_note = user_notes[request.form.get('uuid')]
        current_note.set_title(update_notes_form.title.data) 
        current_note.set_description(update_notes_form.description.data)
        notes_database[str(current_user.id)] = user_notes

@staff.route("/sales")
def sales():
    return render_template("staff-sales-log.html")


@staff.route("/users")
def users():
    users = User.query.all()
    return render_template("staff-user-management.html", users = users)   


@staff.route("/logs")
def logs():
    return render_template("staff-website-log.html")


@staff.route("/tickets")
def tickets():
    return render_template("staff-ticket.html")


@staff.route("/deleteUser", methods=["GET", "POST"])
def deleteUser():
     if request.method == "POST":
          deletes = request.form.get("id")
          User.query.filter_by(id = deletes).delete()
          db.session.commit()
          print("User Deleted")
     return redirect(url_for("staff.users"))



@staff.route("/updateUser/<int:id>", methods=["GET", "POST"])
def updateUser(id):
    update_user_form = EditUser(request.form)
    user = User.query.filter_by(id = id).first()
    if request.method == "POST":
        user.money = update_user_form.amount.data
        if User.query.filter_by(email = update_user_form.email.data).first() and User.query.filter_by(email = update_user_form.email.data).first().id != user.id:
            flash("The email is not unique!", category= "error")
        elif User.query.filter_by(username = update_user_form.username.data).first() and User.query.filter_by(username = update_user_form.username.data).first().id != user.id:
            flash("The username is not unique!", category= "error")
        else:
            user.username = update_user_form.username.data
            user.email = update_user_form.email.data
            user.gender = update_user_form.gender.data
            user.password = generate_password_hash(update_user_form.password.data)
            user.staff = update_user_form.permission.data
            flash(f"{user.username} <ID: {user.id}> has been updated.")
            db.session.commit()
            return redirect(url_for('staff.users'))
    update_user_form.amount.data = user.money
    update_user_form.email.data = user.email
    update_user_form.username.data = user.username
    update_user_form.gender.data = user.gender
    update_user_form.password.data= user.password
    update_user_form.permission.data = user.staff
    
    return render_template("staff-update-user.html", update_user_form = update_user_form, user = user)