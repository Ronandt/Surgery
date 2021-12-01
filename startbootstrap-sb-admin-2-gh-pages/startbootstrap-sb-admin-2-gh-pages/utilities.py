from flask import Blueprint, render_template


blueprint_utilities = Blueprint("blueprint_utilities", __name__)

@blueprint_utilities.route("/cards")
def cards():
    return render_template("utilities-cards.html")

@blueprint_utilities.route("/buttons")
def buttons():
    return render_template("utilities-buttons.html")
    
@blueprint_utilities.route("/animation")    
def animation():
    return render_template("utilities-animation.html")

@blueprint_utilities.route("/border")
def border():
    return render_template("utilities-border.html")

@blueprint_utilities.route("/color")
def color():
    return render_template("utilities-color.html")

@blueprint_utilities.route("/other")
def other():
    return render_template("utilities-other.html")

@blueprint_utilities.route("/charts")
def charts():
    return render_template("utilities-charts.html")

@blueprint_utilities.route("/tables")
def tables():
    return render_template("utilities-tables.html")
    
@blueprint_utilities.route("/home")
def home_index():
    return render_template("utilities-index.html")

@blueprint_utilities.route("/login")
def login_index():
    return render_template("utilities-login.html")

@blueprint_utilities.route("/register")
def register_index():
    return render_template("utilities-register.html")


@blueprint_utilities.route("/forgot")
def forgot_index():
    return render_template("utilities-forgot-password.html")
    
@blueprint_utilities.route("/err")
def err():
    return render_template("utilities-404.html")