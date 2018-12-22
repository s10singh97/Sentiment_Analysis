from flask import Flask, flash, redirect, render_template, request, session, url_for, send_file
from flask_session import Session
from passlib.apps import custom_app_context as pwd_context
from cs50 import SQL
from tempfile import gettempdir

import helpers
import sys
from helpers import *
from analyzer import Analyzer

# configure application
app = Flask(__name__)

# ensure responses aren't cached
if app.config["DEBUG"]:
    @app.after_request
    def after_request(response):
        response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
        response.headers["Expires"] = 0
        response.headers["Pragma"] = "no-cache"
        return response

# configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = gettempdir()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# configure CS50 Library to use SQLite database
db = SQL("sqlite:///sentiments.db")

@app.route("/")
@login_required
def index():
    """Index Page"""

    return render_template("index.html")


@app.route("/search")
@login_required
def search():
    """Analyze the Twitter Handle"""

    # validate screen_name
    screen_name = request.args.get("screen_name", "")
    if not screen_name:
        return redirect(url_for("index"))

    # get screen_name's tweets
    tweets, photo = helpers.get_user_timeline(screen_name, 200)
    tweets1 = tweets[0:99]
    tweets2 = tweets[100:199]

    if tweets == None:
        return redirect(url_for("index"))

    positive, negative, neutral = 0.0, 0.0, 100.0
    analyzer = Analyzer(positive, negative)
    for tweet in tweets1:
        c = analyzer.analyze(tweet)
        if c > 0:
            positive += 1
            neutral -= 1
        elif c < 0:
            negative += 1
            neutral -= 1


    positive2, negative2, neutral2 = 0.0, 0.0, 100.0
    analyzer2 = Analyzer(positive, negative)
    for tweet in tweets2:
        c2 = analyzer2.analyze(tweet)
        if c2 > 0:
            positive2 += 1
            neutral2 -= 1
        elif c2 < 0:
            negative2 += 1
            neutral2 -= 1

    if positive2 < positive:
        # Insert data into histories table
        db.execute("INSERT INTO histories (id, screenname, positive, negative, neutral, flag) \
                        VALUES(:id, :screenname, :positive, :negative, :neutral, :flag)", \
                        screenname=screen_name, positive=positive, negative=negative, \
                        neutral=neutral, id=session["user_id"], flag="static/pos.png")

    elif positive2 > positive:
        # Insert data into histories table
        db.execute("INSERT INTO histories (id, screenname, positive, negative, neutral, flag) \
                        VALUES(:id, :screenname, :positive, :negative, :neutral, :flag)", \
                        screenname=screen_name, positive=positive, negative=negative, \
                        neutral=neutral, id=session["user_id"], flag="static/neg.png")

    else:
       # Insert data into histories table
        db.execute("INSERT INTO histories (id, screenname, positive, negative, neutral, flag) \
                        VALUES(:id, :screenname, :positive, :negative, :neutral, :flag)", \
                        screenname=screen_name, positive=positive, negative=negative, \
                        neutral=neutral, id=session["user_id"], flag="static/neu.png")

    # generate chart
    chart = helpers.chart(positive, negative, neutral)

    

    # render results
    return render_template("search.html", chart=chart, screen_name=screen_name, photo=photo)


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in."""

    # forget any user_id
    session.clear()

    # if user reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # ensure username was submitted
        if not request.form.get("username"):
            return apology("Must provide username")

        # ensure password was submitted
        elif not request.form.get("password"):
            return apology("Must provide password")

        # query database for username
        rows = db.execute("SELECT * FROM users \
                           WHERE username = :username", \
                           username=request.form.get("username"))

        # ensure username exists and password is correct
        if len(rows) != 1 or not pwd_context.verify(request.form.get("password"), rows[0]["hash"]):
            return apology("invalid username and/or password")

        # remember which user has logged in
        session["user_id"] = rows[0]["id"]

        flash("Login Successful!!", category="success")
        # redirect user to home page
        return redirect(url_for("index"))

    # else if user reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out."""

    # forget any user_id
    session.clear()

    # redirect user to login form
    return redirect(url_for("login"))


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user."""
    
    if request.method == "POST":
        
        # ensure username was submitted
        if not request.form.get("username"):
            return apology("Must provide username")
            
        # ensure password was submitted    
        elif not request.form.get("password"):
            return apology("Must provide password")
        
        # ensure password and verified password is the same
        elif request.form.get("password") != request.form.get("passwordagain"):
            return apology("password doesn't match")
        
        # insert the new user into users, storing the hash of the user's password
        result = db.execute("INSERT INTO users (username, hash) \
                             VALUES(:username, :hash)", \
                             username=request.form.get("username"), \
                             hash=pwd_context.hash(request.form.get("password")))
                 
        if not result:
            return apology("Username already exist")
        
        # remember which user has logged in
        session["user_id"] = result

        flash("Registered!")
        # redirect user to home page
        return redirect(url_for("index"))
    
    else:
        return render_template("register.html")


@app.route("/passwordchange", methods=["GET", "POST"])
@login_required
def passwordchange():
    """Password Change"""

    if request.method == "POST":

        # ensure password was submitted
        if not request.form.get("password"):
            return apology("Must provide password")

        # ensure new password was submitted
        elif not request.form.get("newpassword"):
            return apology("Must provide new password")
        # ensure password and verified password is the same
        elif request.form.get("newpassword") != request.form.get("newpasswordretype"):
            return apology("password doesn't match")

        db.execute("UPDATE users SET hash=:hash WHERE id=:id", \
                hash=pwd_context.hash(request.form.get("newpassword")), id=session["user_id"])

        flash("Changed!")

        return redirect(url_for("index"))

    else:
        return render_template("passwordchange.html")


@app.route("/history")
@login_required
def history():
    """Show history of search results."""
    
    histories = db.execute("SELECT * from histories WHERE id=:id", id=session["user_id"])
    
    return render_template("history.html", histories=histories)


@app.route("/emojiinitial")
@login_required
def emojiinitial():
    """Initial Word Checker Page"""

    return render_template("emojiinitial.html")


@app.route("/emojis")
@login_required
def emojis():
    """Individual word checking tool"""

    # ensure a word was entered
    if not request.args.get("word"):
        return apology("Must provide word")

    # absolute paths to lists
    positives = os.path.join(sys.path[0], "positive-words.txt")
    negatives = os.path.join(sys.path[0], "negative-words.txt")

    # instantiate analyzer
    analyzer = Analyzer(positives, negatives)

    # analyze word
    score = analyzer.analyze(request.args.get("word"))

    return render_template("emojis.html", status=score)