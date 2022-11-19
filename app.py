import secrets
import datetime
from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
#from tempfile import mkdtemp
from werkzeug.security import check_password_hash, generate_password_hash
from helpers import error, login_required
from pathlib import Path
from mail import send_mail

# Configure application
app = Flask(__name__)
# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)
# Configure secret key
#! Store secret keys in a hidden file (Stack overflow)
SECRET_FILE_PATH = Path(".flask_secret")
try:
    with SECRET_FILE_PATH.open("r") as secret_file:
        app.secret_key = secret_file.read()
except FileNotFoundError:
    # Create secure code in that file
    with SECRET_FILE_PATH.open("w") as secret_file:
        app.secret_key = secrets.token_hex(48)
        secret_file.write(app.secret_key)

# Configure SQLite Database
db = SQL("sqlite:///note.db")

@app.after_request
def after_request(response):
    """Ensure responses are not cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""
    # Clear session
    session.clear()
    # Variables
    email = request.form.get("email")
    password = request.form.get("password")

    if request.method == "GET":
        return render_template("login.html")
    else:
        # Set login email to lower()
        email = email.lower()

        # Validate login details
        if not email:
            return error("Please provide the email address you used during registration!")
        elif not password:
            return error("Please enter you password!")

        # Query database for user profile
        user = db.execute("SELECT * FROM users WHERE email = ?", email)

        # Check if user exist
        if len(user) != 1 or not check_password_hash(user[0]["hash"], password):
            return error("Invalid username / password!", 403)
        else:
            flash("Logged in!")

        # Remember which user logged in
        session["user_id"] = user[0]["id"]
        # Direct user to home page
        return redirect("/")

@app.route("/", methods=["GET", "POST"])
@login_required
def index():
    """Show user notes"""
    # Global Variables
    user_id = session["user_id"]
    add_note = request.form.get("note")
    today = datetime.date.today()

    if request.method == "GET":
        # Get username to display welcome message.
        username_query = db.execute("SELECT username FROM users WHERE id = ?", user_id)
        username = username_query[0]["username"]
        # Call user notes
        user_notes = db.execute("SELECT * FROM notes WHERE user_id = ? AND visible = 1", user_id)
        return render_template("index.html", username=username, user_notes=user_notes)
    else:
        if add_note:
            # Insert note into database
            db.execute("INSERT INTO notes (user_id, note, date) VALUES (?, ?, ?)", user_id, add_note, today)
            flash("Note added")
        # Return to home / index page
        return redirect("/")

@app.route("/delete", methods=["GET", "POST"])
@login_required
def delete():
    """Remove user note"""
    # Global Variables
    today = datetime.date.today()

    if request.method == "POST":
        # Create list of id's
        note_id = request.args["id"]
        # Remove note
        db.execute("UPDATE notes SET visible = 0, date = ? WHERE id = ?", today, note_id)
        flash("Note removed")
        return redirect("/")


@app.route("/history", methods=["GET"])
@login_required
def history():
    """Show history of notes"""
    # Global Variables
    user_id = session["user_id"]

    if request.method == "GET":
        completed_notes = db.execute("SELECT * FROM notes WHERE user_id = ? AND visible = 0", user_id)
        return render_template("history.html", completed_notes=completed_notes)

@app.route("/logout")
def logout():
    """Log user out"""
    # Forget any user_id
    session.clear()
    # Redirect user to login form
    return redirect("/")

@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""

    # Variables
    # Username
    username = request.form.get("username")
    # Email address
    email = request.form.get("email")
    # Password
    password = request.form.get("password")

    if request.method == "POST":
        # Validate Username
        if not username:
            return error("Please enter a username!")
        # Validate email address
        if not email:
            return error("Please enter a valid email address!")
        elif "@" not in email and "." not in email:
            return error("Enter a valid email address please!")
        # Check if username already in database
        username_check = db.execute("SELECT username FROM users WHERE username = ?", username)
        if len(username_check) == 1:
            return error("This username is not available. Please choose another. ", 400)
        # Set email to lowercase
        email = email.lower()
        # Check if email already in database
        email_check = db.execute("SELECT email FROM users WHERE email = ?", email)
        if len(email_check) == 1:
            return error("This Email Address Has already been registered. Please select forgotten password. ", 400)
        # Validate password
        if not password:
            return error("a Password is required")
        # Confirm Password
        confirmation = request.form.get("confirmation")
        # Validate password
        if password != confirmation or not confirmation:
            return error("Passwords do not match!")

        # Hash password for security
        hash = generate_password_hash(password, method='pbkdf2:sha256', salt_length=24)

        # Insert user details into database
        db.execute("INSERT INTO users (username, email, hash) VALUES(?, ?, ?)", username, email.lower(), hash)

        # Log user in after successful registration
        new_user = db.execute("SELECT * FROM users WHERE email = ?", email)
        session["user_id"] = new_user[0]["id"]
        flash("Successfully Registered!")
        return redirect("/")
    else:
        return render_template("register.html")

@app.route("/password-reset-request", methods=["GET", "POST"])
def password_reset_request():
    """User request password reset"""
    # Get password from user input
    email = request.form.get('email')

    if request.method == "POST":
        # Query database for email address
        valid_email = db.execute("SELECT email FROM users WHERE email = ?", email)
        if not valid_email:
            flash("Not a valid Email address")
        else:
            # Send email with security token & url to reset user password
            send_mail()
            flash("Password Request has been sent to your email address")

    return render_template("/password-reset-request.html")

@app.route("/password-reset", methods=["POST", "GET"])
def password_reset():
    """Reset user password"""
    if request.method == "GET":
        # Query string to get token
        token = request.args['token']
        # Validate Token
        valid_token = db.execute("SELECT * FROM users WHERE reset_token = ?", token)
        # Variables to validate
        request_time_query = db.execute("SELECT token_timer FROM users WHERE reset_token = ?", token )
        request_time = request_time_query[0]["token_timer"]
        current_time = datetime.datetime.now()
        #! TypeError: unsupported operand type(s) for -: 'datetime.datetime' and 'str' / https://stackoverflow.com/questions/12126318/subtracting-dates-with-python (strptime)
        # Subtract current time from request time. strptime converts string to datetime
        diff_time = current_time - datetime.datetime.strptime(request_time, "%Y-%m-%d %H:%M:%S")
        # Check token && Time expiry
        if token != valid_token and diff_time.total_seconds() > 600:
            return error("Invalid token")
        else:
            return render_template("/password-reset.html", token=token)
    # If token is Valid and time has not yet expired update user password and return to login
    else:
        token = request.args['token']
        #token = request.form.get("token")

        # Global Variables
        password = request.form.get("password")

        # Validate password
        if not password:
            return error("a Password is required")
        # Confirm Password
        confirmation = request.form.get("confirmation")
        # Validate password
        if password != confirmation or not confirmation:
            return error("Passwords do not match!")

        # Hash password
        hash = generate_password_hash(password, method='pbkdf2:sha256', salt_length=24)
        db.execute("UPDATE users SET hash = ? WHERE reset_token = ?", hash, token)
        # Flash successful message
        flash("Password successfully reset")
        # Once password reset completed clear cookies and timer
        db.execute("UPDATE users SET reset_token = NULL, token_timer = NULL WHERE reset_token = ?", token)
        return redirect("/login")