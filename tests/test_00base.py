import json
import logging
import webbrowser
from time import sleep

import pytest

from ipernity import IpernityAPI, IpernityError
from ipernity.auth import DesktopAuthHandler, WebAuthHandler


log = logging.getLogger(__name__)


def test_00login(test_config, api, permissions):
    assert api.token is not None
    assert api.user_info['username'] == test_config['user']['username']
    assert api.permissions['doc'] == permissions['doc']


def test_00login_web(test_config, webapi, permissions):
    assert webapi.token is not None
    assert webapi.user_info['username'] == test_config['user']['username']
    assert webapi.permissions['doc'] == permissions['doc']


def test_auth_options(test_config):
    api_key = test_config['auth']['desktop']['api_key']
    api_secret = test_config['auth']['desktop']['api_secret']
    
    api = IpernityAPI(api_key, api_secret, auth='desktop')
    assert isinstance(api.auth, DesktopAuthHandler)
    assert api.token is None
    assert api.user_info is None
    assert api.permissions is None
    
    api = IpernityAPI(api_key, api_secret, auth='web')
    assert isinstance(api.auth, WebAuthHandler)
    assert api.token is None
    assert api.user_info is None
    assert api.permissions is None
    
    with pytest.raises(ValueError):
        api = IpernityAPI(api_key, api_secret, auth='oauth')


def test_user(test_config, api, permissions):
    token_info = api.auth.checkToken(auth_token = api.token)['auth']
    
    for key in ['user_id', 'username']:
        assert api.user_info[key] == test_config['user'][key]
        assert token_info['user'][key] == test_config['user'][key]
    
    for target, perm in permissions.items():
        if perm == 'none':
            assert target not in token_info['permissions']
        else:
            assert token_info['permissions'][target] == perm
    
    user_info = api.user.get(user_id = api.user_info['user_id'])
    for key in ['user_id', 'username']:
        assert user_info['user'][key] == test_config['user'][key]


def test_quota(test_config, api):
    quota = api.account.getQuota()['quota']
    assert quota['user_id'] == test_config['user']['user_id']


def test_new_key(api):
    api.api_key = 'bogus_data'
    assert api.token is None


def test_new_secret(api):
    api.api_secret = 'bogus_data'
    assert api.token is None


def test_permissions(test_data, permissions, api):
    assert api.has_permissions(None)
    assert api.has_permissions(permissions)
    assert not api.has_permissions(test_data['non_permissions'])
    
    api.token = None
    assert not api.has_permissions(permissions)
    assert not api.has_permissions(None)


def test_incomplete_token(test_config, test_data, permissions, api):
    api.token = {'token': test_config['auth']['desktop']['token']}
    assert api.token == test_config['auth']['desktop']['token']
    assert api._user is None
    assert api._perm is None

