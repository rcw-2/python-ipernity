
import json
import logging
import os
from time import time

import pytest

from ipernity import IpernityAPI, IpernityError


# API functions that are not tested
skipped_methods = [
    'auth.getFrob',     # only used for login
    'auth.getToken',    # only used for login
    'doc.albums.add',   # "method not found" - exists only in documentation
    'doc.search',       # Need a better test case?
    'upload.replace',   # Behaves like upload.file, bug in Ipernity?
]


basedir = os.path.dirname(os.path.dirname(__file__))
keyfile = os.path.join(basedir, '.key.json')
webkeyfile = os.path.join(basedir, '.webkey.json')
tokenfile = os.path.join(basedir, '.token.json')
logfile = os.path.join(basedir, 'test.log')
methodlist = os.path.join(basedir, 'tested_methods.json')

logging.basicConfig(
    level = logging.DEBUG,
    filename = logfile,
    filemode = 'w',
    format = '%(levelname)s %(name)s(%(filename)s:%(lineno)s) %(message)s'
)
log = logging.getLogger(__name__)


@pytest.fixture
def files():
    return {
        'key':      keyfile,
        'token':    tokenfile,
        'webkey':   webkeyfile,
    }


@pytest.fixture
def api(token, tested_methods):
    with open(keyfile, 'r') as kf:
        app = json.load(kf)
    return TestAPI(
        app['api_key'],
        app['api_secret'],
        token,
        tested_methods
    )


@pytest.fixture(scope = 'session')
def changes():
    data = {
        'docs':     [],
        'albums':   [],
        'user':     {},
        'start':    int(time()),
    }
    return data


@pytest.fixture(scope = 'session')
def perms():
    return {'doc': 'delete'}


@pytest.fixture(scope = 'session')
def token(changes):
    with open(tokenfile, 'r') as tf:
        auth = json.load(tf)
    changes['user'].update(auth['user'])
    return auth


@pytest.fixture(scope = 'session')
def tested_methods():
    methods = TestedMethods()
    yield methods
    methods.save(methodlist)


class TestedMethods:
    def __init__(self):
        self._data = {}
        for method in IpernityAPI.__methods__:
            if method in skipped_methods:
                self._data[method] = 'skipped'
            else:
                self._data[method] = 'untested'
    
    def mark(self, method):
        if method not in self._data:
            raise KeyError('{method} is not in method list')
        self._data[method] = 'tested'
    
    def save(self, filename):
        save_data = {
            'tested':   [m for m, t in self._data.items() if t == 'tested'],
            'skipped':  [m for m, t in self._data.items() if t == 'skipped'],
            'untested': [m for m, t in self._data.items() if t == 'untested'],
        }
        save_data.update({
            'count': {
                'tested':   len(save_data['tested']),
                'skipped':  len(save_data['skipped']),
                'untested': len(save_data['untested']),
            }
        })
        with open(filename, 'w') as mf:
            json.dump(save_data, mf, indent = 4)


class TestAPI(IpernityAPI):
    def __init__(self, key, secret, token, tested):
        self._tested_methods = tested
        super().__init__(key, secret, token)
    
    def call(self, method_name, **kwargs):
        res = super().call(method_name, **kwargs)
        self._tested_methods.mark(method_name)
        return res

