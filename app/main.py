from flask import Blueprint, render_template, request, session, redirect, flash, url_for
from cs50 import SQL
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import datetime
from app.helpers import apology, login_required, lookup, usd
from app import db


main = Blueprint('main', __name__)

@main.route("/")
@login_required
def index():
    profile = db.execute("SELECT * FROM users WHERE id = ?", session.get('user_id'))

    """Show portfolio of stocks"""
    shares = db.execute("SELECT * from shares where user_id =?", session.get('user_id'))
    for share in shares:
        symbol = share["symbol"]
        info = lookup(symbol)
        numShares = share["shares"]
        share["price"] = info["price"]
        share["total"] = info["price"] * numShares

    totalSharesAmt = 0
    for share in shares:
        totalSharesAmt += float(share["total"])

    cashBal = db.execute("SELECT cash from users where id =?", session.get('user_id'))
    grandTotl = totalSharesAmt + cashBal[0]["cash"]
    return render_template("index.html", shares=shares, totalSharesAmt=cashBal[0]["cash"], grandTotl=grandTotl, profile=profile[0]['username'])

@main.route('/send-email')
def send_test_email():
    from app.email import send_email
    message, status_code = send_email(
        'Test Email 2',
        recipients=['achemede@gmail.com'],
        text_body='This is a test email sent from a Flask application!',
        html_body='<p>This is a <b>test</b> email sent from a Flask application!</p>'
    )
    return message, status_code

@main.route("/buy", methods=["GET", "POST"])
@login_required
def buy():
    profile = db.execute("SELECT * FROM users WHERE id = ?", session.get('user_id'))

    """Buy shares of stock"""
    if request.method == "POST":
        if not request.form.get("symbol"):
            return apology("Must provide symbol")
        if not request.form.get("shares"):
            return apology("Must provide shares")
        # Check user input
        symbolvalue = lookup(request.form.get("symbol"))
        if symbolvalue is None:
            return apology("That symbol " + request.form.get("symbol") + " doesn't exist")

        symbPrice = symbolvalue['price']
        try:
            numShares = float(request.form.get("shares"))
        except ValueError:
            return apology("Please provide a number")
        if int(numShares) < 1:
            return apology("Provide a value greater than zero")
        if numShares != int(numShares):
            return apology("Provide an integer value")
        if not isinstance(numShares, (int, float)):
            return apology("Provide an integer value")

        Symb = symbolvalue['symbol']

        # get the user balance
        user = db.execute("SELECT * FROM users WHERE id = ?", session.get('user_id'))
        usrBal = user[0]["cash"]
        sharesCost = int(numShares) * symbPrice

        # check if user has enough balance
        if sharesCost < usrBal:
            # update user balance
            db.execute("UPDATE users SET cash = ? WHERE id = ?", (usrBal - sharesCost), session.get('user_id'))
            db.execute("INSERT INTO history (user_id, symbol, shares, price, transacted) VALUES (?, ?, ?, ?, ?)",
                       session.get('user_id'), Symb, numShares, sharesCost, datetime.now())

            shares = db.execute("SELECT * FROM shares WHERE user_id = ? AND symbol = ?", session.get('user_id'), Symb)
            if len(shares) != 1:
                db.execute("INSERT INTO shares (user_id, symbol, shares) VALUES (?, ?, ?)",
                           session.get('user_id'), Symb, numShares)
            else:
                db.execute("UPDATE shares SET shares = ? WHERE user_id = ? AND symbol = ?",
                           shares[0]['shares'] + int(numShares), session.get('user_id'), Symb)

        elif sharesCost > usrBal:
            return apology("You don't have enough cash")

        flash("Successfully bought the shares")
        return redirect("/")

    else:
        return render_template("buypage.html", profile=profile[0]['username'])

@main.route("/history")
@login_required
def history():
    """Show history of transactions"""
    history = db.execute("SELECT * FROM history WHERE user_id = ?", session.get('user_id'))
    profile = db.execute("SELECT * FROM users WHERE id = ?", session.get('user_id'))
    return render_template("history.html", history=history, profile=profile[0]['username'])

@main.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""
    # Forget any user_id
    session.clear()

    if request.method == "POST":
        if not request.form.get("email"):
            return apology("must provide email")
        if not request.form.get("password"):
            return apology("must provide password")

        rows = db.execute("SELECT * FROM users WHERE email = ?", request.form.get("email"))
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return apology("invalid email and/or password")

        session["user_id"] = rows[0]["id"]
        flash("Login successful")
        return redirect("/")

    else:
        return render_template("login.html")

@main.route("/logout")
def logout():
    """Log user out"""
    session.clear()
    return redirect("/")

@main.route("/quote", methods=["GET", "POST"])
@login_required
def quote():
    profile = db.execute("SELECT * FROM users WHERE id = ?", session.get('user_id'))
    if request.method == "POST":
        if not request.form.get("symbol"):
            return apology("Must provide symbol")

        symbolvalue = lookup(request.form.get("symbol"))
        if symbolvalue is None:
            return apology("That symbol " + request.form.get("symbol") + " doesn't exist")

        valUsd = usd(symbolvalue['price'])
        valSymb = symbolvalue['symbol']
        return render_template("quoted.html", valUsd=valUsd, valSymb=valSymb)

    else:
        return render_template("quote.html", profile=profile[0]['username'])

@main.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    session.clear()

    if request.method == "POST":
        if not request.form.get("username"):
            return apology("must provide username")
        if not request.form.get("email"):
            return apology("must provide email")
        if not request.form.get("password"):
            return apology("must provide password", 400)
        if request.form.get("password") != request.form.get("confirmation"):
            return apology("passwords do not match", 400)

        usrpwd = request.form.get("password")
        usrpwdHash = generate_password_hash(usrpwd)
        
        #Check if the email already exists 
        rows = db.execute("SELECT * FROM users WHERE email = ?", request.form.get("email"))
        if len(rows) != 1:
            db.execute("INSERT INTO users (username, hash, email) VALUES (?, ?, ?)", request.form.get("username"), usrpwdHash, request.form.get("email"))
        else:
            return apology("email " + rows[0]['email'] + " already exists")

        user = db.execute("SELECT * FROM users WHERE email = ?", request.form.get("email"))
        session["user_id"] = user[0]["id"]
        return redirect("/")

    else:
        return render_template("register.html")

@main.route("/sell", methods=["GET", "POST"])
@login_required
def sell():
    profile = db.execute("SELECT * FROM users WHERE id = ?", session.get('user_id'))

    if request.method == "POST":
        if not request.form.get("symbol"):
            return apology("Select a symbol please!")
        if not request.form.get("shares"):
            return apology("Fill the number of shares!")

        user = db.execute("SELECT * FROM users WHERE id = ?", session.get('user_id'))
        usrBal = user[0]["cash"]
        numShares = int(request.form.get("shares"))
        symbolvalue = lookup(request.form.get("symbol"))
        symbPrice = symbolvalue['price']
        Symb = symbolvalue['symbol']
        sharesCost = float(numShares) * symbPrice

        shares = db.execute("SELECT shares FROM shares WHERE user_id = ? AND symbol = ?", session.get('user_id'), Symb)
        if shares[0]['shares'] < numShares:
            return apology("You don't have that many shares")

        db.execute("UPDATE users SET cash = ? WHERE id = ?", (usrBal + sharesCost), session.get('user_id'))
        db.execute("UPDATE shares SET shares = ? WHERE user_id = ? AND symbol = ?",
                   shares[0]['shares'] - int(numShares), session.get('user_id'), Symb)
        db.execute("INSERT INTO history (user_id, symbol, shares, price, transacted) VALUES (?, ?, ?, ?, ?)",
                   session.get('user_id'), Symb, -numShares, sharesCost, datetime.now())

        flash("Congratulations! Your sell was successful")
        return redirect("/")

    else:
        usrid = session.get('user_id')
        symbols = db.execute("SELECT symbol FROM shares WHERE user_id = ?", usrid)
        return render_template("sell.html", symbols=symbols, profile=profile[0]['username'])

@main.route("/profile", methods=["GET", "POST"])
@login_required
def profile():
    user_id = session.get('user_id')
    profile = db.execute("SELECT * FROM users WHERE id = ?", user_id)[0]

    if request.method == "POST":
        # Handle multi-factor authentication update
        enable_2fa = request.form.get("2fa") == "on"
        db.execute("UPDATE users SET mfactor = ? WHERE id = ?", enable_2fa, user_id)

        flash("Profile updated successfully.", "success")
        return redirect(url_for('main.profile'))

    return render_template("profile.html", profile=profile)


@main.route("/forgetpass", methods = ["GET", "POST"])
def forgetpass():
    from app.email import generate_token
    from app.email import send_email
    if request.method == "POST":
        email = request.form.get("email")
        print(f"email {email}")
    # check if email exists in the database
        user = db.execute("SELECT * FROM users WHERE email = ?", email)
        if user:
            token = generate_token(email)
            print(f"token {token}, email {email}")
            # Store the token in database
            db.execute("UPDATE users SET token = ? WHERE email = ?", token, email)

            # Send email with link

            reset_url = url_for('main.reset_password', token=token, _external=True)
            print(f'The url : {reset_url}')

            # Send the email with the reset link
            subject = "Flask Server Password Reset"
            text_body = f"Please click the following link to reset your password: {reset_url}"
            html_body = f"<p>Please click the following link to reset your password:</p><p><a href='{reset_url}'>{reset_url}</a></p> </br> <p>Flask Server</p>"
            
            message, status_code = send_email(subject, [email], text_body, html_body)
            flash(message)
            #flash("Password Reset Email sent !")
            return render_template("login.html")

        
        return apology("Email not found in the System", 400)
    else:
        return(render_template("forgetpass.html"))
    

@main.route("/reset_password", methods=["GET", "POST"])
def reset_password():
    token = request.args.get('token')
    print(f"Token {token}")
    if not token:
        return apology("Invalid or missing token", 400)
    
    # Find the user by the token
    user = db.execute("SELECT * FROM users WHERE token = ?", token)

    if not user:
        return apology("Invalid or expired token", 400)
    
    if request.method == "POST":
        new_password = request.form.get("password")
        if not new_password:
            return apology("Must provide a new password", 400)
        
        if request.form.get("password") != request.form.get("confirmation"):
            flash("Passwords do not match !!!")
            return render_template("reset_password.html", token=token)
        
        # Update the user's password
        hashed_password = generate_password_hash(new_password)
        db.execute("UPDATE users SET hash = ?, token = NULL WHERE id = ?", hashed_password, user[0]["id"])
        
        flash("Your password has been reset. Please log in.")
        return render_template("login.html")
    
    return render_template("reset_password.html", token=token, profile = user[0])

@main.route("/changepass", methods=["GET", "POST"])
@login_required
def change_pass():
    user_id = session.get('user_id')
    profile = db.execute("SELECT * FROM users WHERE id = ?", user_id)[0]
    if request.method == "POST":
        if not request.form.get("currentpass"):
            flash("You need to provide current password !")
            return redirect("/changepass")
        if not request.form.get("newpassword"):
            flash("You need to provide new password !")
            return redirect("/changepass")

        rows = db.execute("SELECT * FROM users WHERE id = ?", user_id)
        if not check_password_hash(rows[0]["hash"], request.form.get("currentpass")):
            flash("Invalid Current Password !!!")
            return redirect("/changepass")
        
        if request.form.get("newpassword") != request.form.get("confirmation"):
            flash("New and Confirmation Passwords do not match !!!")
            return redirect("/changepass")
        
        hashed_password = generate_password_hash(request.form.get("newpassword"))
        db.execute("UPDATE users SET hash = ?, token = NULL WHERE id = ?", hashed_password, user_id)
        
        flash("Password Updated Successfully")
        return redirect("/profile")

    else:
        return render_template("changepass.html", profile = profile)
