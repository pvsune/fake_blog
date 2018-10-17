import json
import logging
import os
from urllib.parse import urlencode

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
    limit = int(request.query.get('limit', 5))
    offset = int(request.query.get('offset', 0))
    articles = pocket.get(session, limit, offset)
    return template(
        'index',
        articles=articles,
        next='/?{}'.format(urlencode({'limit': limit, 'offset': offset+1})),
        username=session['username'].split('@')[0],
    )


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
    REDIRECT_HOST = os.getenv('REDIRECT_HOST', '')  # Use with Kubernetes.

    logging.basicConfig(level=logging.DEBUG)
    app = app()

    # Set configs.
    with open('config.json') as fp:
        app.config.load_dict(json.load(fp))
    app.config.update(
        'blog.pocket',
        consumer_key=CONSUMER_KEY,
        redirect_uri=app.config['blog.pocket.redirect_uri'].format(
            REDIRECT_HOST, 80 if REDIRECT_HOST else HOST, PORT
        )
    )

    # Setup session.
    app = SessionMiddleware(app, app.config)

    run(app=app, host=HOST, port=PORT, reloader=True)
