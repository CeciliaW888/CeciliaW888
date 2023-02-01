import os

from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session, url_for
from flask_session import Session
from flask_bootstrap import Bootstrap
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Email, Length, URL
from flask_ckeditor import CKEditor, CKEditorField

from tempfile import mkdtemp
from werkzeug.security import check_password_hash, generate_password_hash
# import requests
from datetime import datetime


from helpers import apology, login_required, strip_invalid_html

# Configure application
app = Flask(__name__)
app.config['SECRET_KEY'] = "DoNotTellAnyone"
Bootstrap(app)
ckeditor = CKEditor(app)

# Make sure Flask secret key is set
# app.secret_key = os.environ.get("FLASK_SECRET_KEY")


# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///blog.db")


@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


# Create a login form
class LoginForm(FlaskForm):
    username = StringField(label='Username', validators=[DataRequired(), Length(min=4, max=15)])
    password = PasswordField(label='Password', validators=[DataRequired(), Length(min=3, max=80)])
    remember = BooleanField(label='Remember me')
    submit = SubmitField(label="Log In")


# Create a register form
class RegisterForm(FlaskForm):
    username =  StringField(label='Username', validators=[DataRequired(), Length(min=4, max=15)])
    password = PasswordField(label='Password', validators=[DataRequired(), Length(min=3, max=80)])
    confirm_password = PasswordField(label='Confirm password', validators=[DataRequired(), Length(min=3, max=80)])
    submit = SubmitField(label="Sign Up")


# Create a post form for writting/editing blog posts
class PostForm(FlaskForm):
    title =  StringField(label='Title', validators=[DataRequired()])
    subtitle = StringField(label='Subtitle', validators=[DataRequired()])
    img_url = StringField(label='Blog Image URL', validators=[DataRequired(), URL()])
    body = CKEditorField(label='Blog Content', validators=[DataRequired()])
    submit = SubmitField(label="Submit Post")


@app.route("/about")
@login_required
def about():
    return render_template("about.html")


@app.route("/contact", methods=["GET", "POST"])
@login_required
def contact():
    if request.method == "POST":
        return render_template("contact.html", msg_sent=True)
    else:
        return render_template("contact.html", msg_sent=False)


@app.route("/edit-post/<int:post_id>", methods=["GET", "POST"])
@login_required
def edit_post(post_id):
    post = db.execute("SELECT * FROM blogs WHERE id = ?", post_id)[0]
    edit_form = PostForm(
        title=post["title"],
        subtitle=post["subtitle"],
        img_url=post["img_url"],
        body=post["body"]
    )
    if edit_form.validate_on_submit():
        post["title"] = edit_form.title.data
        post["subtitle"] = edit_form.subtitle.data,
        post["img_url"] = edit_form.img_url.data
        # Strip off the html tags in the ckeditor textarea
        post["body"] = strip_invalid_html(edit_form.body.data)
        # Update database
        db.execute("UPDATE blogs SET title=?, subtitle=?, img_url=?, body=? WHERE id=?",  post["title"],  post["subtitle"],  post["img_url"], post["body"], post_id)
        flash("Post has been updated!")
        return redirect(url_for("show_post", post_id=post["id"]))

    return render_template("make-post.html", form=edit_form, is_edit=True)


@app.route("/delete/<int:post_id>")
def delete_post(post_id):
    db.execute("DELETE FROM blogs WHERE id = ?", post_id)
    return redirect("/")


@app.route("/")
@login_required
def index():
    """Show blog posts"""
    username = db.execute("SELECT username FROM users WHERE id = ?", session["user_id"])[0]["username"]
    posts = db.execute("SELECT * FROM blogs")
    return render_template("index.html", posts=posts, username=username)


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""
    # Forget any user_id
    session.clear()

    # Instantiate form
    form = LoginForm(meta={'csrf': False})

    # Validate the form
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = ?", username)

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], password):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        flash("You are logged in!")
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    return render_template("login.html", form=form)


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


@app.route("/new-post", methods=["GET", "POST"])
@login_required
def new_post():
    """Write new blog post."""
    form = PostForm()
    if form.validate_on_submit():
        username = db.execute("SELECT username FROM users WHERE id = ?", session["user_id"])[0]["username"]
        title=form.title.data,
        subtitle=form.subtitle.data,
        img_url=form.img_url.data,
        body=strip_invalid_html(form.body.data),
        date = datetime.today().strftime("%d %B, %Y")

        # Add post in the database
        db.execute("INSERT INTO blogs (user_name, title, subtitle, img_url, body, timestamp) VALUES(?, ?, ?, ?, ?, ?)", username, title, subtitle, img_url, body, date)
        # Redirect user to home page
        flash("You published a new post!")
        return redirect("/")

    else:
        return render_template("make-post.html", form=form)


@app.route("/register", methods=["GET", "POST"])
def register():
    """Sign up new user"""
    # Instantiate form
    form = RegisterForm()

    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        confirmation = form.confirm_password.data
        hash = generate_password_hash(password)
        # Ensure password matches the confirmation
        if password != confirmation:
            return apology("passwords don't match")

        # Insert the new user into users and store a hash of the password
        try:
            new_user = db.execute("INSERT INTO users (username, hash) VALUES (?, ?)", username, hash)
        except:
            # Ensure user doesn't exist
             return apology("username already exists")

        # Remember which user has logged in
        session["user_id"] = new_user

        # Redirect user to home page
        flash("You are signed up!")
        return redirect("/")

    return render_template("register.html", form=form)


@app.route("/post/<int:post_id>")
@login_required
def show_post(post_id):
    requested_post = db.execute("SELECT * FROM blogs WHERE id = ?", post_id)[0]
    return render_template("post.html", post=requested_post)





