from flask import redirect, render_template, request, url_for, flash, session
from flask import current_app as app
from application.models import *
from application.forms import RegistrationForm, LoginForm
from application.database import db
import datetime


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
            session["username"] = user.username
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
    #print(trackers)
    return render_template('dashboard.html', title="Dashboard", username=user.fname, userid=userid, trackers=trackers)


tracker_type = ["Numeric", "Muliple Choice", "Time Duration", "Boolean"]

@app.route("/dashboard/create", methods=["GET","POST"])
def create_tracker():
    if "user" not in session:
        return redirect(url_for("index"))
    user = User.query.filter_by(userid=session["user"]).first()
    
    if request.method == "POST":
        tracker = Tracker.query.filter_by(trackername=request.form["name"], userid=session["user"] ).first()
        if tracker != None:
            flash('Tracker Already Exist!', category='danger')
        else:
            tracker = Tracker(trackername=request.form["name"], description=request.form["description"], type=request.form.get('tracker_type'), userid=session["user"])
            db.session.add(tracker)
            db.session.commit()

            if tracker_type[1] == request.form.get('tracker_type'):
                tracker = Tracker.query.filter_by(trackername=request.form["name"], userid=session["user"] ).first()
                print(tracker)
                return redirect(url_for('multiple_choice', trackerid=tracker.trackerid))
        #print(session["user"])
        return redirect(url_for('dashboard', userid=session["user"]))

    return render_template('create_tracker.html', title="Create Tracker",userid=session["user"], username=user.fname, tracker_type=tracker_type)


@app.route("/dashboard/create/multiple_choice/<int:trackerid>", methods=["GET","POST"])
def multiple_choice(trackerid):
    if "user" not in session:
        return redirect(url_for("index"))
    user = User.query.filter_by(userid=session["user"]).first()

    if request.method == "POST":
        choices = request.form["choices"].split(",")
        for item in choices:
            mcq = MultipleChoice(trackerid=trackerid, choices=item)
            db.session.add(mcq)
            db.session.commit()

        return redirect(url_for('dashboard', userid=session["user"]))

    return render_template('multiple_choice.html', title="Create Tracker", username=user.fname, trackerid=trackerid)


@app.route("/dashboard/update/<int:trackerid>", methods=["GET","POST"])
def tracker_update(trackerid):
    if "user" not in session:
        return redirect(url_for("index"))
    
    tracker = Tracker.query.filter_by(trackerid=trackerid).first()
    #print(tracker.description)

    if request.method == "POST":
        trackercheck = Tracker.query.filter_by(trackername=request.form["name"], userid=session["user"] ).first()
        if (trackercheck != None) and (tracker.trackername != request.form["name"]):
            flash('Tracker Already Exist!', category='danger')
        else:
            tracker.trackername = request.form["name"]
            tracker.description = request.form["description"]
            db.session.commit()

        return redirect(url_for('dashboard', userid=session["user"]))

    return render_template("tracker_update.html", userid=session["user"], username=session["username"], title="Update Tracker", tracker=tracker)


@app.route("/dashboard/delete/<int:trackerid>", methods=["GET","POST"])
def tracker_delete(trackerid):
    if "user" not in session:
        return redirect(url_for("index"))
    
    tracker = Tracker.query.filter_by(trackerid=trackerid).first()
    db.session.delete(tracker)
    db.session.commit()

    return redirect(url_for('dashboard', userid=session["user"]))


@app.route("/dashboard/logs/<int:trackerid>", methods=["GET","POST"])
def logs(trackerid):
    if "user" not in session:
        return redirect(url_for("index"))

    user = User.query.filter_by(userid=session["user"]).first()
    tracker = Tracker.query.filter_by(trackerid=trackerid).first()    
    time_now = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M")

    if request.method == "GET":

        if tracker.type == "Numeric":
            return render_template('logs_numeric.html', title="LOG", userid=session["user"], username=user.fname, trackerid=trackerid, time_now=time_now)

        if tracker.type == "Muliple Choice":
            mcqs = MultipleChoice.query.filter_by(trackerid=trackerid).all()
            return render_template('logs_mcq.html', title="LOG", userid=session["user"], username=user.fname, trackerid=trackerid, time_now=time_now, mcqs=mcqs, trackername=tracker.trackername)

        if tracker.type == "Boolean":
            return render_template('logs_boolean.html', title="LOG", userid=session["user"], username=user.fname, trackerid=trackerid, time_now=time_now, trackername=tracker.trackername)

        if tracker.type == "Time Duration":
            pass

    if request.method == "POST":

        date_time = datetime.datetime.strptime(request.form["datetime"], "%Y-%m-%dT%H:%M")
        tracker.lastseen = date_time

        if tracker.type == "Numeric":
            log = Logs(trackerid=trackerid, value=request.form["value"], note=request.form["note"], datetime=date_time)
            db.session.add(log)
            db.session.commit()
            return redirect(url_for('dashboard', userid=session["user"]))

        if tracker.type == "Muliple Choice":
            log = Logs(trackerid=trackerid, value=request.form["choice"], note=request.form["note"], datetime=date_time)
            db.session.add(log)
            db.session.commit()
            return redirect(url_for('dashboard', userid=session["user"]))

        if tracker.type == "Boolean":
            log = Logs(trackerid=trackerid, value=request.form["choice"], note=request.form["note"], datetime=date_time)
            db.session.add(log)
            db.session.commit()
            return redirect(url_for('dashboard', userid=session["user"]))

        if tracker.type == "Time Duration":

            pass

        

        return redirect(url_for('dashboard', userid=session["user"]))

@app.route("/dashboard/tracker/<int:trackerid>", methods=["GET","POST"])
def trackers(trackerid):
    if "user" not in session:
        return redirect(url_for("index"))
    
    return "<h1>Work in Progress</h1>"





@app.route("/logout")
def logout():
    session.pop("user", None)
    session.pop("username", None)
    return redirect(url_for("index"))