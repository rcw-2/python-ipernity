import json
import logging
import webbrowser
from time import sleep

import pytest

from ipernity import IpernityAPI, IpernityError


log = logging.getLogger(__name__)


def test_00login(test_config, api):
    assert api.token is not None
    assert api.user_info['username'] == test_config['user']['username']


def test_00login_web(test_config, webapi):
    assert webapi.token is not None
    assert webapi.user_info['username'] == test_config['user']['username']


def test_user(test_config, api, changes):
    token_info = api.auth.checkToken(auth_token = api.token)['auth']
    for key in ['user_id', 'username']:
        assert token_info['user'][key] == test_config['user'][key]
    # for target, perm in token['permissions'].items():
    #     if perm == 'none':
    #         continue
    #     assert token_info['permissions'][target] == perm
    
    user_info = api.user.get(user_id = api.user_info['user_id'])
    for key in ['user_id', 'username']:
        assert user_info['user'][key] == test_config['user'][key]


def test_quota(test_config, api):
    quota = api.account.getQuota()['quota']
    assert quota['user_id'] == test_config['user']['user_id']


