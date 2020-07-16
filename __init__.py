from flask import Flask
from flask_sqlalchemy import SQLAlchemy

# init SQLAlchemy so we can use it later in our models
db = SQLAlchemy()


def create_app():
    app = Flask(__name__,  static_url_path='', static_folder='static',)
    #app.config.from_object('config')
    app.config['CSRF_ENABLED']= True

    app.config['SECRET_KEY'] = 'secret-key-goes-here'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite'

    db.init_app(app)

    # blueprint for auth routes in our app
    from .views import auth as auth_blueprint
    app.register_blueprint(auth_blueprint)

    # blueprint for non-auth parts of app
    from .views import calend_bp as calend_blueprint
    app.register_blueprint(calend_blueprint)

    from .views import index_bp
    app.register_blueprint(index_bp)

    return app
