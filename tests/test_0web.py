import json
import logging
import webbrowser
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
from time import sleep
from os import environ

import pytest

from ipernity import IpernityAPI, IpernityError


log = logging.getLogger(__name__)


@pytest.mark.skipif(
    environ.get('TEST_WEB', '').upper() != 'TRUE',
    reason = 'Set TEST_WEB=true in environment to run web login test'
)
def test_web_login(perms, files):
    with open(files['webkey'], 'r') as kf:
        app = json.load(kf)
    
    api = IpernityAPI(app['api_key'], app['api_secret'], auth = 'web')
    url = api.auth.auth_url(perms)
    log.debug('Authentication URL %s', url)
    app = HTTPServer(('', 5678), CallbackHandler)
    assert webbrowser.open(url)
    app.handle_request()
    assert app.frob
    auth = api.auth.getToken(app.frob)['auth']
    assert isinstance(auth, dict)
    assert 'token' in auth


class CallbackHandler(BaseHTTPRequestHandler):
    
    def do_GET(self):
        if self.path.startswith('/callback'):
            frob = parse_qs(
                urlparse(self.path).query
            )['frob'][0]
            title = 'frob received'
            self.send_response(200)
        else:
            frob = None
            title = 'error'
            self.send_response(500)
        
        self.send_header('Content-Type', 'text/html')
        self.end_headers()
        self.wfile.write((
            '<html>'
            f'<head><title>{title}</title></head>'
            f'<body><h1>{title}</h1><p>frob={frob}</p></body>'
            '</html>'
        ).encode('utf-8'))
        self.wfile.close()
        
        self.server.frob = frob
