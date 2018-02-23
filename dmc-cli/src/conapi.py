import os
import json
import logging
import requests
from requests import get, post

TIMEOUT_SECONDS = 3

logging.basicConfig(
    format="[conapi %(asctime)s] %(levelname)s %(message)s",
    level=logging.INFO)


class ConApi(object):
    def __init__(self, uri):
        self.uri = uri

    def gen_url(self, url):
        return os.path.join(self.uri, url).replace('\\', '/')

    def try_request(func):
        def handle_exception(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except requests.exceptions.ConnectionError:
                logging.warn('could not connect to server')
            except requests.exceptions.Timeout:
                logging.warn('request timed out')

        return handle_exception

    @try_request
    def clear_list(self):
        return get(self.gen_url('reset'), timeout=TIMEOUT_SECONDS)

    @try_request
    def update_list(self, latest):
        return post(self.gen_url('update'),
                    data=json.dumps({'latest': latest}),
                    headers={'content-type': 'application/json'}, timeout=TIMEOUT_SECONDS)

    @try_request
    def get_list(self):
        return get(self.gen_url('devices'), timeout=TIMEOUT_SECONDS)
