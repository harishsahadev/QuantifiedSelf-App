from .database import db

class User(db.Model):
    __tablename__ = 'user'
    userid = db.Column(db.Integer, autoincrement=True, primary_key=True)
    username = db.Column(db.String, unique=True, nullable=False)
    password = db.Column(db.String, unique=True, nullable=False)

class Tracker_type(db.Model):
    __tablename__ = 'tracker_type'
    typeid = db.Column(db.Integer, autoincrement=True, primary_key=True)
    type = db.Column(db.String, unique=True, nullable=False)

class Tracker(db.Model):
    __tablename__ = 'tracker'
    trackerid = db.Column(db.Integer, autoincrement=True, primary_key=True)
    trackername = db.Column(db.String, unique=True, nullable=False)
    description = db.Column(db.String)
    type = db.Column(db.Integer, db.ForeignKey("tracker_type.type"), nullable=False)
    userid = db.Column(db.Integer, db.ForeignKey("user.userid"), nullable=False)