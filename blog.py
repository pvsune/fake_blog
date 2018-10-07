import json
import logging
import os

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
    HOST = os.getenv('HOST', 'localhost')
    PORT = os.getenv('PORT', 8080)
    CONSUMER_KEY = os.getenv('CONSUMER_KEY', '')

    logging.basicConfig(level=logging.DEBUG)
    app = app()

    # Set configs.
    with open('config.json') as fp:
        app.config.load_dict(json.load(fp))
    app.config.update(
        'blog.pocket',
        consumer_key=CONSUMER_KEY,
        redirect_uri=app.config['blog.pocket.redirect_uri'].format(HOST, PORT)
    )

    # Setup session.
    app = SessionMiddleware(app, app.config)

    run(app=app, host=HOST, port=PORT, reloader=True)
