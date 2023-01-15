import os

from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.security import check_password_hash, generate_password_hash

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

# Make sure API key is set
if not os.environ.get("API_KEY"):
    raise RuntimeError("API_KEY not set")


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
    """Show portfolio of stocks"""
    user_id = session["user_id"]
    stocks = db.execute(
        "SELECT company_name, symbol, SUM(shares) as shares, price FROM transactions WHERE user_id = ? GROUP BY symbol", user_id)
    cash = db.execute("SELECT cash FROM users WHERE id = ?", user_id)[0]["cash"]

    # Keep tracking of total value
    total = cash
    for stock in stocks:
        current_price = lookup(stock["symbol"])["price"]
        total += current_price * stock["shares"]

    return render_template("index.html", stocks=stocks, cash=cash, total=total, usd=usd, lookup=lookup)


@app.route("/buy", methods=["GET", "POST"])
@login_required
def buy():
    """Buy shares of stock"""
    if request.method == "POST":
        user_id = session["user_id"]
        symbol = request.form.get("symbol").upper()
        stock = lookup(symbol)

        # Ensure symbol is entered
        if not symbol:
            return apology("must provide symbol")
        # Ensure symbol exist in the API response
        if not stock:
            return apology("symbol does not exist")

        # If stock exists, continue
        name = stock["name"]
        price = stock["price"]
        # Ensure shares are a positive interger
        try:
            shares = int(request.form.get("shares"))
        except:
            return apology("shares must be an interger")
        if shares <= 0:
            return apology("shares must be a positive whole number")

        # Check user balance
        cash = db.execute("SELECT cash FROM users WHERE id = ?", user_id)[0]["cash"]
        transaction_amount = shares * price

        # If the user cannot afford the number of shares at the current price
        if cash < transaction_amount:
            return apology("not enough balance")

        # If the transaction is successful, reduce the user balance
        cash -= transaction_amount

        # Update users table in SQL
        db.execute("UPDATE users SET cash = ? WHERE id = ?", cash, user_id)

        # Update transactions table in SQL
        db.execute("INSERT INTO transactions (user_id, company_name, symbol, shares, price, transaction_type) VALUES (?, ?, ?, ?, ?, ?)",
                   user_id, name, symbol, shares, price, 'Buy')

        # Provide message and redirect user to home page
        flash("Bought!")
        return redirect("/")

    # User reached route via GET
    else:
        return render_template("buy.html")


@app.route("/history")
@login_required
def history():
    """Show history of transactions"""
    user_id = session["user_id"]
    transactions = db.execute("SELECT symbol, shares, price, transaction_date FROM transactions WHERE user_id = ?", user_id)
    return render_template("history.html", transactions=transactions, usd=usd)


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
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
    """Get stock quote."""
    # User reached route via POST
    if request.method == "POST":
        symbol = request.form.get("symbol")
        # Ensure ticker is entered
        if not symbol:
            return apology("must provide the ticker")
        # Ensure ticker exist in the API response
        stock = lookup(symbol.upper())
        if not stock:
            return apology("ticker does not exist")
        company = stock["name"]
        price = usd(stock["price"])
        symbol = stock["symbol"]
        return render_template("quoted.html", company=company, price=price, symbol=symbol)

    # User reached route via GET
    else:
        return render_template("quote.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")

        # Ensure username is not blank
        if not username:
            return apology("must provide username")
        # Ensure password is not blank
        elif (not password) or (not confirmation):
            return apology("must provide password")
        # Ensure password matches the confirmation
        elif password != confirmation:
            return apology("passwords don't match")

        hash = generate_password_hash(password)
        # Insert the new user into users and store a hash of the password
        try:
            new_user = db.execute("INSERT INTO users (username, hash) VALUES (?, ?)", username, hash)
        except:
            # Ensure user doesn't exist
            return apology("username already exists")

        # Remember which user has logged in
        session["user_id"] = new_user

        # Provide message and redirect user to home page
        flash("Registered!")
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("register.html")


@app.route("/sell", methods=["GET", "POST"])
@login_required
def sell():
    """Sell shares of stock"""
    user_id = session["user_id"]
    if request.method == "POST":
        symbol = request.form.get("symbol")
        shares = int(request.form.get("shares"))
        stock = lookup(symbol)
        name = stock["name"]
        price = stock["price"]

        # If user fails to select a stock
        if not symbol:
            return apology("must select a symbol")
        # if the user does not own any shares of that stock
        user_shares = db.execute(
            "SELECT shares FROM transactions WHERE user_id = ? AND symbol = ? GROUP BY symbol", user_id, symbol)[0]["shares"]
        # if the user does not own any shares of that stock.
        if user_shares <= 0:
            return apology("you don't have any shares to sell")
        # If the input is not a positive integer
        if shares <= 0:
            return apology("must enter a positive interger")
        # If the user does not own that many shares of the stock.
        if shares > user_shares:
            return apology("not enough shares to sell")

        # Update user tale in SQL
        cash = db.execute("SELECT cash FROM users WHERE id = ?", user_id)[0]["cash"]
        transaction_amount = price * shares

        # If the transaction is successful, increase the user balance
        cash += transaction_amount

        # Update users table in SQL
        db.execute("UPDATE users SET cash = ? WHERE id = ?", cash, user_id)

        # Update transactions table in SQL
        db.execute("INSERT INTO transactions (user_id, company_name, symbol, shares, price, transaction_type) VALUES (?, ?, ?, ?, ?, ?)",
                   user_id, name, symbol, -shares, price, 'sell')

        # Provide message and redirect user to home page
        flash("Sold")
        return redirect("/")

    # User reached route via GET
    else:
        stocks = db.execute("SELECT symbol, SUM(shares) as shares FROM transactions WHERE user_id = ? GROUP BY symbol", user_id)
        # Generate options for the select menu
        return render_template("sell.html", stocks=stocks)
