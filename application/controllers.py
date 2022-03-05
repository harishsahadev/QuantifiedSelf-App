from flask import render_template, request
from flask_bootstrap import Bootstrap

from flask import current_app as app
from application.models import User, Tracker_type, Tracker

@app.route("/")
def index():
    return render_template('index.html')

@app.route("/login")
def login():
    return render_template('login.html')

@app.route("/signup")
def signup():
    return render_template('signup.html')

@app.route("/dashboard")
def dashboard():
    return render_template('dashboard.html')