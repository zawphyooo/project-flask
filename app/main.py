from flask import Blueprint, render_template, request, session, redirect, flash
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
        if not request.form.get("username"):
            return apology("must provide username")
        if not request.form.get("password"):
            return apology("must provide password")

        rows = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return apology("invalid username and/or password")

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
        if not request.form.get("password"):
            return apology("must provide password", 400)
        if request.form.get("password") != request.form.get("confirmation"):
            return apology("passwords do not match", 400)

        usrpwd = request.form.get("password")
        usrpwdHash = generate_password_hash(usrpwd)

        rows = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))
        if len(rows) != 1:
            db.execute("INSERT INTO users (username, hash) VALUES (?, ?)", request.form.get("username"), usrpwdHash)
        else:
            return apology("User " + rows[0]['username'] + " already exists")

        user = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))
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

@main.route("/profile")
@login_required
def profile():
    return apology("Work in progress", 400)
