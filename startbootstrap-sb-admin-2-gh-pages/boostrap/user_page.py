from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login.utils import login_required
from Forms import AddFundsForm, TicketForm, FeedbackForm, UpdateUserForm
from models import Ticket, Feedback, User, Product
from __init__ import db
# trying to salt it later
from werkzeug.security import generate_password_hash,  check_password_hash, gen_salt
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


@user_page.route("/products", methods=["GET", "POST"])
def products():
    try:
        search = request.args.get('search')
        product_dict = {}
        product_database = shelve.open('product.db', 'c')
        if 'products' in product_database:
            product_dict = product_database['products']
        else:
            product_database['products'] = product_dict
    except Exception as e:
        flash(f"{e}", category='error')
    if request.method == "POST":
        try:
            cart_dict = {}
            cart_database = shelve.open('cart.db', 'c')
            if str(current_user.id) in cart_database:
                cart_dict = cart_database[str(current_user.id)]
            else:
                cart_database[str(current_user.id)] = cart_dict
        except Exception as e:
            flash(f"{e}", category='error')
        else:
            if request.form.get('uuid') not in cart_dict:
                cart_dict[request.form.get('uuid')] = Product(name = product_dict[request.form.get('uuid')].get_name(), quantity = int(request.form.get('quantity')), description = product_dict[request.form.get('uuid')].get_description(), price = product_dict[request.form.get('uuid')].get_price() )
            else:
                cart_dict[request.form.get('uuid')].set_quantity(min(cart_dict[request.form.get('uuid')].get_quantity() + int(request.form.get('quantity')), product_dict[request.form.get('uuid')].get_quantity()))
                  
            flash("Item has been added!", category='success')
            cart_database[str(current_user.id)] = cart_dict
            #product_dict[request.form.get('uuid')].set_quantity(product_dict[request.form.get('uuid')].get_quantity() - int(request.form.get('quantity')))
            product_database['products'] = product_dict
            cart_database.close()
            return redirect(url_for("user_page.products"))
        
    product_database.close()

    return render_template("page-listing-grid.html", product_dict=product_dict, search = search)


@user_page.route("/cart", methods=["GET", "POST"])
def cart():
    try:
        cart_dict = {}
        product_dict = {}
        product_database = shelve.open('product.db', 'c')
        cart_database = shelve.open('cart.db', 'c')
        if str(current_user.id) in cart_database:
            cart_dict = cart_database[str(current_user.id)]
        else:
            cart_database[str(current_user.id)] = cart_dict
        if 'products' in product_database:
            product_dict = product_database['products']
        else:
            product_database['products'] = product_dict
    except Exception as e:
        flash(f"{e}", category='error')
    else:
        total = sum([x.get_quantity() * x.get_price() for x in cart_dict.values()])
    if request.method == "POST":
        all_orders = {}
        all_orders_database = shelve.open('orders.db', 'c')
        if str(current_user.id) in all_orders:
            all_orders = all_orders_database[str(current_user.id)]
        else:
            all_orders_database[str(current_user.id)] = all_orders
        all_orders = {**all_orders, **cart_dict}
        for remove in cart_dict:
            product_dict = product_database["products"]
            get_product = product_dict[remove]
            inventory_quantity = get_product.get_quantity()
            product_quantity = cart_dict[remove].get_quantity()
            inventory_quantity = inventory_quantity - product_quantity
            get_product.set_quantity(inventory_quantity)
        product_database['products'] = product_dict
        cart_dict.clear()
        
        all_orders_database[str(current_user.id)] = all_orders
        cart_database[str(current_user.id)] = cart_dict
        all_orders_database.close()
        cart_database.close()
        if total > current_user.money:
            flash("Not enough money! Please deposit more.", category='error')
        else:
            current_user.money -= total    
            db.session.commit()
            flash("Money paid", category="success")
            return redirect(url_for('user_page.cart'))

 
    return render_template("page-shopping-cart.html", cart_dict = cart_dict, product_dict= product_dict, total = total)
@user_page.route("/cart/delete", methods=["GET","POST"])
def remove_from_cart():
    if request.method == "POST":
        remove = request.form.get('uuid')
        cart_database = shelve.open('cart.db', 'c')
        cart_dict = {}
        if str(current_user.id) in cart_database:
            cart_dict = cart_database[str(current_user.id)]
        else:
            cart_database[str(current_user.id)] = cart_dict
        del cart_dict[remove]
        cart_database[str(current_user.id)] = cart_dict
        return redirect(url_for("user_page.cart"))
@user_page.route("/cart/remove", methods=["GET","POST"])
def remove_from_db():
        remove = request.form.get('uuid')
        cart_database = shelve.open('cart.db', 'c')
        cart_dict = cart_database[str(current_user.id)]
        product_dict = {}
        product_database = shelve.open('product.db', 'c')
        product_dict = product_database["products"]
        get_product = product_dict[remove]
        inventory_quantity = get_product.get_quantity()
        product_quantity = cart_dict[remove].get_quantity()
        #inventory_quantity = inventory_quantity - product_quantity
        #get_product.set_quantity(inventory_quantity)
        #product_database['products'] = product_dict
        total = sum([x.get_quantity() * x.get_price() for x in cart_dict.values()])
        if total > current_user.money:
            cart_database[str(current_user.id)] = cart_dict
            flash("Not enough money! Please deposit more.", category='error')
        else:
            current_user.money -= total
            inventory_quantity = inventory_quantity - product_quantity
            get_product.set_quantity(inventory_quantity)
            product_database['products'] = product_dict
            del cart_dict[remove]
            cart_database[str(current_user.id)] = cart_dict
            db.session.commit()
            flash("Money paid", category="success")
            return redirect(url_for('user_page.cart'))

        return redirect(url_for("user_page.cart"))
        
@user_page.route("/purchased")

@user_page.route('/purchase')
def purchase():
    pass


@user_page.route("/account")
def account():

    gender_dict = {"F": "Female",
                   "M": "Male"}
    return render_template("page-profile-main.html", gender_dict=gender_dict)


@user_page.route("/editAccount", methods=["GET", "POST"])
def editAccount():
    update_account_form = UpdateUserForm(request.form)
    gender_dict = {"F": "Female",
                   "M": "Male"}

    if request.method == "POST":
        if User.query.filter_by(username=update_account_form.username.data).first() and update_account_form.username.data != current_user.username:
            flash("This username is not unique!", category="error")
        elif User.query.filter_by(email=update_account_form.email.data).first() and update_account_form.email.data != current_user.email:
            flash("This email is not unique!", category="error")
        elif (update_account_form.repeat_password.data != update_account_form.password.data) and not check_password_hash(current_user.password, update_account_form.password.data):
            flash(
                "Your repeat password or your password is incorrect. Try again.", category="error")
        else:
            current_user.username = update_account_form.username.data
            current_user.email = update_account_form.email.data
            current_user.gender = update_account_form.gender.data
            current_user.password = generate_password_hash(
                update_account_form.password.data)
            current_user.address = update_account_form.address.data
            db.session.commit()
            flash("Updating of profile is successful!", category="success")
            return redirect(url_for('user_page.account'))

    update_account_form.username.data = current_user.username
    update_account_form.email.data = current_user.email
    update_account_form.gender.data = current_user.gender
    update_account_form.password.data = current_user.password
    update_account_form.address.data = current_user.address

    return render_template("page-edit-account.html", update_account_form=update_account_form, gender_dict=gender_dict)


@user_page.route("/disableAccount", methods=["GET", "POST"])
def disableAccount():
    if request.method == "POST":
        disable = int(request.form.get('id'))
        User.query.filter_by(id=disable).first().disabled = True
        db.session.commit()
        logout_user(disable)
    return redirect(url_for("user_page.main_html"))


@user_page.route("/deleteAccount", methods=["GET", "POST"])
def deleteAccount():
    if request.method == "POST":
        delete = request.form.get('id')
        User.query.filter_by(id=delete).delete()
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
            feedback = Feedback(description=feedback_form.remarks.data, rating=int(request.form.get('rate')), favourite=feedback_form.favourite.data,
                                least_favourite=feedback_form.least_favourite.data, improvement=feedback_form.improvement.data, title=feedback_form.title.data, sender=current_user.username)
            feedback_dict[feedback.get_id()] = feedback
            feedback_database['feedback'] = feedback_dict
            flash("Sent a feedback!", category="success")
        feedback_database.close()
        return redirect(url_for('user_page.feedback'))
    return render_template("page-feedback.html", feedback_form=feedback_form)


@user_page.route("/tickets", methods=["GET", "POST"])
def tickets():
    status_dict = {"Pending": "warning",
                   "Resolved": "success",
                   "Unresolved": "secondary"}
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

        ticket = Ticket(ticket_form.description.data, ticket_form.title.data, ticket_form.issue.data,
                        ticket_form.severity.data, current_user.id,  current_user.username)
        ticket_dict[ticket.get_id()] = ticket
        current_user_dict[ticket.get_id()] = ticket
        ticket_database['ticket'] = ticket_dict
        ticket_database[str(current_user.id)] = current_user_dict
        flash("Ticket has been sent!", category="success")
        return redirect(url_for('user_page.tickets'))
    current_user_dict = ticket_dict = dict(sorted(current_user_dict.items(
    ), key=lambda x: x[1].get_reply_time_sent(), reverse=True))
    ticket_database.close()
    print(current_user_dict)
    return render_template("page-reports.html", ticket_form=ticket_form, status_dict=status_dict, current_user_dict=current_user_dict)


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
    return render_template("page-funds.html", funds_form=funds_form)


@user_page.route("/about_us")
def about_us():

    return render_template("page-content.html")


@user_page.route('/logout')
def logout():
    logout_user()
    return redirect(url_for("login_register.user_login"))

@user_page.route('/wishlist', methods=['GET','POST']) # add from here to the end
def wishlist():
    wishlist_database = shelve.open('wishlist.db', 'c')
    wishlist_dict = {}
    if str(current_user.id) in wishlist_database:
        wishlist_dict = wishlist_database[str(current_user.id)]
    else:
        wishlist_database[str(current_user.id)] = wishlist_dict
    if request.method == "POST":
        flash("Wishlist item has been added")
        product_database = shelve.open('product.db', 'c')
        product_dict = {}
        if 'products' in product_database:
            product_dict = product_database['products']
        else:
            product_database['products'] = product_dict
  
        obj = product_dict[request.form.get('wishlist')]
        wishlist_dict[request.form.get('wishlist')] = obj
        wishlist_database[str(current_user.id)] = wishlist_dict

    return render_template("page-wishlist.html", wishlist_dict=wishlist_dict)



@user_page.route('/wishlist/delete', methods=['GET', 'POST'])
def delete():
    if request.method == "POST":   
        flash("Wishlist item has been removed")
        wishlist_dict = {}
        wishlist_database = shelve.open('wishlist.db', 'c')
        if str(current_user.id) in wishlist_database:
            wishlist_dict = wishlist_database[str(current_user.id)]
        del wishlist_dict[request.form.get('uuid')]
        wishlist_database[str(current_user.id)] = wishlist_dict
        return redirect(url_for("user_page.wishlist"))

@user_page.route("/wishlist/addtocart", methods=["GET", "POST"])
def wishlist_addtocart():
    try:
        product_dict = {}
        product_database = shelve.open('product.db', 'c')
        if 'products' in product_database:
            product_dict = product_database['products']
        else:
            product_database['products'] = product_dict
    except Exception as e:
        flash(f"{e}", category='error')
    if request.method == "POST":
        try:
            cart_dict = {}
            cart_database = shelve.open('cart.db', 'c')
            if str(current_user.id) in cart_database:
                cart_dict = cart_database[str(current_user.id)]
            else:
                cart_database[str(current_user.id)] = cart_dict
        except Exception as e:
            flash(f"{e}", category='error')
        else:
            if request.form.get('uuid') not in cart_dict:
                cart_dict[request.form.get('uuid')] = Product(name = product_dict[request.form.get('uuid')].get_name(), quantity = int(request.form.get('quantity')), description = product_dict[request.form.get('uuid')].get_description(), price = product_dict[request.form.get('uuid')].get_price() )
            else:
                cart_dict[request.form.get('uuid')].set_quantity(cart_dict[request.form.get('uuid')].get_quantity() + int(request.form.get('quantity')))
                  
            flash("Item has been added!", category='success')
            cart_database[str(current_user.id)] = cart_dict
            product_dict[request.form.get('uuid')].set_quantity(product_dict[request.form.get('uuid')].get_quantity() - int(request.form.get('quantity'))) 
            product_database['products'] = product_dict
            cart_database.close()
            return redirect(url_for("user_page.wishlist"))
