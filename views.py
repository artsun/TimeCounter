# -*- coding: utf-8 -*-

from flask import request, render_template, redirect, Blueprint, flash, url_for
from werkzeug.security import generate_password_hash, check_password_hash
from .models import User
from . import db

from .forms import RegistrationForm

index_bp = Blueprint('index_bp', __name__)

@index_bp.route('/')
def index_page():
    return render_template('index.html')

@index_bp.route('/profile')
def profile_page():
    return render_template('profile.html')


calend_bp = Blueprint('calend_bp', __name__) #, url_prefix='/'


@calend_bp.route('/cal', methods=['GET'])
def calendar_page():
    """
    обработка REST-запроса GET
    """
    if request.method == 'GET':
        #request.args.get('url')
        print(request.args)
    else:
        res = 'Incorrect request. Try: url=https://...'

    return render_template('calend.html', data='')

auth = Blueprint('auth', __name__)


@auth.route('/login')
def login():
    return render_template('login.html')


@auth.route('/signup')
def signup():
    return render_template('signup.html')


@auth.route('/signup', methods=['POST'])
def signup_post():
    email = request.form.get('email')
    name = request.form.get('name')
    password = request.form.get('password')
    print(email, name, password)

    user = User.query.filter_by(email=email).first() # if this returns a user, then the email already exists in database

    if user: # if a user is found, we want to redirect back to signup page so user can try again
        return redirect(url_for('auth.signup'))

    # create a new user with the form data. Hash the password so the plaintext version isn't saved.
    new_user = User(email=email, name=name, password=generate_password_hash(password, method='sha256'))

    # add the new user to the database
    db.session.add(new_user)
    db.session.commit()

    return redirect(url_for('auth.login'))


@auth.route('/logout')
def logout():
    return 'Logout'

# @bp.route('/', methods=['GET'])
# def register():
#     form = RegistrationForm(request.form)
#     # if request.method == 'POST' and form.validate():
#     #     #user = User(form.username.data, form.email.data, form.password.data)
#     #     #db_session.add(user)
#     #     flash('Thanks for registering')
#     #     return redirect(url_for('login'))
#     return render_template('auth.html', form=form)



#redirect("http://www.example.com", code=302)