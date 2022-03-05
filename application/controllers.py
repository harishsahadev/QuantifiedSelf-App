from flask import render_template, request

from flask import current_app as app
from application.models import User, Tracker_type, Tracker

@app.route("/")
def index():
    # Front Page
    return render_template('index.html', title = 'About')

@app.route("/register")
def signup():
    return render_template('register.html')

@app.route("/dashboard/<int:user>")
def dashboard():
    return render_template('dashboard.html')