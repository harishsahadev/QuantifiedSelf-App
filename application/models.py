from .database import db

class User(db.Model):
    __tablename__ = 'user'
    userid = db.Column(db.Integer, autoincrement=True, primary_key=True)
    username = db.Column(db.String, unique=True, nullable=False)
    password = db.Column(db.String, nullable=False)
    fname = db.Column(db.String, nullable=False)
    lname = db.Column(db.String)
    tracker = db.relationship('Tracker', cascade="all, delete") # one-to-many relationship with delete on cascade

class Tracker(db.Model):
    __tablename__ = 'tracker'
    trackerid = db.Column(db.Integer, autoincrement=True, primary_key=True)
    trackername = db.Column(db.String, nullable=False)
    description = db.Column(db.String)
    type = db.Column(db.String, nullable=False)
    userid = db.Column(db.Integer, db.ForeignKey("user.userid"), nullable=False)
    lastseen = db.Column(db.DateTime)
    mcq = db.relationship('MultipleChoice', cascade="all, delete")
    log = db.relationship('Logs', cascade="all, delete")

class MultipleChoice(db.Model):
    __tablename__ = 'multiple_choice'
    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    trackerid = db.Column(db.Integer, db.ForeignKey("tracker.trackerid"), nullable=False)
    choices = db.Column(db.String, nullable=False)

class Logs(db.Model):
    __tablename__ = 'logs'
    logid = db.Column(db.Integer, autoincrement=True, primary_key=True)
    trackerid = db.Column(db.Integer, db.ForeignKey("tracker.trackerid"), nullable=False)
    value = db.Column(db.String, nullable=False)
    note = db.Column(db.String)
    datetime = db.Column(db.DateTime, nullable=False)


#tracker_type = ["Numeric", "Muliple Choice", "Boolean"]