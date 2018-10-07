import logging
import os

import requests
from beaker.middleware import SessionMiddleware
from bottle import (
    route, run, template, static_file, HTTPError, redirect, request,
    app as bottle_app
)

from helpers.pocket import Pocket


def get_access_token(pocket):
    session = request.environ.get('beaker.session')
    if session.get('access_token'):
        return session['access_token']
    # Get request token.
    res = pocket.request(
        method='POST',
        path='v3/oauth/request',
        json={
            'consumer_key': pocket.consumer_key,
            'redirect_uri': pocket.redirect_uri,
        },
    )
    session['request_token'] = res['code']
    session.save()
    # TODO: Use urlparse.
    return redirect('{}?request_token={}&redirect_uri={}'.format(
        pocket.AUTHORIZE_URL, res['code'], pocket.redirect_uri
    ))


@route('/')
def index():
    pocket = Pocket(
        # TODO: Put to config.
        '74628-e4bcb63cf0c35403d8e8c86b',
        'http://localhost:8080/oauth/cb',
    )
    access_token = get_access_token(pocket)
    return template('index')


@route('/oauth/cb')
def oauth_cb():
    session = request.environ.get('beaker.session')
    pocket = Pocket(
        # TODO: Put to config.
        '74628-e4bcb63cf0c35403d8e8c86b',
        'http://localhost:8080/oauth/cb',
    )
    res = pocket.request(
        'POST',
        'v3/oauth/authorize',
        json={
            'consumer_key': pocket.consumer_key,
            'code': session['request_token']
        }
    )
    session['access_token'] = res['access_token']
    session.save()
    return redirect('/')


@route('/<filename:path>')
def send_static(filename):
    return static_file(filename, root='static')


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    app = SessionMiddleware(bottle_app(), {
        'session.type': 'file',
        'session.cookie_expires': 300,
        'session.data_dir': './data',
        'session.auto': True
    })
    run(app=app, host='localhost', port=8080, reloader=True)
