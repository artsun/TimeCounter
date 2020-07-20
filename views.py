# -*- coding: utf-8 -*-

from flask import request, render_template, redirect, Blueprint, flash, url_for, make_response
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, login_required, current_user, logout_user
from datetime import datetime
from collections import namedtuple

from .constants import MONTHS
from .tools import define_current_user, delta_to_hms
from .models import User, Wday, Break
from . import db

Verbose_hms = namedtuple('Verbose_hms', ['start', 'stop', 'duration', 'done'])

common = Blueprint('common', __name__)


@common.route('/', methods=['GET'])
def main_page():
    cuser = User.by_name(name=define_current_user(current_user))
    day = Wday.by_user_today(cuser) if cuser else None
    if day is not None:
        breaks = Break.today(day).filter_by(actual=False)
        breaks = [] if breaks is None else [
            Verbose_hms(x.start, x.stop, f'({delta_to_hms(x.stop-x.start)})', 1) for x in breaks]
        break_now = Break.today(day).filter_by(actual=True).first()
        pause_label, is_pause = ('Продолжить', 1) if break_now else ('Пауза', 0)
        breaks.append(Verbose_hms(break_now.start, ' ... ', '', 0)) if break_now else None
        show_month = MONTHS[day.finish.month]
        begind = day.longitude
        fin = Verbose_hms(day.start, day.finish, delta_to_hms(day.finish-day.start), day.done)
    else:
        pause_label, is_pause, begind, breaks, fin, show_month = 'Пауза', 0, 8, [], None, ''

    return render_template('calend.html', cuser=cuser, begind=begind, pause_label=pause_label,
                           is_pause=is_pause, show_month=show_month, fin=fin, breaks=breaks)


@common.route('/refreshtimer', methods=['GET'])
def refresh_timer():
    if request.args.get('refreshLeftTime') is not None:
        cuser = User.by_name(name=define_current_user(current_user))
        day = Wday.by_user_today(cuser) if cuser else None
        h, m, s = (0, 0, 0) if day is None else day.delta()
        return dict(getHours=h, getMinutes=m, getSeconds=s)


@common.route('/setday', methods=['POST'])
def set_day():
    cuser = User.by_name(name=define_current_user(current_user))
    day = Wday.by_user_today(cuser) if cuser else None
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
    if request.form.get("paused") is not None:
        if day is not None and day.finish > datetime.now():
            actual_break = Break.today(day).filter_by(actual=True).first()
            if actual_break:  # уже на паузе
                actual_break.close()
            else:
                db.session.add(Break(day_pk=day.pk, actual=True))
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
