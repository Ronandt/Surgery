from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_required, current_user
from models import User, Notes, Message
from flask_socketio import send, emit
from __init__ import db, socketio
from Forms import EditUser, AddNotes, TicketForm, AddUser
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
    return render_template('staff-inventory.html')





@staff.route("/messages")
def messages():
    message_database = shelve.open('messages.db', 'c')
    message_dict = {}
    if 'message' in message_database:
        message_dict = message_database['message']
    else:
        message_database['message'] = message_dict
    print(message_dict)
    return render_template("staff-messages.html", message_dict = message_dict)

@socketio.on('message') #main event of messaging
def handleMessage(msg): #second step
    print("Message: " + msg)
    try:
        message_database = shelve.open('messages.db', 'c')
        message = Message(description = msg, sender = current_user.username)
        message_dict = {}
        if 'message' in message_database:
            message_dict = message_database['message']
      
        else:
            message_database['message'] = message_dict
    except:
        print("What the fuck went wrong")
    else:
        message_dict[message.get_id()] = message
        print(message_dict)
        message_database['message'] = message_dict
        message_database.close()

    send(msg, broadcast = True) #send message, broadcast is to send to everyone

@socketio.on('connect')
def handleConnect(auth):
    emit('responses', auth) #emit is for custom responses/events

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
            new_note = Notes(title = add_notes_form.title.data, description = add_notes_form.description.data, time_added = datetime.now().strftime("%d/%m/%y"), time_updated = datetime.now().strftime("%d/%m/%y"))
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
        current_note.set_title(request.form.get('title')) 
        current_note.set_description(request.form.get('description'))
        current_note.set_time_updated(datetime.now().strftime("%d/%m/%y"))
        notes_database[str(current_user.id)] = user_notes
        notes_database.close()
    

    return redirect(url_for("staff.notes"))



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
    reply_ticket_form = TicketForm(request.form)
    severity_dict = {"Low" : "success",
    "Medium" : "warning", "High" : "danger"}
    status_dict = {"Pending" : "dark",
    "Reviewed" : "secondary"}
    try:
        ticket_dict = {}
        ticket_database = shelve.open('ticket.db', 'c')
        if 'ticket' in ticket_database:
            ticket_dict = ticket_database['ticket']
        else:
            ticket_database['ticket'] = ticket_dict
        ticket_dict = dict(sorted(ticket_dict.items(), key=lambda x : x[1].get_status() == "Resolved" ))
    except ValueError:
        flash("Something unexpected has happened", category='error')
    ticket_database.close()

    
    return render_template("staff-ticket.html", ticket_dict = ticket_dict, severity_dict = severity_dict , status_dict = status_dict, reply_ticket_form = reply_ticket_form)



@staff.route("/sendTickets", methods=["GET", "POST"])
def sendTickets():
    if request.method == "POST":
        reply_ticket_form = TicketForm(request.form)
        try:
            ticket_dict = {}
            current_user_dict = {}
            ticket_database = shelve.open('ticket.db', 'c')
            if 'ticket' in ticket_database:
                ticket_dict = ticket_database['ticket']
            else:   
                ticket_database['ticket'] = ticket_dict
            if str(request.form.get('sender')) in ticket_database:
                current_user_dict = ticket_database[str(request.form.get('sender'))]
            else:
                ticket_database[str(request.form.get('sender'))] = current_user_dict

    
        except:
            flash("Something unexpected has occurred", category="error")
        else:
            direct_ticket = ticket_dict[request.form.get('uuid')]
            direct_ticket.set_reply_title(reply_ticket_form.title.data) 
            direct_ticket.set_reply_description(reply_ticket_form.description.data)
            direct_ticket.set_status("Resolved")
            direct_ticket.set_reply_time_sent()
            direct_ticket.set_replied_staff(current_user.username)
            current_user_dict[request.form.get('uuid')] = direct_ticket
            ticket_database['ticket'] = ticket_dict
            ticket_database[str(request.form.get('sender'))] = current_user_dict
            flash('Ticket has been sent!', category="success")
            ticket_database.close()
    return redirect(url_for("staff.tickets"))
    

@staff.route("/deleteTicket", methods=["GET", "POST"])
def deleteTicket():
    if request.method == "POST":
        ticket_dict = {}
        current_user_dict = {}
        try:
            ticket_database = shelve.open('ticket.db', 'c')
            if request.form.get('user') in ticket_database:
                current_user_dict = ticket_database[request.form.get('user')]
            else:
                ticket_database[request.form.get('user')] = current_user_dict
            if 'ticket' in ticket_database:
                ticket_dict = ticket_database['ticket']
            else:
                ticket_database['ticket'] = ticket_dict
    
        except:
            flash("Something unexpected has occurred", category='error')
        else:
            del ticket_dict[request.form.get('uuid')]
            current_user_dict[request.form.get('uuid')].set_status("Unresolved")
            ticket_database['ticket'] = ticket_dict
            ticket_database[request.form.get('user')] = current_user_dict


    return redirect(url_for('staff.tickets'))

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

@staff.route('/addUser/', methods=['GET', 'POST'])
def addUser():
    add_user_form = AddUser(request.form)
    if request.method == "POST":
        if User.query.filter_by(email = add_user_form.email.data).first():
            print(User.query.filter_by(email = add_user_form.email.data))
            flash("Email already exists", category='error')
        elif User.query.filter_by(username = add_user_form.username.data).first():
            flash("Username already exists", category='error')
        else:
            user = User(staff = add_user_form.permission.data, username = add_user_form.username.data, email = add_user_form.email.data, gender = add_user_form.gender.data, password = add_user_form.password.data, money = add_user_form.amount.data)
            db.session.add(user)
            db.session.commit()
            flash(f"Successfully added {user.username} <ID: {user.id}>")
        return redirect(url_for('staff.users'))
    return render_template('staff-add-users.html', add_user_form = add_user_form)
    