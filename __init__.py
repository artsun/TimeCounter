import os.path
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

db = SQLAlchemy()


def create_app():
    app = Flask(__name__,  static_url_path='', static_folder='static',)
    app.config['CSRF_ENABLED']= True
    app.config['SECRET_KEY'] = 'any-key'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///{}'.format(os.path.join(os.path.dirname(__file__), 'storage.db'))
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)

    from .models import User

    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_pk):
        return User.query.get(int(user_pk))

    from .views import auth as auth_blueprint
    app.register_blueprint(auth_blueprint)

    from .views import indx
    app.register_blueprint(indx)

    return app
