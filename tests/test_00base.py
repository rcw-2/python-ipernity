import json
import logging
import webbrowser
from time import sleep

from ipernity import IpernityAPI, IpernityError


log = logging.getLogger(__name__)


def test_00login(perms, files):
    with open(files['key'], 'r') as kf:
        app = json.load(kf)
    
    # Check if we have a valid token
    try:
        with open(files['token'], 'r') as tf:
            auth = json.load(tf)
        api = IpernityAPI(
            app['api_key'],
            app['api_secret'],
            token = auth['token']
        )
        api.auth.checkToken(auth['token'])
        return        
    except (OSError, json.JSONDecodeError, IpernityError):
        # An error means that we cannot use the token data,
        # so we start the login procedure.
        pass
    
    # If the existing token is valid, 
    api = IpernityAPI(app['api_key'], app['api_secret'])
    frob = api.auth.getFrob()['auth']['frob']
    url = api.auth.auth_url(perms, frob)

    print('Starting web browser for authorization...')
    log.debug(f'Starting browser with {url}')
    webbrowser.open_new(url)
    sleep(1)
    input('Press <Enter> after authorizing access in browser... ')

    auth = api.auth.getToken(frob)['auth']
    print('Token retrieved, you can close the browser now.')
    with open(files['token'], 'w') as tf:
        json.dump(auth, tf)


def test_user(token, api, changes):
    token_info = api.auth.checkToken(auth_token = token['token'])['auth']
    for key in ['user_id', 'username']:
        assert token_info['user'][key] == token['user'][key]
    for target, perm in token['permissions'].items():
        if perm == 'none':
            continue
        assert token_info['permissions'][target] == perm
    
    user_info = api.user.get(user_id = token['user']['user_id'])
    for key in ['user_id', 'username']:
        assert user_info['user'][key] == token['user'][key]


def test_quota(token, api):
    quota = api.account.getQuota()['quota']
    assert quota['user_id'] == token['user']['user_id']


