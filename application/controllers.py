from flask import redirect, render_template, request, url_for, flash
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
        if (user == None) or (user.password != request.form["password"]):
            flash("Login unsuccessful! Please check username or password.", category='danger')
            return render_template('login.html', title="Login", form=form)
        else:
            return redirect(url_for('dashboard', userid=user.userid))
  
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
def dashboard():
    return render_template('dashboard.html')