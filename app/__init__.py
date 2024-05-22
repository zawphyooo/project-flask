from flask import Flask
from flask_mail import Mail
from flask_session import Session
from cs50 import SQL
from app.helpers import usd

app = Flask(__name__)
app.config.from_object('app.config.Config')  # Load configuration from config.py

# Initialize extensions
mail = Mail(app)  # Initialize Flask-Mail

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///finance.db")

# Custom filter
app.jinja_env.filters["usd"] = usd

# Import and register blueprints
from app.main import main as main_blueprint
app.register_blueprint(main_blueprint)

from app import email  # Import email to register it with the app

@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response
