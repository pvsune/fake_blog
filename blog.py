import logging

import requests
from beaker.middleware import SessionMiddleware
from bottle import route, run, template, static_file, redirect, request, app

from helpers.pocket import Pocket


@route('/')
def index():
    session = request.environ.get('beaker.session')
    pocket = Pocket(
        request.app.config['blog.pocket.consumer_key'],
        request.app.config['blog.pocket.redirect_uri'],
    )
    articles = pocket.get(session)
    return template('index', articles=articles)


@route('/oauth/cb')
def oauth_cb():
    session = request.environ.get('beaker.session')
    pocket = Pocket(
        request.app.config['blog.pocket.consumer_key'],
        request.app.config['blog.pocket.redirect_uri'],
    )
    pocket.authorize(session)
    return redirect('/')


@route('/<filename:path>')
def send_static(filename):
    return static_file(filename, root='static')


if __name__ == '__main__':
    # WANT: Get from CLI args.
    HOST = 'localhost'
    PORT = 8080

    logging.basicConfig(level=logging.DEBUG)
    app = app()

    # Set configs.
    app.config['blog.pocket.consumer_key'] = '74628-e4bcb63cf0c35403d8e8c86b'
    app.config['blog.pocket.redirect_uri'] = (
        'http://{}:{}/oauth/cb'.format(HOST, PORT)
    )

    # Setup session.
    app = SessionMiddleware(app, {
        'session.type': 'file',
        'session.cookie_expires': 300,
        'session.data_dir': './data',
        'session.auto': True,
    })

    run(app=app, host=HOST, port=PORT, reloader=True)
