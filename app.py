import os

from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import datetime

from helpers import apology, login_required, lookup, usd

# Configure application
app = Flask(__name__)

# Custom filter
app.jinja_env.filters["usd"] = usd

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///finance.db")


@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


@app.route("/")
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
    return render_template("index.html", shares=shares, totalSharesAmt = cashBal[0]["cash"], grandTotl=grandTotl, profile=profile[0]['username'])


@app.route("/buy", methods=["GET", "POST"])
@login_required
def buy():

    profile = db.execute("SELECT * FROM users WHERE id = ?", session.get('user_id'))

    """Buy shares of stock"""
    profile = db.execute(
                "SELECT * FROM users WHERE id = ?", session.get('user_id')
            )
    if request.method == "POST":
        if not request.form.get("symbol"):
            return apology("Must provide symbol")
        if not request.form.get("shares"):
            return apology("Must provide shares")
        # Check user input
        symbolvalue = lookup(request.form.get("symbol"))
        if symbolvalue is None:
            return apology("That symbol " + request.form.get("symbol") + " doesn't exit")

        symbPrice = symbolvalue['price']
        try:
            numShares = float(request.form.get("shares"))
        except ValueError:
            return apology("Please provide a number")
        if int(numShares) < 1:
            return apology("Provide the value grater than zero")
        if numShares != int(numShares):
            return apology("Provide the integer value")
        if not isinstance(numShares, (int, float)):
            return apology("Provide the integer value")

        Symb = symbolvalue['symbol']
        # print(Symb)
        # print(symbPrice)
        # print(numShares)
        # print("User Id : {}".format(session.get('user_id')))

        # get the user balance
        user = db.execute(
            "SELECT * FROM users WHERE id = ?", session.get('user_id')
        )

        usrBal = user[0]["cash"]
        sharesCost = int(numShares) * symbPrice

        # check user has enough balance
        if sharesCost < usrBal:
            # update user balance
            db.execute(
                "UPDATE users SET cash = ? where id = ?", (usrBal - sharesCost), session.get('user_id')
            )

            db.execute(
                "INSERT INTO history (user_id, symbol, shares, price, transacted) VALUES (?,?,?,?,?)", session.get('user_id'), Symb, numShares, sharesCost, datetime.now()
            )

            shares = db.execute(
                "SELECT * FROM shares WHERE user_id = ? and symbol = ?", session.get('user_id'), Symb
            )

            if len(shares) != 1:
                db.execute(
                    "INSERT INTO shares (user_id,symbol,shares) VALUES (?,?,?)", session.get('user_id'), Symb, numShares
                )
            else:
                db.execute(
                    "UPDATE shares SET shares = ? WHERE user_id = ? AND symbol = ?", shares[0]['shares'] + int(numShares), session.get('user_id'), Symb
                )

        elif sharesCost > usrBal:
            return apology("You don't have enough cash")

        # return render_template("quoted.html", valUsd=valUsd, valSymb=valSymb)
        return redirect("/")

    else:
        return render_template("buypage.html", profile=profile[0]['username'])


@app.route("/history")
@login_required
def history():
    """Show history of transactions"""
    history = db.execute(
                "SELECT * FROM history WHERE user_id = ?", session.get('user_id')
            )
    profile = db.execute("SELECT * FROM users WHERE id = ?", session.get('user_id'))
    return render_template("history.html", history=history, profile=profile[0]['username'])

@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username")

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password")

        elif not request.form.get("password"):
            return apology("must provide confirmed password")

        # Query database for username
        rows = db.execute(
            "SELECT * FROM users WHERE username = ?", request.form.get("username")
        )

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(
            rows[0]["hash"], request.form.get("password")
        ):
            return apology("invalid username and/or password")

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        flash("Login successful")
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


@app.route("/quote", methods=["GET", "POST"])
@login_required
def quote():
    profile = db.execute("SELECT * FROM users WHERE id = ?", session.get('user_id'))

    """Get stock quote."""
    if request.method == "POST":
        if not request.form.get("symbol"):
            return apology("Must provide symbol")

        symbolvalue = lookup(request.form.get("symbol"))
        if symbolvalue is None:
            return apology("That symbol " + request.form.get("symbol") + " doesn't exit")
        print(symbolvalue)
        valUsd = usd(symbolvalue['price'])
        print(valUsd)
        valSymb = symbolvalue['symbol']
        print(valSymb)
        return render_template("quoted.html", valUsd=valUsd, valSymb=valSymb)

    else:
        return render_template("quote.html", profile=profile[0]['username'])


@app.route("/register", methods=["GET", "POST"])
def register():

    """Register user"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username")

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 400)

        elif request.form.get("password") != request.form.get("confirmation"):
            return apology("passwords do not match", 400)

        usrpwd = request.form.get("password")
        usrpwdHash = generate_password_hash(usrpwd)

        # Query database for username
        rows = db.execute(
            "SELECT * FROM users WHERE username = ?", request.form.get(
                "username")
        )

        # Ensure username exists and password is correct
        if len(rows) != 1:
            db.execute(
                "INSERT INTO users (username, hash) VALUES (?,?)", request.form.get("username"), usrpwdHash
            )
        else:
            print("debug")
            print(rows)
            print("debug")
            return apology("User " + rows[0]['username'] + " already exist")

        # Query database for username

        user = db.execute(
            "SELECT * FROM users WHERE username = ?", request.form.get("username")
        )

        # Remember which user has logged in
        session["user_id"] = user[0]["id"]

        # Redirect user to login page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("register.html")


@app.route("/sell", methods=["GET", "POST"])
@login_required
def sell():

    profile = db.execute("SELECT * FROM users WHERE id = ?", session.get('user_id'))

    """Sell shares of stock"""
    if request.method == "POST":
        if not request.form.get("symbol"):
            return apology("Select a symbol plz!!")
        if not request.form.get("shares"):
            return apology("Fill the number of shares!")

        # get the user balance
        user = db.execute(
            "SELECT * FROM users WHERE id = ?", session.get('user_id')
        )

        usrBal = user[0]["cash"]

        numShares   = int(request.form.get("shares"))
        symbolvalue = lookup(request.form.get("symbol"))
        symbPrice   = symbolvalue['price']
        Symb        = symbolvalue['symbol']
        sharesCost  = float(numShares) * symbPrice

        shares = db.execute(
            "SELECT shares FROM shares WHERE user_id = ? and symbol = ?", session.get('user_id'), Symb
        )

        if shares[0]['shares'] < numShares:
            return apology("You don't have that much shares")

        db.execute(
            "UPDATE users SET cash = ? where id = ?", (usrBal + sharesCost), session.get('user_id')
        )

        db.execute(
            "UPDATE shares SET shares = ? WHERE user_id = ? AND symbol = ?", shares[0]['shares'] - int(numShares), session.get('user_id'), Symb
        )

        db.execute(
            "INSERT INTO history (user_id, symbol, shares, price, transacted) VALUES (?,?,?,?,?)", session.get('user_id'), Symb, -numShares, sharesCost, datetime.now()
        )




        flash("Congratuation! your sell out successful")
        return redirect("/")

    else:

        usrid = session.get('user_id')

        symbols = db.execute(
            "SELECT symbol FROM shares WHERE user_id = ?", usrid
        )


        return render_template("sell.html", symbols=symbols, profile=profile[0]['username'])


@app.route("/profile")
@login_required
def profile():
    return apology("Working in progress", 400)
