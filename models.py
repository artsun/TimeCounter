
from flask_login import UserMixin
from datetime import datetime
from . import db


class User(UserMixin, db.Model):
    pk = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))
    name = db.Column(db.String(1000))

    def get_id(self):
        return self.pk


class Day(db.Model):
    pk = db.Column(db.Integer, primary_key=True)
    user_pk = db.Column(db.Integer, db.ForeignKey('user.pk'))
    start = db.Column(db.DateTime, default=datetime.now)
    longitude = db.Column(db.Integer(10))


class Break(db.Model):
    pk = db.Column(db.Integer, primary_key=True)
    day_pk = db.Column(db.Integer, db.ForeignKey('day.pk'))
    start = db.Column(db.DateTime, default=datetime.now)
    stop = db.Column(db.DateTime, default=datetime.now)
