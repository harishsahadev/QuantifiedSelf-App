from flask import redirect, render_template, request, url_for, flash, session
from flask import current_app as app
from application.models import User, Tracker_type, Tracker
from application.forms import RegistrationForm, LoginForm
from application.database import db


@app.route("/", methods=["GET","POST"])
def index():
    # Front Page and Login page
    form = LoginForm()

    if form.validate_on_submit():
        username = request.form["username"]
        user = User.query.filter_by(username=username).first()
        session["user"] = user.userid
        if (user == None) or (user.password != request.form["password"]):
            flash("Login unsuccessful! Please check username or password.", category='danger')
            return render_template('login.html', title="Login", form=form)
        else:
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
    user = User.query.filter_by(userid=userid).first()
    tracker = Tracker.query.filter_by(userid=userid).all()

    return render_template('dashboard.html', title="Dashboard", username=user.fname, userid=userid, tracker=tracker)

tracker_type = ["Numeric", "Muliple Choice", "Time Duration", "Boolean"]

@app.route("/dashboard/<int:userid>/create", methods=["GET","POST"])
def create_tracker(userid):
    if "user" not in session:
        return redirect(url_for("index"))
    user = User.query.filter_by(userid=userid).first()
    
    if request.method == "POST":
        type = request.form.get('tracker_type')
        if tracker_type[1] == type:
            return render_template("multiple_choice.html", title="Add choices", username=user.fname, userid=userid)

    return render_template('create_tracker.html', title="Create Tracker", username=user.fname, userid=userid, tracker_type=tracker_type)

@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect(url_for("index"))