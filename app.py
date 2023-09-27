import os
from flask import Flask, render_template
from flasgger import Swagger

basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)

# DATABASE_PATH = os.path.join(basedir, "hotelbca.db")

app.config[
    "SQLALCHEMY_DATABASE_URI"
] = "mysql+mysqlconnector://root:FUeY6phVMNPy7EGkNi3V@containers-us-west-48.railway.app:7708/railway"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Swagger
app.config["SWAGGER"] = {
    "title": "Data Booking Hotel BCA",
    "uiversion": 3,
    "headers": [],
    "specs": [
        {
            "endpoint": "apispec_1",
            "route": "/apispec_1.json",
            "rule_filter": lambda rule: True,
            "model_filter": lambda tag: True,
        }
    ],
    "static_url_path": "/flasgger_static",
    "swagger_ui": True,
    "specs_route": "/apidocs/",
}

swagger = Swagger(app)

from extensions import db

db.init_app(app)


@app.before_first_request
def create_tables():
    db.create_all()


@app.route("/")
def index():
    return render_template("index.html")


from routes.room import bp as room_bp
from routes.booking import bp as booking_bp

app.register_blueprint(room_bp)
app.register_blueprint(booking_bp)

if __name__ == "__main__":
    app.run(debug=True)
