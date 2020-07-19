
from flask_login import UserMixin
from datetime import datetime
from uuid import uuid4
from sqlalchemy_utils import UUIDType

from .constants import MONTHS
from . import db


class User(UserMixin, db.Model):
    pk = db.Column(UUIDType(binary=False), primary_key=True, default=uuid4, unique=True, nullable=False)
    email = db.Column(db.String(100))
    password = db.Column(db.String(100))
    name = db.Column(db.String(1000), unique=True)

    def get_id(self):
        return self.pk

    @staticmethod
    def by_name(name):
        return User.query.filter_by(name=name).first()


class Wday(db.Model):
    pk = db.Column(UUIDType(binary=False), primary_key=True, default=uuid4, unique=True, nullable=False)
    user_pk = db.Column(UUIDType(binary=False), db.ForeignKey('user.pk'))
    start = db.Column(db.DateTime, default=datetime.now)
    longitude = db.Column(db.Integer())
    day = db.Column(db.Integer, default=datetime.now().day)
    month = db.Column(db.Integer, default=datetime.now().month)
    year = db.Column(db.Integer, default=datetime.now().year)
    finish = db.Column(db.DateTime)

    def set_finish(self):
        total_hours = self.start.hour+self.longitude
        hours = total_hours % 24 if total_hours // 24 else total_hours
        days = (total_hours // 24) + self.start.day
        self.finish = self.start.replace(hour=hours, day=days)

    def delta(self) -> tuple:
        if self.finish < datetime.now():
            return 0, 0, 0
        delta = self.finish - datetime.now()
        return delta.seconds//3600, (delta.seconds//60)%60, delta.seconds%60

    @staticmethod
    def by_user_today(user_pk):
        return Wday.query.filter_by(user_pk=user_pk, day=datetime.now().day).first()

    def correct_session(self, db):
        db.session.add(self)
        db.session.commit()
        self.set_finish()
        db.session.add(self)
        db.session.commit()

    def finday(self):
        hms = []
        for x in (self.finish.hour, self.finish.minute, self.finish.second, self.finish.day):
            hms.append(str(x)) if x > 9 else hms.append(f'0{x}')
        hms.append(MONTHS[self.finish.month])
        return hms


class Break(db.Model):
    pk = db.Column(UUIDType(binary=False), primary_key=True, default=uuid4, unique=True, nullable=False)
    day_pk = db.Column(UUIDType(binary=False), db.ForeignKey('wday.pk'))
    start = db.Column(db.DateTime, default=datetime.now)
    stop = db.Column(db.DateTime, default=datetime.now)
