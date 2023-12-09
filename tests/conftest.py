
from __future__ import annotations

import json
import logging
import os
from hashlib import md5
from html.parser import HTMLParser
from time import time
from urllib.parse import parse_qs, urlparse
from typing import Any, Dict, Mapping

import pytest
import requests
import yaml

from ipernity import IpernityAPI, IpernityError
from ipernity.auth import DesktopAuthHandler, WebAuthHandler


# API functions that are not tested
skipped_methods = [
    'auth.getFrob',     # only used for login
    'auth.getToken',    # only used for login
    'doc.albums.add',   # "method not found" - exists only in documentation
    'doc.search',       # Need a better test case?
    'upload.replace',   # Behaves like upload.file, bug in Ipernity?
]


basedir = os.path.dirname(os.path.dirname(__file__))
logfile = os.path.join(basedir, 'test.log')
methodlist = os.path.join(basedir, 'tested_methods.json')


log = logging.getLogger(__name__)


@pytest.fixture
def permissions(test_data) -> Dict:
    return test_data['permissions']


@pytest.fixture(scope='session')
def test_config() -> Dict:
    cfgfile = os.path.join(os.path.dirname(__file__), '.test-config.yaml')
    with open(cfgfile, 'r') as cfg:
        return yaml.load(cfg, Loader=yaml.SafeLoader)
    

@pytest.fixture(scope='session')
def test_data() -> Dict:
    datafile = os.path.join(os.path.dirname(__file__), 'data.yaml')
    with open(datafile, 'r') as data:
        return yaml.load(data, Loader=yaml.SafeLoader)


@pytest.fixture
def api(test_config: Dict, permissions: Dict, tested_methods: TestedMethods):
    config = test_config['auth']['desktop']
    api = TestAPI(
        config,
        tested_methods
    )
    if _auth_from_config(config, api):
        return api
    
    browser = IpernitySession(test_config['user']['cookies'])
    frob = api.auth.getFrob()['auth']['frob']
    browser.authorize(api.auth.auth_url(permissions, frob))
    config['token'] = api.auth.getToken(frob)['auth']['token']
    return api


@pytest.fixture
def webapi(test_config: Dict, permissions: Dict, tested_methods: TestedMethods):
    config = test_config['auth']['web']
    api = TestAPI(
        config,
        tested_methods,
        auth = 'web'
    )
    if _auth_from_config(config, api):
        return api
    
    browser = IpernitySession(test_config['user']['cookies'])
    frob = browser.authorize(api.auth.auth_url(permissions))
    config['token'] = api.auth.getToken(frob)['auth']['token']
    return api


def _auth_from_config(config: Mapping, api: IpernityAPI) -> bool:
    if api.token is not None:
        return True
    
    if 'token' in config:
        api.token = config['token']
        return True
    
    return False


@pytest.fixture
def images(api, test_data):
    imgs = []
    for name, data in test_data['images'].items():
        img = None
        if 'md5' not in data:
            path = os.path.join(os.path.dirname(__file__), name)
            log.debug('Calculating MD5 of %s', path)
            data['md5'] = md5(open(path, 'rb').read()).hexdigest()
        for doc in api.doc.checkMD5(md5 = data['md5'])['docs']['doc']:
            try:
                doc = api.doc.get(doc_id = doc['doc_id'], extra='md5')['doc']
            except IpernityError:
                continue
            if doc['owner']['user_id'] != api.user_info['user_id']:
                continue
            img = doc
            break
        
        if not img:
            id_ = api.upload_file(
                path,
                public = 0,
                title = data['title'],
                description = data['desc']
            )
            img = api.doc.get(doc_id = id_, extra='md5')['doc']
        
        img['filename'] = name
        imgs.append(img)
    
    return imgs


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
def tested_methods():
    methods = TestedMethods()
    yield methods
    methods.save(methodlist)


@pytest.fixture
def tabula_rasa(api):
    while int((docs := api.doc.getList()['docs'])['total']):
        for doc in docs['doc']:
            api.doc.delete(doc_id = doc['doc_id'])
    while int((albums := api.album.getList()['albums'])['total']):
        for album in albums['album']:
            api.album.delete(album_id = album['album_id'])


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
    def __init__(self, config, tested, auth = 'desktop'):
        self._tested_methods = tested
        super().__init__(
            config.get('api_key'),
            config.get('api_secret'),
            config.get('token'),
            auth = auth
        )
    
    def call(self, method_name, **kwargs):
        res = super().call(method_name, **kwargs)
        self._tested_methods.mark(method_name)
        return res


class IpernitySession(requests.Session):
    def __init__(self, cookies: Mapping):
        super().__init__()
        for domain, paths in cookies.items():
            for path, cookies in paths.items():
                for name, value in cookies.items():
                    self.cookies.set(name, value, domain=domain, path=path)
    
    def authorize(self, auth_url: str) -> str:
        log.info('Authorizing via %s', auth_url)
        res = self.get(auth_url, allow_redirects=False)
        mimetype = res.headers.get('Content-Type')
        log.info('Got result %d: %s', res.status_code, mimetype)
        
        if res.status_code == 200 and mimetype.startswith('text/html'):
            log.debug('Text: %s', res.text)
            html = IpernityParser()
            html.feed(res.text)
            if html.ok:
                log.info('Desktop login OK.')
                return None
            
            url = urlparse(auth_url)
            log.info('Posting authorization %s', html.params)
            res = self.request(
                html.method,
                auth_url,
                data = html.params,
                allow_redirects = False
            )
            mimetype = res.headers.get('Content-Type')
            log.info('Got result %d: %s', res.status_code, mimetype)
        
        if res.status_code == 302:
            url = res.headers.get('location')
            log.info('Got redirect to %s', url)
            if url.startswith('http://127.0.0.1'):
                frob = parse_qs(urlparse(url).query)['frob'][0]
                log.info('Returning frob %s', frob)
                return frob
        
        if mimetype.startswith('text/html'):
            log.debug('Text: %s', res.text)
        
        log.error('No frob')
        return None


class IpernityParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.parsing_form = False
        self.params = {}
        self.ok = False
    
    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]):
        if tag == 'form':
            if self.get_attr(attrs, 'name') == 'fa':
                if self.ok:
                    raise RuntimeError('Something strange happened')
                self.method = self.get_attr(attrs, 'method')
                self.parsing_form = True
        
        elif (
            self.parsing_form and
            tag == 'input' and
            self.get_attr(attrs, 'type') == 'hidden'
        ):
            self.params[self.get_attr(attrs, 'name')] = self.get_attr(attrs, 'value')
        
        elif tag == 'div' and self.get_attr(attrs, 'class') == 'ok':
            if self.params:
                raise RuntimeError('Something strange happened')
            self.ok = True
    
    def handle_endtag(self, tag: str):
        if tag == 'form' and self.parsing_form:
            if self.ok:
                raise RuntimeError('Something strange happened')
            self.parsing_form = False
    
    @staticmethod
    def get_attr(attrs: list, key: str) -> str|None:
        for k, v in attrs:
            if k == key:
                return v
        return None


