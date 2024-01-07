"""
Ipernity API shell
"""

import json
import os
import readline
import shlex
import sys
from configparser import ConfigParser
from argparse import ArgumentParser, Namespace
from typing import Mapping

from ipernity import IpernityAPI, IpernityError


def args() -> ArgumentParser:
    a = ArgumentParser(
        'ipernity',
        description = 'CLI for Ipernity API calls'
    )
    a.add_argument(
        '-c', '--config',
        help = 'Configuration file',
        action = 'store'
    )
    a.add_argument(
        '-k', '--api-key',
        help = 'API key',
        action = 'store'
    )
    a.add_argument(
        '-s', '--api-secret',
        help = 'API secret',
        action = 'store'
    )
    a.add_argument(
        '-t', '--api-token',
        help = 'API token',
        action = 'store'
    )
    return a


def get_api_init(opts: Namespace) -> tuple[str, str, str]:
    # From environment
    key = os.environ.get('IPERNITY_API_KEY')
    secret = os.environ.get('IPERNITY_API_SECRET')
    token = os.environ.get('IPERNITY_API_TOKEN')
    
    # From config file
    filename = opts.config or os.path.expanduser('~/.ipernity.ini')
    if os.path.isfile(filename):
        c = ConfigParser()
        c.read(filename)
        if 'ipernity' in c:
            key = c['ipernity'].get('api key', key)
            secret = c['ipernity'].get('api secret', secret)
            token = c['ipernity'].get('api token', token)
    
    # From command line options
    if opts.api_key is not None:
        key = opts.api_key
    if opts.api_secret is not None:
        secret = opts.api_secret
    if opts.api_token is not None:
        token = opts.api_token
    
    return key, secret, token


def help():
    print("""
        To call an Ipernity method, enter
        
            <method.name> <param1>=<value1> <param2>=<value2> ...
        
        where <paramN> is the name of the method parameter and <valueN> the
        corresponding value. If a value contains spaces, enclose it in single
        or double quotes. Note that there must not be spaces around the "=".
        
        To obtain an application token, enter
        
            login <resource>=[read|write|delete] ...
        
        See http://www.ipernity.com/help/api/permissions.html for possible
        values. Omitted scopes get zero permissions (i.e. only public content
        can be read).
        """
    )


def login(api: IpernityAPI, permissions: Mapping):
    import webbrowser
    
    frob = api.auth.getFrob()['auth']['frob']
    url = api.auth.auth_url(permissions, frob)
    print('Starting web browser for authorization...')
    old_stdout = os.dup(1)
    old_stderr = os.dup(2)
    os.close(1)
    os.close(2)
    webbrowser.open_new(url)
    os.dup2(old_stdout, 1)
    os.dup2(old_stderr, 2)
    input('Press <Enter> after authorizing access in browser... ')
    api.auth.getToken(frob)
    print('Token retrieved, you can close the browser now.')


def main():
    key, secret, token = get_api_init(args().parse_args())
    
    api = IpernityAPI(key, secret, token)
    print('Starting Ipernity API interactive mode...')
    
    while True:
        try:
            line = input('Ipernity> ').strip()
        except EOFError:
            print()
            sys.exit(0)
        
        if line == '':
            continue
        
        words = shlex.split(line)
        method = words[0]
        
        if method == 'help':
            help()
            continue
        
        if method == 'exit':
            sys.exit(0)
        
        words = words[1:]
        params = {}
        for word in words:
            k, v = word.split('=', 2)
            params[k] = v
        
        if method == 'login':
            login(api, params)
            continue
        
        try:
            res = api.call(method, **params)
            print(json.dumps(res, indent = 4))
        except IpernityError as e:
            print(e, file = sys.stderr)


main()

