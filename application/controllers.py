from flask import redirect, render_template, request, url_for, flash, session
from flask import current_app as app
from application.models import *
from application.forms import RegistrationForm, LoginForm
from application.database import db
import datetime
import matplotlib.pyplot as plt



#---------------------------INDEX AND LOGIN-------------------------------#

@app.route("/", methods=["GET","POST"])
def index():
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


#---------------------------REGISTRATION-------------------------------#

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


#---------------------------DASHBOARD-------------------------------#

@app.route("/dashboard/<int:userid>")
def dashboard(userid):
    if "user" not in session:
        return redirect(url_for("index"))
    user = User.query.filter_by(userid=session["user"]).first()
    trackers = Tracker.query.filter_by(userid=userid).all()
    #print(trackers)
    return render_template('dashboard.html', title="Dashboard", username=user.fname, userid=userid, trackers=trackers)


#---------------------------TRACKER TYPES-------------------------------#
tracker_type = ["Numeric", "Muliple Choice", "Boolean"] 


#---------------------------CREATE TRACKER-------------------------------#

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


#---------------------------MULTIPLE CHOICES FOR MCQ-TRACKER-------------------------------#

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


#---------------------------UPDATE TRACKER-------------------------------#

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


#---------------------------DELETE TRACKER-------------------------------#

@app.route("/dashboard/delete/<int:trackerid>", methods=["GET","POST"])
def tracker_delete(trackerid):
    if "user" not in session:
        return redirect(url_for("index"))
    
    tracker = Tracker.query.filter_by(trackerid=trackerid).first()
    db.session.delete(tracker)
    db.session.commit()

    return redirect(url_for('dashboard', userid=session["user"]))


#---------------------------ADD LOG-------------------------------#

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

        if tracker.type == "Muliple Choice":
            log = Logs(trackerid=trackerid, value=request.form["choice"], note=request.form["note"], datetime=date_time)
            db.session.add(log)
            db.session.commit()

        if tracker.type == "Boolean":
            log = Logs(trackerid=trackerid, value=request.form["choice"], note=request.form["note"], datetime=date_time)
            db.session.add(log)
            db.session.commit()

        return redirect(url_for('dashboard', userid=session["user"]))


#---------------------------TRACKER WITH LOGS AND GRAPHS-------------------------------#

@app.route("/dashboard/tracker/<int:trackerid>", methods=["GET","POST"])
def trackers(trackerid):
    if "user" not in session:
        return redirect(url_for("index"))
    
    logs = Logs.query.filter_by(trackerid=trackerid).order_by(Logs.datetime).all()
    tracker = Tracker.query.filter_by(trackerid=trackerid).first()  

    if tracker.type == "Numeric":
        x,y,data = [],[],{}

        for i in range(0,len(logs)):
            #x.append(str(logs[i].datetime)[0:16])
            #y.append(float(logs[i].value))
            data[str(logs[i].datetime)[0:16]] = float(logs[i].value)
        sorted_data = dict(sorted(data.items()))

        #print(data, sorted_data)

        x = list(sorted_data.keys())
        y = list(sorted_data.values())

        plt.clf()
        #ax = plt.axes()
        #ax.set_facecolor('silver')
        plt.style.use('_classic_test_patch')
        plt.xlabel('Date-Time')
        plt.ylabel('Value')
        plt.title("Trend Line")
        plt.plot(x, y, color ='#1B6E2D', marker = 'D', ms = 6, mfc = 'hotpink')
        plt.grid(axis='y', linestyle = '--')
        plt.gcf().autofmt_xdate()
        plt.tight_layout()
        plt.savefig('static/graph.png', transparent=True)
    
    if tracker.type == "Muliple Choice":
        data = {}
        for i in range(0,len(logs)):
            if logs[i].value in data.keys():
                data[logs[i].value] += 1
            else:
                data[logs[i].value] = 1
        #print(data,x)
        labels = list(data.keys())
        sizes = list(data.values())

        plt.clf()
        plt.style.use('_classic_test_patch')
        plt.title("Share Pie")
        plt.pie(sizes, labels=labels, autopct='%1.1i%%')
        plt.savefig('static/graph.png', transparent=True)

    if tracker.type == "Boolean":
        data = {}
        for i in range(0,len(logs)):
            if logs[i].value in data.keys():
                data[logs[i].value] += 1
            else:
                data[logs[i].value] = 1
        
        labels = list(data.keys())
        sizes = list(data.values())
        plt.clf()
        plt.bar(range(len(data)), sizes, tick_label=labels)
        plt.grid(axis='y', linestyle = '--')
        plt.title("BARified progress")
        plt.ylabel('Count')
        plt.savefig('static/graph.png', transparent=True)

    return render_template("tracker_log.html", logs=logs, userid=session["user"],tracker=tracker, username=session["username"], title="Tracker Logs")


#---------------------------UPDATE LOGS-------------------------------#

@app.route("/dashboard/log_update/<int:logid>", methods=["GET","POST"])
def log_update(logid):
    if "user" not in session:
        return redirect(url_for("index"))
    

    log = Logs.query.filter_by(logid=logid).first()
    tracker = Tracker.query.filter_by(trackerid=log.trackerid).first()  
    dt = str(log.datetime)
    date_time = dt[0:10]+"T"+dt[11:16]


    if request.method == "GET":

        if tracker.type == "Numeric":
            return render_template('update_numeric.html', title="LOG update", userid=session["user"], username=session["username"], log=log, date_time=date_time)

        if tracker.type == "Muliple Choice":
            mcqs = MultipleChoice.query.filter_by(trackerid=log.trackerid).all()
            return render_template('update_mcq.html', title="LOG update", userid=session["user"], username=session["username"], log=log, trackername=tracker.trackername, mcqs=mcqs, date_time=date_time)

        if tracker.type == "Boolean":
            return render_template('update_boolean.html', title="LOG update", userid=session["user"], username=session["username"], log=log, trackername=tracker.trackername, date_time=date_time)

    if request.method == "POST":

        date_time = datetime.datetime.strptime(request.form["datetime"], "%Y-%m-%dT%H:%M")

        if tracker.type == "Numeric":
            log.datetime = date_time
            log.value = request.form["value"]
            log.note = request.form["note"]
            db.session.commit()

        if tracker.type == "Muliple Choice":
            log.datetime = date_time
            log.value = request.form["choice"]
            log.note = request.form["note"]
            db.session.commit()

        if tracker.type == "Boolean":
            log.datetime = date_time
            log.value = request.form["choice"]
            log.note = request.form["note"]
            db.session.commit()
        
        return redirect(url_for("trackers", trackerid=log.trackerid))


#---------------------------DELETE LOGS-------------------------------#

@app.route("/dashboard/log_delete/<int:logid>", methods=["GET","POST"])
def log_delete(logid):
    if "user" not in session:
        return redirect(url_for("index"))
    
    log = Logs.query.filter_by(logid=logid).first()
    db.session.delete(log)
    db.session.commit()

    return redirect(url_for('dashboard', userid=session["user"]))


#---------------------------LOGOUT-------------------------------#

@app.route("/logout")
def logout():
    session.pop("user", None)
    session.pop("username", None)
    return redirect(url_for("index"))