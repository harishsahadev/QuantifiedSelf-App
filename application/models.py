from .database import db

class User(db.Model):
    __tablename__ = 'user'
    userid = db.Column(db.Integer, autoincrement=True, primary_key=True)
    username = db.Column(db.String, unique=True, nullable=False)
    password = db.Column(db.String, nullable=False)
    fname = db.Column(db.String, nullable=False)
    lname = db.Column(db.String)
    tracker = db.relationship('Tracker', cascade="all, delete") # one-to-many relationship with delete on cascade

#class Tracker_type(db.Model):
  #  __tablename__ = 'tracker_type'
  #  typeid = db.Column(db.Integer, autoincrement=True, primary_key=True)
  #  type = db.Column(db.String, unique=True, nullable=False)

class Tracker(db.Model):
    __tablename__ = 'tracker'
    trackerid = db.Column(db.Integer, autoincrement=True, primary_key=True)
    trackername = db.Column(db.String, unique=True, nullable=False)
    description = db.Column(db.String)
    type = db.Column(db.String, nullable=False)
    userid = db.Column(db.Integer, db.ForeignKey("user.userid"), nullable=False)

class MultipleChoice(db.Model):
    __tablename__ = 'multiple_choice'
    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    trackerid = db.Column(db.Integer, db.ForeignKey("tracker.trackerid"), nullable=False)
    choices = db.Column(db.String, nullable=False)
