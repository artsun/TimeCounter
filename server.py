# -*- coding: utf-8 -*-

from flask import Flask, request, render_template

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.3'
}

app = Flask(__name__,  static_url_path='', static_folder='static',)


@app.route('/', methods=['GET'])
def index():
    """
    обработка REST-запроса GET
    """
    if request.method == 'GET':
        #request.args.get('url')
        print(request.args)
    else:
        res = 'Incorrect request. Try: url=https://...'

    return render_template('calend.html', data='')

@app.errorhandler(404)
def page_not_found(*args):
    """
    обработка случая: страница не найдена
    """
    return render_template('calend.html', data='Incorrect request. Try: url=https://...'), 404

if __name__ == '__main__':
    app.run(host='localhost', port=5000, debug=False)
