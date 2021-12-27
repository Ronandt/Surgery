from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_required, current_user, logout_user
from models import User, Notes, Message, Supplier, Mail
from flask_socketio import send, emit
from __init__ import db, socketio
from Forms import EditUser, AddNotes, TicketForm, AddUser, AddProductForm, EmailForm,  AddSuppliersForm
from uuid import uuid4
import shelve
from datetime import datetime
from werkzeug.security import generate_password_hash


user = current_user
staff = Blueprint('staff', __name__)


@staff.before_request
def before_request():
    if current_user.is_authenticated:
        if user.staff == 0:
            return redirect(url_for("user_page.main_html"))
        elif user.disabled:
            logout_user()
    else:
        return redirect(url_for("login_register.user_login"))


@staff.route("/feedback")
def feedback():
    try:
        feedback_dict = {}
        feedback_database = shelve.open('feedback.db', 'c')
        if 'feedback' in feedback_database:
            feedback_dict = feedback_database['feedback']
        else:
            feedback_database['feedback'] = feedback_dict
    except:
        flash("Something unexpected has occurred", category="error")
    feedback_database.close()
    return render_template("staff-feedback.html", feedback_dict=feedback_dict)


@staff.route("/deleteFeedback", methods=["GET", "POST"])
def deleteFeedback():
    if request.method == "POST":
        try:
            feedback_dict = {}
            feedback_database = shelve.open('feedback.db', 'c')
            if 'feedback' in feedback_database:
                feedback_dict = feedback_database['feedback']
            else:
                feedback_database['feedback'] = feedback_dict
        except:
            flash("Something unexpected has occurred", category='error')
        else:
            del feedback_dict[request.form.get('feedback_item')]
            feedback_database['feedback'] = feedback_dict
            feedback_database.close()
    return redirect(url_for('staff.feedback'))


@staff.route("/home")
def home():
    return render_template("utilities-index.html")


@staff.route("/inventory")
def inventory():
    return render_template('staff-inventory-management.html')


@staff.route("/messages")
def messages():
    message_database = shelve.open('messages.db', 'c')
    message_dict = {}
    if 'message' in message_database:
        message_dict = message_database['message']
    else:
        message_database['message'] = message_dict
    print(message_dict)
    return render_template("staff-messages.html", message_dict=message_dict)


@socketio.on('message')  # main event of messaging
def handleMessage(msg):  # second step
    print("Message: " + msg)
    try:
        message_database = shelve.open('messages.db', 'c')
        message = Message(description=msg, sender=current_user.username)
        message_dict = {}
        if 'message' in message_database:
            message_dict = message_database['message']

        else:
            message_database['message'] = message_dict
    except:
        print("What went wrong")
    else:
        message_dict[message.get_id()] = message
        print(message_dict)
        message_database['message'] = message_dict
        message_database.close()

    send(msg, broadcast=True)  # send message, broadcast is to send to everyone


@socketio.on('connect')
def handleConnect(auth):
    emit('responses', auth)  # emit is for custom responses/events


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
            new_note = Notes(title=add_notes_form.title.data, description=add_notes_form.description.data,
                             time_added=datetime.now().strftime("%d/%m/%y"), time_updated=datetime.now().strftime("%d/%m/%y"))
            user_notes[new_note.get_id()] = new_note
            print(user_notes)
            notes_database[str(current_user.id)] = user_notes
            notes_database.close()
            return redirect(url_for("staff.notes"))
    return render_template("staff-notes.html", add_notes_form=add_notes_form, user_notes=user_notes)


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
    status_dict = {True: "Disabled",
                   False: "Active"}
    users = User.query.all()

    return render_template("staff-user-management.html", users=users, status_dict=status_dict)


@staff.route("/logs")
def logs():
    return render_template("staff-website-log.html")


@staff.route("/tickets")
def tickets():
    reply_ticket_form = TicketForm(request.form)
    severity_dict = {"Low": "success",
                     "Medium": "warning", "High": "danger"}
    status_dict = {"Pending": "dark",
                   "Reviewed": "secondary"}
    try:
        ticket_dict = {}
        ticket_database = shelve.open('ticket.db', 'c')
        if 'ticket' in ticket_database:
            ticket_dict = ticket_database['ticket']
        else:
            ticket_database['ticket'] = ticket_dict
        ticket_dict = dict(
            sorted(ticket_dict.items(), key=lambda x: x[1].get_status() == "Resolved"))
    except ValueError:
        flash("Something unexpected has happened", category='error')
    ticket_database.close()

    return render_template("staff-ticket.html", ticket_dict=ticket_dict, severity_dict=severity_dict, status_dict=status_dict, reply_ticket_form=reply_ticket_form)


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
                current_user_dict = ticket_database[str(
                    request.form.get('sender'))]
            else:
                ticket_database[str(request.form.get(
                    'sender'))] = current_user_dict

        except:
            flash("Something unexpected has occurred", category="error")
        else:
            direct_ticket = ticket_dict[request.form.get('uuid')]
            direct_ticket.set_reply_title(reply_ticket_form.title.data)
            direct_ticket.set_reply_description(
                reply_ticket_form.description.data)
            direct_ticket.set_status("Resolved")
            direct_ticket.set_reply_time_sent()
            direct_ticket.set_replied_staff(current_user.username)
            current_user_dict[request.form.get('uuid')] = direct_ticket
            ticket_database['ticket'] = ticket_dict
            ticket_database[str(request.form.get('sender'))
                            ] = current_user_dict
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
            if current_user_dict[request.form.get('uuid')].get_status() == "Pending":
                current_user_dict[request.form.get(
                    'uuid')].set_status("Unresolved")
            ticket_database['ticket'] = ticket_dict
            ticket_database[request.form.get('user')] = current_user_dict

    return redirect(url_for('staff.tickets'))


@staff.route("/deleteUser", methods=["GET", "POST"])
def deleteUser():
    if request.method == "POST":
        deletes = request.form.get("id")
        User.query.filter_by(id=deletes).delete()
        db.session.commit()
        print("User Deleted")
    return redirect(url_for("staff.users"))


@staff.route("/updateUser/<int:id>", methods=["GET", "POST"])
def updateUser(id):
    update_user_form = EditUser(request.form)
    user = User.query.filter_by(id=id).first()
    if request.method == "POST":
        user.money = update_user_form.amount.data
        if User.query.filter_by(email=update_user_form.email.data).first() and User.query.filter_by(email=update_user_form.email.data).first().id != user.id:
            flash("The email is not unique!", category="error")
        elif User.query.filter_by(username=update_user_form.username.data).first() and User.query.filter_by(username=update_user_form.username.data).first().id != user.id:
            flash("The username is not unique!", category="error")
        else:
            user.username = update_user_form.username.data
            user.email = update_user_form.email.data
            user.gender = update_user_form.gender.data
            user.password = generate_password_hash(
                update_user_form.password.data, method='sha256')
            user.staff = update_user_form.permission.data
            user.address = update_user_form.address.data
            user.disabled = bool(int(request.form.get('options')))
            flash(f"{user.username} <ID: {user.id}> has been updated.")
            db.session.commit()
            return redirect(url_for('staff.users'))
    update_user_form.amount.data = user.money
    update_user_form.email.data = user.email
    update_user_form.username.data = user.username
    update_user_form.gender.data = user.gender
    update_user_form.password.data = user.password
    update_user_form.permission.data = user.staff
    update_user_form.address.data = user.address

    return render_template("staff-update-user.html", update_user_form=update_user_form, user=user)


@staff.route('/addUser/', methods=['GET', 'POST'])
def addUser():
    add_user_form = AddUser(request.form)
    if request.method == "POST":
        if User.query.filter_by(email=add_user_form.email.data).first():
            print(User.query.filter_by(email=add_user_form.email.data))
            flash("Email already exists", category='error')
        elif User.query.filter_by(username=add_user_form.username.data).first():
            flash("Username already exists", category='error')
        else:
            user = User(staff=add_user_form.permission.data, username=add_user_form.username.data, email=add_user_form.email.data,
                        gender=add_user_form.gender.data, password=generate_password_hash(add_user_form.password.data), money=add_user_form.amount.data, address=add_user_form.address.data)
            db.session.add(user)
            db.session.commit()
            flash(f"Successfully added {user.username} <ID: {user.id}>")
        return redirect(url_for('staff.users'))
    return render_template('staff-add-users.html', add_user_form=add_user_form)


@staff.route("/suppliers", methods=["GET", "POST"])
def suppliers():
    add_suppliers = AddSuppliersForm(request.form)
    try:
        supplier_database = shelve.open('supplier.db', 'c')
        supplier_dict = {}
        if 'supplier' in supplier_database:
            supplier_dict = supplier_database['supplier']
        else:
            supplier_database['supplier'] = supplier_dict
        supplier_database.close()
    except Exception as e:
        flash(f"Something unexpected has went wrong {e}", category='error')
    supplier_dict = dict(reversed(supplier_dict.items()))
    if request.method == "POST":
        supplier = supplier_dict[request.form.get('uuid')]
        supplier.set_status("unedited")
        add_suppliers.suppliers_name.data = supplier.get_name()
        add_suppliers.suppliers_description.data = supplier.get_description()
        add_suppliers.products.data = ','.join(
            supplier.get_product_in_charge())

    return render_template("staff-suppliers.html", supplier_dict=supplier_dict, add_suppliers=add_suppliers)


@staff.route("/addProduct", methods=["GET", "POST"])
def addProduct():
    add_product_form = AddProductForm(request.form)
    return render_template("staff-addProduct.html", add_product_form=add_product_form)


@staff.route("/addSupplier", methods=["GET", "POST"])
def addSupplier():
    try:
        supplier_dict = {}
        supplier_database = shelve.open("supplier.db", 'c')
        if 'supplier' in supplier_database:
            supplier_dict = supplier_database['supplier']
        else:
            supplier_database['supplier'] = supplier_dict
    except Exception as e:
        flash(f"Something went wrong {e}")
    if request.method == "GET":
        supplier = Supplier()
        supplier_dict[supplier.get_id()] = supplier
        supplier_database['supplier'] = supplier_dict
    elif request.method == 'POST':
        add_suppliers = AddSuppliersForm(request.form)
        supplier = supplier_dict[request.form.get('uuid')]
        supplier.set_status("edited")
        supplier.set_name(add_suppliers.suppliers_name.data)
        supplier.set_product_in_charge(
            str(add_suppliers.products.data).replace(" ", "").split(","))
        supplier.set_description(add_suppliers.suppliers_description.data)
        supplier_database['supplier'] = supplier_dict
        supplier_database.close()
    return redirect(url_for('staff.suppliers'))


@staff.route("/removeSupplier", methods=["GET", "POST"])
def removeSupplier():
    try:
        supplier_dict = {}
        supplier_database = shelve.open("supplier.db", 'c')
        if 'supplier' in supplier_database:
            supplier_dict = supplier_database['supplier']
        else:
            supplier_database['supplier'] = supplier_dict
    except Exception as e:
        flash(f"Something went wrong {e}")
    if request.method == 'POST':
        del supplier_dict[request.form.get('uuid')]
    supplier_database['supplier'] = supplier_dict
    supplier_database.close()
    return redirect(url_for('staff.suppliers'))


@staff.route("/mail", methods=["GET", "POST"])
def mail():
    email_form = EmailForm(request.form)
    staffs = User.query.filter_by(staff=1)
    current_user_dict = {current_user.username: "You"}

    try:
        mail_database = shelve.open('mail.db', 'c')
      
        mail_dict_sender = {}
        
        if str(current_user.id) in mail_database:
            mail_dict_sender = mail_database[str(current_user.id)]
        else:
            mail_database[str(current_user.id)] = mail_dict_sender
        
      
    except Exception as e:
        flash(f"Something unexpected has occurred {e}", category='error')
    if request.method == "POST":
     
        mail = Mail(email_form.title.data, email_form.description.data, [request.form.get('recipient'), User.query.get(
            int(request.form.get('recipient'))).username], [str(current_user.id), current_user.username])
        try:

            inbox_database = shelve.open('inbox.db', 'c') 
            inbox_dict_send = []
            inbox_dict_recipient = []
            if str(current_user.id) in inbox_database:
                inbox_dict_send = inbox_database[str(current_user.id)]
            else:
                inbox_database[str(current_user.id)] = inbox_dict_send
            if request.form.get('recipient') in inbox_database:
                inbox_dict_recipient = inbox_database[request.form.get('recipient')]
            else:
                inbox_database[request.form.get('recipient')] = inbox_dict_recipient
            mail_dict_recipient = {}
            if request.form.get('recipient') in mail_database:
                mail_dict_recipient = mail_database[request.form.get(
                    'recipient')]
            else:
                mail_database[request.form.get(
                    'recipient')] = mail_dict_recipient
        except Exception as e:
            flash(f"Something unexpected has occurred {e}", category='error')
        else:
            inbox_dict_send.append(mail)
            inbox_dict_recipient.append(mail)
            mail_dict_recipient[mail.get_id()] = mail
            mail_dict_sender[mail.get_id()] = mail
            mail_database[str(current_user.id)] = mail_dict_sender
            mail_database[request.form.get('recipient')] = mail_dict_recipient
            inbox_database[str(current_user.id)] = inbox_dict_send
            inbox_database[request.form.get('recipient')] = inbox_dict_recipient
            flash(
                f"Mail sent to {User.query.get(int(request.form.get('recipient'))).username}", category='success')
            inbox_database.close()
            return redirect(url_for('staff.mail'))
    mail_database.close()
    mail_dict_sender = dict(sorted(mail_dict_sender.items(), key=lambda x : x[1].get_time_sent(), reverse=True))

    return render_template('staff-mail.html', email_form=email_form, staffs=staffs, mail_dict_sender=mail_dict_sender, current_user_dict=current_user_dict)


@staff.route("/mail/view/<string:uuid>", methods=["GET", "POST"])
def viewMail(uuid):
    current_user_dict = {current_user.username: "You"}
    try:
        email_form = EmailForm(request.form)
        mail_database = shelve.open('mail.db', 'c')
        inbox_database = shelve.open('inbox.db', 'c')
        mail_dict_sender = {}
        current_inbox = []
        if str(current_user.id) in inbox_database:
            current_inbox = inbox_database[str(current_user.id)]
        else:
            inbox_database[str(current_user.id)] = current_inbox
        if str(current_user.id) in mail_database:
            mail_dict_sender = mail_database[str(current_user.id)]
        else:
            mail_database[str(current_user.id)] = mail_dict_sender
        mail = mail_dict_sender[uuid]
    except KeyError:
        flash(
            f"This ticket does not exist!", category='error')
        return redirect(url_for('staff.mail'))
    except Exception as e:
        flash(f"Something unexpected has occurred -> {e}")
    else:
        print(current_inbox)
        print(mail)
        for x,y in enumerate(current_inbox):
            if mail.get_id() == y.get_id():
                current_inbox.pop(x)
       
        inbox_database[str(current_user.id)] = current_inbox 
        inbox_database.close()
        mail_database.close()
        return render_template("staff-mailview.html", mail=mail, email_form=email_form, current_user_dict=current_user_dict)


@staff.route("/mail/reply", methods=['GET', "POST"])
def replyMail():

    if request.method == 'POST':
        email_form = EmailForm(request.form)
        try:
            mail_database = shelve.open('mail.db', 'c')
            mail_dict_sender = {}
            mail_dict_recipient = {}
            if str(current_user.id) in mail_database:
                mail_dict_sender = mail_database[str(current_user.id)]
            else:
                mail_database[str(current_user.id)] = mail_dict_sender
            if request.form.get('recipient') in mail_database:
                mail_dict_recipient = mail_database[request.form.get(
                    'recipient')]
            else:
                mail_database[request.form.get(
                    'recipient')] = mail_dict_recipient


            inbox_database = shelve.open('inbox.db', 'c') 
            inbox_dict_send = []
            inbox_dict_recipient = []
            if str(current_user.id) in inbox_database:
                inbox_dict_send = inbox_database[str(current_user.id)]
            else:
                inbox_database[str(current_user.id)] = inbox_dict_send
            if request.form.get('recipient') in inbox_database:
                inbox_dict_recipient = inbox_database[request.form.get('recipient')]
            else:
                inbox_database[request.form.get('recipient')] = inbox_dict_recipient

        except Exception as e:
            flash(
                f"Something unexpected has occurred replyMail {e}", category='error')
        else:
            mail_original = mail_dict_sender[request.form.get('reply_uuid')]
            mail_reply = Mail(title=email_form.title.data, description=email_form.description.data, recipient=mail_original.get_sender(), sender=mail_original.get_recipient())
            mail_reply.get_mail_reply().append(
                [mail_original.get_id(), mail_original.get_title()])
            mail_dict_sender[mail_reply.get_id()] = mail_reply
            mail_dict_recipient[mail_reply.get_id()] = mail_reply
            mail_database[str(current_user.id)] = mail_dict_sender
            mail_database[request.form.get('recipient')] = mail_dict_recipient

            inbox_dict_send.append(mail_reply)
            inbox_dict_recipient.append(mail_reply)

            inbox_database[request.form.get('recipient')] = inbox_dict_recipient
            inbox_database[str(current_user.id)] = inbox_dict_send

            flash("Sent!", category="success")
            
    return redirect(url_for('staff.mail'))


@staff.route("/mail/delete", methods=["GET", "POST"])
def deleteMail():
    if request.method == "POST":
        try:
            mail_dict_user = {}
            mail_database = shelve.open('mail.db', 'c')
            if str(current_user.id) in mail_database:
                mail_dict_user = mail_database[str(current_user.id)]
            else:
                mail_database[str(current_user.id)] = mail_dict_user
        except Exception as e:
            flash(f"{e}", category="error")
        else:
            del mail_dict_user[request.form.get('uuid')]
            mail_database[str(current_user.id)] = mail_dict_user
            mail_database.close()
    return redirect(url_for("staff.mail"))

