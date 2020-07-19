
from flask_login import UserMixin
from datetime import datetime, timedelta
from uuid import uuid4
from sqlalchemy_utils import UUIDType
from sqlalchemy.orm import relationship

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
    children = relationship("Break", cascade="all,delete", backref="parent")

    def _recalc_longitude(self):
        delta = (self.finish-self.start)
        self.longitude = (delta.seconds//3600)

    def calc_finish(self):
        total_hours = self.start.hour+self.longitude
        hours = total_hours % 24 if total_hours // 24 else total_hours
        days = (total_hours // 24) + self.start.day
        return self.start.replace(hour=hours, day=days)

    def delta(self) -> tuple:
        break_ = Break.today(self).filter_by(actual=True).first()
        diff = break_.start if break_ is not None else datetime.now()
        delta = (self.finish - diff) if self.finish > diff else timedelta(0, 0)
        return delta.seconds//3600, (delta.seconds//60)%60, delta.seconds%60

    @staticmethod
    def by_user_today(user):
        return None if user is None else Wday.query.filter_by(user_pk=user.pk, day=datetime.now().day).first()

    def correct_finish_with_session(self, db, now=False):
        db.session.add(self)
        db.session.commit()
        self.finish = datetime.now() if now else self.calc_finish()
        self._recalc_longitude() if now else None
        db.session.add(self)
        db.session.commit()

    def finday(self):
        hms = []
        for x in (self.finish.hour, self.finish.minute, self.finish.second, self.finish.day):
            hms.append(str(x)) if x > 9 else hms.append(f'0{x}')
        hms.append(MONTHS[self.finish.month])
        return hms

    def add_break_delay(self, break_):
        self.finish += break_.period()
        db.session.add(self)
        db.session.commit()


class Break(db.Model):
    pk = db.Column(UUIDType(binary=False), primary_key=True, default=uuid4, unique=True, nullable=False)
    day_pk = db.Column(UUIDType(binary=False), db.ForeignKey('wday.pk'))
    start = db.Column(db.DateTime, default=datetime.now)
    stop = db.Column(db.DateTime)
    actual = db.Column(db.Boolean)

    @staticmethod
    def today(day):
        return Break.query.filter_by(day_pk=day.pk)

    def period(self):
        return (datetime.now() - self.start) if self.stop is None else (self.stop - self.start)

    def close(self):
        self.stop = datetime.now()
        self.actual = False
        db.session.add(self)
        db.session.commit()
