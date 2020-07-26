# -*- coding: utf-8 -*-

from flask import request, render_template, redirect, Blueprint, flash, url_for, make_response
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, login_required, current_user, logout_user
from datetime import datetime
from collections import namedtuple

from .constants import MONTHS
from .tools import delta_to_hms
from .models import User, Wday, Break
from . import db
from . import cache

HMS = namedtuple('HMS', ['start', 'stop', 'duration', 'done'])

common = Blueprint('common', __name__)

@common.route('/istrue', methods=['GET'])
def istrue():
    cuser = User.check_anon(current_user)
    day = cuser.day() if cache.get(cuser.pk) is None else Wday.query.filter_by(pk=cache.get('day')).first()
    br = Break.today(day).filter_by(actual=True).first()
    return '0' if br is None else '1'


@common.route('/', methods=['GET'])
def main_page():
    cuser = User.check_anon(current_user)
    day = cuser.day(tuple(request.args.values())) if request.args else cuser.day()

    if day is not None:
        print(Wday().get_breaks())
        cache.set(cuser.pk, day.pk)

        break_now = Break.today(day).filter_by(actual=True).first()
        is_pause = 1 if break_now else 0
        show_month = MONTHS[day.finish.month]
        begind = day.longitude
        today = HMS(day.start, day.finish, delta_to_hms(day.finish-day.start), day.done)
        breaks_sum = day.calc_breaks()
        breaks_sum = delta_to_hms(breaks_sum) if breaks_sum else ''
    else:
        is_pause, begind, today, show_month, breaks_sum = 0, 8, None, '', ''

    return render_template('calend.html', cuser=cuser, begind=begind, breaks_sum=breaks_sum,
                           is_pause=is_pause, show_month=show_month, today=today)


@common.route('/refreshtimer', methods=['GET'])
def refresh_timer():
    if request.args.get('do') is not None:
        cuser = User.check_anon(current_user)
        day = cuser.day() if cache.get(cuser.pk) is None else Wday.by_pk(cache.get(cuser.pk))
        return day.left()


@common.route('/refreshbreaks', methods=['GET'])
def refresh_breaks():
    if request.args.get('do') is not None:
        cuser = User.check_anon(current_user)
        day = cuser.day() if cache.get(cuser.pk) is None else Wday.by_pk(cache.get(cuser.pk))
        res = day.breaks_strings()
        return dict(breaks=res)


@common.route('/setday', methods=['GET'])
def setday():
    cuser = User.check_anon(current_user)
    day = Wday.by_user_today(cuser)
    if request.args.get("paused") is not None:
        if day is not None and day.finish > datetime.now():
            actual_break = Break.today(day).filter_by(actual=True).first()
            if actual_break:  # уже на паузе
                actual_break.close()
            else:
                db.session.add(Break(day_pk=day.pk, actual=True))
                db.session.commit()
        return dict(done='ok')


@common.route('/', methods=['POST'])
def set_day():
    cuser = User.check_anon(current_user)
    day = Wday.by_user_today(cuser)
    if request.form.get("begind") is not None:
        if cuser and day is None:
            begind = int(request.form.get("begind"))
            day = Wday(user_pk=cuser.pk, longitude=begind)
            day.update_session()
            day.finish = day.calc_finish()
            day.update_session()
    if request.form.get("changed") is not None:
        if day is not None and day.finish > datetime.now():
            day.longitude = int(request.form.get("changed"))
            day.update_session()
            day.finish = day.calc_finish()
            day.update_session()
    if request.form.get("finishd") is not None:
        if day is not None:
            day.finish = datetime.now()
            day.done = True
            day.update_session()
            day.longitude = day.recalc_longitude()
            day.update_session()
    if request.form.get("resetd") is not None:
        if day is not None:
            db.session.delete(day)
            db.session.commit()
    return redirect(url_for('common.main_page'))


@common.route('/profile')
@login_required
def profile_page():
    return render_template('profile.html', cuser=current_user)


auth = Blueprint('auth', __name__)


@auth.route('/login')
def login_page():
    return render_template('login.html')


@auth.route('/login', methods=['POST'])
def login_post_page():
    username = request.form.get('username')
    password = request.form.get('password')
    remember = True if request.form.get('remember') else False

    user = User.query.filter_by(name=username).first()

    if not user or not check_password_hash(user.password, password):
        flash('Введён неверный пароль, либо пользователь не существует')
        return redirect(url_for('auth.login_page'))

    login_user(user, remember=remember)
    return redirect(url_for('common.main_page'))


@auth.route('/signup')
def signup_page():
    return render_template('signup.html')


@auth.route('/signup', methods=['POST'])
def signup_post_page():
    email, name, password = request.form.get('email'), request.form.get('name'), request.form.get('password')
    user = User.query.filter_by(name=name).first()

    if user:
        flash('Пользователь уже зарегистрирован')
        return redirect(url_for('auth.signup_page'))

    db.session.add(User(email=email, password=generate_password_hash(password, method='sha256'), name=name))
    db.session.commit()

    return redirect(url_for('auth.login_page'))


@auth.route('/logout')
def logout_page():
    logout_user()
    return redirect(url_for('common.main_page'))
