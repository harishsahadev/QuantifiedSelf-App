from flask import redirect, render_template, request, url_for, flash
from flask import current_app as app
from application.models import User, Tracker_type, Tracker
from application.forms import RegistrationForm, LoginForm
from application.database import db


@app.route("/")
def index():
    # Front Page
    return render_template('index.html', title = 'About')

@app.route("/register", methods=["GET","POST"])
def register():
    error = None
    form = RegistrationForm()
    if request.method == "GET":
        return render_template('register.html', title="Register", form=form)

    if request.method == "POST":
        username = request.form["username"]
        print(username)
        #Check for existing user
        user = User.query.filter_by(username=username).first()
        if user != None:
            flash('Try a different Username', category='danger')
            return render_template('register.html', title="Register", form=form)


        user = User(username=username, password=request.form["password"], fname=request.form["fname"], lname=request.form["lname"])
        db.session.add(user)
        db.session.commit()
        #if form.validate_on_submit():
          #  flash(f'{form.username.data}, successfully Registered!', 'success')
        return redirect(url_for("index"))

@app.route("/dashboard/<int:user>")
def dashboard():
    return render_template('dashboard.html')