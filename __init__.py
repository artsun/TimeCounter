import os.path
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_caching import Cache

db = SQLAlchemy()
cache = Cache(config={'CACHE_TYPE': 'simple'})

def create_app():



    app = Flask(__name__,  static_url_path='', static_folder='static',)
    app.config['CSRF_ENABLED']= True
    app.config['SECRET_KEY'] = 'any-key'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///{}'.format(os.path.join(os.path.dirname(__file__), 'storage.db'))
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    cache.init_app(app)
    db.init_app(app)

    from .models import User

    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_pk):
        return User.query.get(user_pk) if not isinstance(user_pk, int) else None

    from .views import auth
    app.register_blueprint(auth)

    from .views import common
    app.register_blueprint(common)

    return app
