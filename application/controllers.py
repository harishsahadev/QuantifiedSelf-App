from flask import redirect, render_template, request, url_for, flash, session
from flask import current_app as app
from application.models import *
from application.forms import RegistrationForm, LoginForm
from application.database import db


@app.route("/", methods=["GET","POST"])
def index():
    # Front Page and Login page
    form = LoginForm()

    if form.validate_on_submit():
        username = request.form["username"]
        user = User.query.filter_by(username=username).first()
        if (user == None) or (user.password != request.form["password"]):
            flash("Login unsuccessful! Please check username or password.", category='danger')
            return render_template('login.html', title="Login", form=form)
        else:
            session["user"] = user.userid
            return redirect(url_for('dashboard', userid=user.userid))
    
    if "user" in session:
        return redirect(url_for("dashboard", userid=session["user"]))
    return render_template('login.html', title = 'Login', form=form)

@app.route("/register", methods=["GET","POST"])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        username = request.form["username"]
        print(username)
        #Check for existing user
        user = User.query.filter_by(username=username).first()
        if user != None:
            flash('Try a different Username', category='danger')
        else:
            user = User(username=username, password=request.form["password"], fname=request.form["fname"], lname=request.form["lname"])
            db.session.add(user)
            db.session.commit()
            flash('Registration Successful! Welcome to Quantified Self', category='success')
            return redirect(url_for("index"))
    return render_template('register.html', title="Register", form=form)


@app.route("/dashboard/<int:userid>")
def dashboard(userid):
    if "user" not in session:
        return redirect(url_for("index"))
    user = User.query.filter_by(userid=session["user"]).first()
    trackers = Tracker.query.filter_by(userid=userid).all()
    print(trackers)
    return render_template('dashboard.html', title="Dashboard", username=user.fname, userid=userid, trackers=trackers)

tracker_type = ["Numeric", "Muliple Choice", "Time Duration", "Boolean"]

@app.route("/dashboard/create", methods=["GET","POST"])
def create_tracker():
    if "user" not in session:
        return redirect(url_for("index"))
    user = User.query.filter_by(userid=session["user"]).first()
    
    if request.method == "POST":
        tracker = Tracker.query.filter_by(userid=session["user"]).first()
        if tracker.trackername == request.form["name"]:
            flash('Tracker Already Exist!', category='danger')
        else:
            tracker = Tracker(trackername=request.form["name"], description=request.form["description"], type=request.form.get('tracker_type'), userid=session["user"])
            db.session.add(tracker)
            db.session.commit()

            if tracker_type[1] == request.form.get('tracker_type'):
                return redirect(url_for('multiple_choice'))
        #print(session["user"])
        return redirect(url_for('dashboard', userid=session["user"]))

    return render_template('create_tracker.html', title="Create Tracker", username=user.fname, tracker_type=tracker_type)

@app.route("/dashboard/multiple_choice", methods=["GET","POST"])
def multiple_choice():
    if "user" not in session:
        return redirect(url_for("index"))
    user = User.query.filter_by(userid=session["user"]).first()

    if request.method == "POST":
        tracker = Tracker.query.filter_by(userid=session["user"]).first()
        choices = request.form["choices"].split(",")
        for item in choices:
            mcq = MultipleChoice(trackerid=tracker.trackerid, choices=item)
            db.session.add(mcq)
            db.session.commit()

        return redirect(url_for('dashboard'), userid=session["user"])

    return render_template('multiple_choice.html', title="Create Tracker", username=user.fname)

@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect(url_for("index"))