
from flask_login import UserMixin
from datetime import datetime, timedelta
from uuid import uuid4
from sqlalchemy_utils import UUIDType
from sqlalchemy.orm import relationship

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
    done = db.Column(db.Boolean, default=False)
    children = relationship("Break", cascade="all,delete", backref="wday")

    def recalc_longitude(self) -> int:
        delta = (self.finish-self.start)
        return delta.seconds//3600

    def calc_finish(self):
        h = self.start.hour + self.longitude
        days = (h // 24) + self.start.day
        h = h % 24 if h // 24 else h
        breaks = Break.today(self).filter_by(actual=False)
        breaks = sum(((x.stop - x.start) for x in breaks), timedelta()) if breaks else timedelta(0,0)
        return self.start.replace(hour=h, day=days) + breaks


    def delta(self) -> tuple:
        break_ = Break.today(self).filter_by(actual=True).first()
        diff = break_.start if break_ is not None else datetime.now()
        delta = (self.finish - diff) if self.finish > diff else timedelta(0, 0)
        return delta.seconds//3600, (delta.seconds//60)%60, delta.seconds%60

    @staticmethod
    def by_user_today(user: User):
        return None if user is None else Wday.query.filter_by(user_pk=user.pk, day=datetime.now().day).first()

    def update_session(self):
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

    def period(self) -> tuple:
        delta = self.stop - self.start
        return delta.seconds//3600, (delta.seconds//60)%60, delta.seconds%60

    def close(self):
        self.stop = datetime.now()
        self.wday.finish += (self.stop - self.start)
        self.wday.update_session()
        self.actual = False
        db.session.add(self)
        db.session.commit()
