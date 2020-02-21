# blog.py - Controller

# imports
from flask import Flask
from flask import render_template
from flask import request
from flask import session
from flask import flash
from flask import redirect
from flask import url_for
from flask import g
import sqlite3
from functools import wraps

# Configuration

DATABASE = "blog.db"
USERNAME = "admin"
PASSWORD = "admin"
SECRET_KEY = "hard_to_guess"

app = Flask(__name__)

# Pulls in app configuration by looking for UPPERCASE variables
app.config.from_object(__name__)

# Function used for connecting to the database
def connect_db():
    return sqlite3.connect(app.config['DATABASE'])

def login_required(test):
    @wraps(test)
    def wrap(*args, **kwargs):
        if "logged_in" in session:
            return test(*args, **kwargs)
        else:
            flash("You need to log in first.")
            return redirect(url_for("login"))
    return wrap

@app.route("/", methods=["GET", "POST"])
def login():
    error = None
    status_code = 200
    if request.method == "POST":
        if request.form["username"] != app.config["USERNAME"] or \
                request.form["password"] != app.config["PASSWORD"]:
            error = " Invalid Credentials. Please try again."
            status_code = 401
        else:
            session['logged_in'] = True
            return redirect(url_for('main'))

    return render_template("login.html", error=error), status_code

@app.route("/main")
@login_required
def main():
    g.db = connect_db()
    cur = g.db.execute("SELECT * FROM posts")
    posts = [dict(title=row[0], post=row[1]) for row in cur.fetchall()]
    g.db.close()
    return render_template("main.html", posts=posts)

@app.route("/logout")
def logout():
    session.pop("logged_in", None)
    flash("You were logged out")
    return redirect(url_for("login"))

@app.route("/add", methods=["POST"])
@login_required
def add():
    title = request.form["title"]
    post = request.form["post"]
    if not title or not post:
        flash("All fields are required. Please try again.")
        return redirect(url_for("main"))
    else:
        g.db = connect_db()
        g.db.execute("INSERT INTO posts (title, post) VALUES (?, ?)",
            [request.form["title"], request.form["post"]])
        g.db.commit()
        g.db.close()
        flash ("New entry was succesfully added")
        return redirect(url_for("main"))



if __name__ == "__main__":
    app.run(debug=True)
