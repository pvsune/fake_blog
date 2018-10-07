import logging

import requests


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
            logging.exception(
                'Failed requesting POCKET url=%s: %s', path, r.headers
            )
            raise HTTPError(status=500, body='Internal Server Error')
        return res
