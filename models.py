
from flask_login import UserMixin
from datetime import datetime
from uuid import uuid4
from sqlalchemy_utils import UUIDType


from . import db


class User(UserMixin, db.Model):
    pk = db.Column(UUIDType(binary=True), primary_key=True, default=uuid4, unique=True, nullable=False)
    email = db.Column(db.String(100))
    password = db.Column(db.String(100))
    name = db.Column(db.String(1000), unique=True)

    def get_id(self):
        return self.pk


class Wday(db.Model):
    pk = db.Column(UUIDType(binary=True), primary_key=True, unique=True, nullable=False)
    user_pk = db.Column(UUIDType(binary=True), db.ForeignKey('user.pk'))
    start = db.Column(db.DateTime, default=datetime.now)
    longitude = db.Column(db.Integer())
    day = db.Column(db.Integer, default=datetime.now().day)
    month = db.Column(db.Integer, default=datetime.now().month)
    year = db.Column(db.Integer, default=datetime.now().year)
    finish = db.Column(db.DateTime)


class Break(db.Model):
    pk = db.Column(UUIDType(binary=True), primary_key=True, unique=True, nullable=False)
    day_pk = db.Column(UUIDType(binary=True), db.ForeignKey('wday.pk'))
    start = db.Column(db.DateTime, default=datetime.now)
    stop = db.Column(db.DateTime, default=datetime.now)
