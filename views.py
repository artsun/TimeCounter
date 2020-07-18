# -*- coding: utf-8 -*-

from flask import request, render_template, redirect, Blueprint, flash, url_for, make_response
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, login_required, current_user, logout_user, AnonymousUserMixin
from datetime import datetime

from .models import User, Wday
from . import db


common = Blueprint('common', __name__)


@common.route('/', methods=['POST', 'GET'])
def main_page():
    is_anon = (current_user.is_active, current_user.is_authenticated, current_user.is_anonymous)
    cuser = '' if is_anon == (False, False, True) else current_user.name

    #if request.args.get('refreshLeftTime') is not None:
        # day = Wday.query.filter_by(user_pk=User.query.filter_by(name=cuser).first().pk)
        # day = [x for x in day if x.start.day==datetime.now().day]
        # print(day)
        # return dict(getHours=7, getMinutes=1, getSeconds=10)

    # if request.form.get("begind") is not None:
    #     begind = int(request.form.get("begind"))
    #     day = Wday(user_pk=User.query.filter_by(name=cuser).first().pk, longitude=begind)
    #     db.session.add(day)
    #     db.session.commit()

    return render_template('calend.html', cuser=cuser, ishold=False)


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
    email = request.form.get('email')
    name = request.form.get('name')
    password = request.form.get('password')
    print(email, name, password)

    user = User.query.filter_by(email=email).first()

    if user:
        flash('Данная почта уже зарегистрирована')
        return redirect(url_for('auth.signup_page'))

    new_user = User(email=email, name=name, password=generate_password_hash(password, method='sha256'))

    db.session.add(new_user)
    db.session.commit()

    return redirect(url_for('auth.login_page'))


@auth.route('/logout')
def logout_page():
    logout_user()
    return redirect(url_for('common.main_page'))
