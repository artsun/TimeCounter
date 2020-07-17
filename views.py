# -*- coding: utf-8 -*-

from flask import request, render_template, redirect, Blueprint, flash, url_for
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, login_required, current_user, logout_user, AnonymousUserMixin

from .models import User
from . import db


common = Blueprint('common', __name__)


@common.route('/')
def main_page():
    cuser = '' if not current_user.is_active and not current_user.is_authenticated and current_user.is_anonymous else current_user.name

    print()
    return render_template('calend.html', name=cuser, ishold=False)


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
    email = request.form.get('email')
    password = request.form.get('password')
    remember = True if request.form.get('remember') else False

    user = User.query.filter_by(email=email).first()

    if not user or not check_password_hash(user.password, password):
        flash('Введите корректные данные')
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
