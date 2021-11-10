from flask import *
app = Flask(__name__)

from utilities import blueprint_utilities



app.register_blueprint(blueprint_utilities, url_prefix="/utilities")

if __name__ == "__main__":
    app.run(debug=True)