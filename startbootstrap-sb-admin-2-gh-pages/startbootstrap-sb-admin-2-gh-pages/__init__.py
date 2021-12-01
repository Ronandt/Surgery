from flask import *
app = Flask(__name__)

from utilities import blueprint_utilities



app.register_blueprint(blueprint_utilities, url_prefix="/utilities")

@app.route("/staff")
def staff_html():
    return render_template("utilities-blank-base.html")


@app.route("/")
def main_html():
    return render_template("page-index-3.html")



if __name__ == "__main__":
    app.run(debug=True)