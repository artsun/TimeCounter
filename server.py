# -*- coding: utf-8 -*-
# import os.path
# #from flask import Flask, render_template, Blueprint
# from . import create_app
# import sqlite3
# from flask import g
#
# DATABASE = os.path.join(os.path.dirname(__file__), 'database.db')
#
# # app = Flask(__name__,  static_url_path='', static_folder='static',)
# # app.config.from_object('config')
# # app.register_blueprint(views.bp)
#
#
# # def get_db():
# #     db = getattr(g, '_database', None)
# #     if db is None:
# #         db = g._database = sqlite3.connect(DATABASE)
# #     return db
# #
# #
# # @app.errorhandler(404)
# # def page_not_found(*args):
# #     """
# #     обработка случая: страница не найдена
# #     """
# #     return render_template('404.html', data='Incorrect request. Try: url=https://...'), 404
#
#
# if __name__ == '__main__':
#
#     create_app().run(host='localhost', port=5000, debug=False)
