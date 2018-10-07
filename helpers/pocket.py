import logging

import requests
from bottle import redirect, HTTPError


logging.basicConfig(level=logging.DEBUG)


class Pocket(object):
    BASE_URL = 'https://getpocket.com'
    AUTHORIZE_URL = '{}/auth/authorize'.format(BASE_URL)

    def __init__(self, consumer_key, redirect_uri):
        self.consumer_key = consumer_key
        self.redirect_uri = redirect_uri

    def request(self, method, path, json={}):
        try:
            r = requests.request(
                method=method,
                url='{}/{}'.format(self.BASE_URL, path),
                json=json,
                headers={'X-Accept': 'application/json'}
            )
            r.raise_for_status()
            logging.debug(
                'POCKET %s url=%s, json=%s, resp=%s',
                method, path, json, r.text
            )
            res = r.json()
        except requests.exceptions.HTTPError:
            # Error details are returned in headers (X-Error, X-Error-Code).
            logging.error(
                'Failed requesting POCKET url=%s: %s', path, r.headers
            )
            raise
        return res

    def get_access_token(self, session):
        if session.get('access_token'):
            return session['access_token']
        # Get request token.
        res = self.request(
            method='POST',
            path='v3/oauth/request',
            json={
                'consumer_key': self.consumer_key,
                'redirect_uri': self.redirect_uri,
            },
        )
        session['request_token'] = res['code']
        session.save()
        # TODO: Use urlparse.
        return redirect('{}?request_token={}&redirect_uri={}'.format(
            self.AUTHORIZE_URL, res['code'], self.redirect_uri
        ))

    def authorize(self, session):
        try:
            res = self.request(
                'POST',
                'v3/oauth/authorize',
                json={
                    'consumer_key': self.consumer_key,
                    'code': session['request_token']
                }
            )
        except requests.exceptions.HTTPError:
            raise HTTPError(status=400, body='Pocket authorization failed.')
        session['access_token'] = res['access_token']
        session.save()
        return

    def get(self, session):
        access_token = self.get_access_token(session)
        res = self.request(
            'POST',
            'v3/get',
            json={
                'consumer_key': self.consumer_key,
                'access_token': access_token,
                'count': 5,
                'detailType': 'complete',
                'contentType': 'article',
            }
        )
        return (v for k, v in res['list'].items())
