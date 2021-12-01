from flask import Blueprint, render_template

user_page = Blueprint("user_page", __name__)
@user_page.route("/login")
def user_login():
    return render_template("page-user-login.html")

@user_page.route("/register")
def user_register():
    return render_template("page-user-register.html")


@user_page.route("/account")
def user_forgot():
    return render_template("page-profile-main")

@user_page.route("/feedback")
def feedback():
    return ""