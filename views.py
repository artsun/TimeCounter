# -*- coding: utf-8 -*-

from flask import request, render_template, redirect, Blueprint, flash, url_for, make_response
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, login_required, current_user, logout_user
from datetime import datetime

from .models import User, Wday, Break
from . import db



common = Blueprint('common', __name__)


@common.route('/', methods=['POST', 'GET'])
def main_page():
    is_anon = (current_user.is_active, current_user.is_authenticated, current_user.is_anonymous)
    cuser = '' if is_anon == (False, False, True) else current_user.name
    pause_label, is_pause = 'Пауза', 0

    if request.args.get('refreshLeftTime') is not None:
        day = Wday.by_user_today(User.by_name(name=cuser))
        h, m, s = (0, 0, 0) if day is None else day.delta()
        return dict(getHours=h, getMinutes=m, getSeconds=s)

    if Wday.by_user_today(User.by_name(name=cuser)) is None:
        begind, finday = 8, (' - ', ' - ', ' - ', ' - ', ' - ')
        if request.form.get("begind") is not None:
            begind = int(request.form.get("begind"))
            day = Wday(user_pk=User.by_name(name=cuser).pk, longitude=begind)
            day.correct_finish_with_session(db)
            finday = day.finday()
    else:
        day = Wday.by_user_today(User.by_name(name=cuser))
        list_breaks = Break.today(day)
        actual_break = list_breaks.filter_by(actual=True).first()
        pause_label, is_pause = ('Продолжить', 1) if actual_break else ('Пауза', 0)
        if request.form.get("changed") is not None:
            changed = int(request.form.get("changed"))
            day.longitude = changed
            day.correct_finish_with_session(db)
        if request.form.get("finish") is not None:
            day.correct_finish_with_session(db, now=True)
        finday = day.finday()
        begind = day.longitude
        if request.form.get("reset") is not None:
            db.session.delete(day)
            db.session.commit()
            finday = (' - ', ' - ', ' - ', ' - ', ' - ')
        if request.form.get("pause") is not None:
            if actual_break:  # уже на паузе
                actual_break.close()
                day.add_break_delay(actual_break)
                finday = day.finday()
                pause_label, is_pause = 'Пауза', 0
            else:
                db.session.add(Break(day_pk=day.pk, actual=True))
                db.session.commit()
                pause_label, is_pause = 'Продолжить', 1


    return render_template('calend.html', cuser=cuser, begind=begind, fhou=finday[0], pause_label=pause_label,
                           is_pause=is_pause, fmin=finday[1], fsec=finday[2], fday=finday[3], fmon=finday[4])


@common.route('/profile')
@login_required
def profile_page():
    if request.method == 'GET':
        #request.args.get('url')
        print(request.args)
    else:
        res = 'Incorrect request'

    return render_template('profile.html', name=current_user.name)


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
