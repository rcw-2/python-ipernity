"""
Authentication and Authorization
==================================

The ``auth`` module defines the authentication handlers to be used with

.. inheritance-diagram:: ipernity.auth
    :parts: 1
    :top-classes: ipernity.auth.AuthHandler

The authentication handlers provide access to the ``auth.*`` API methods and

"""

from __future__ import annotations

from abc import ABC, abstractmethod
from hashlib import md5
from logging import getLogger
from urllib.parse import urlencode
from typing import Mapping, TYPE_CHECKING

import requests

if TYPE_CHECKING:
    from .api import IpernityAPI, api_arg

log = getLogger(__name__)


class AuthHandler(ABC):
    """
    Generic authentication handler
    
    Args:
        api:    The API object to which the handler belongs.
    """
    def __init__(
        self,
        api: IpernityAPI,
    ):
        log.debug(
            'Initializing %s with API key %s',
            self.__class__.__name__,
            api._api_key
        )
        self._api = api
    
    @property
    def api(self) -> IpernityAPI:
        """The corresponding :class:`IpernityAPI` object"""
        return self._api
    
    def getToken(self, frob: str, store_token: bool = True, **kwargs: api_arg) -> dict:
        """
        Runs the :iper:`auth.getToken` API method.
        
        By default, also stores the token and user info in the API object.
        
        Args:
            frob:           String gotten via :meth:`~DesktopAuthHandler.getFrob`
                            or callback.
            store_token:    If ``True`` (the default), the token and user info
                            will be stored in the API object (:attr:`api`).
            kwargs:         Passed to Ipernity as additional parameters.
        
        Return:
            The result of the API call.
        
        .. versionchanged: 0.1.3
            Parameter ``store_token``
        """
        result = self.api.call('auth.getToken', frob = frob, **kwargs)
        if store_token:
            self.api.token = result['auth']
        return result
    
    def checkToken(self, auth_token: str, **kwargs: api_arg) -> dict:
        """Runs the :iper:`auth.checkToken` API method"""
        return self.api.call(
            'auth.checkToken',
            auth_token = auth_token,
            **kwargs
        )
    
    @abstractmethod
    def auth_url(self, perms: Mapping, **kwargs: str) -> str:
        """
        URL to pass to a web browser for authorization.
        
        Args:
            perms:  Dictionary used to generate the ``perm_XXX`` parameters to the
                    authorization URL. The keys can be ``doc``, ``blog`` etc.
        """
        pass
    
    def do_request(
        self,
        url: str,
        method_name: str,
        method_args: Mapping[str, api_arg]
    ) -> requests.Response:
        """
        Signs and runs a request.
        
        This is part of ``AuthHandler`` to make an OAuth handler possible, as
        OAuth uses a different format for signing and authentication info.
        
        Args:
            url:            Request URL.
            method_name:    The method to be called (needed for signing).
            method_args:    Arguments of the method call.
        """
        data = self._sign_request(method_name, **method_args)
        log.debug(
            'Calling %s with %s',
            url,
            ', '.join([
                # Censor potentially sensitive data
                f'{k}=XXX' if k in ['api_key', 'auth_token'] else f'{k}={v}'
                for k, v in data.items()
            ])
        )
        
        # Do request, use POST if required
        if int(self.api.__methods__[method_name]['authentication'].get('post', "0")):
            if 'file' in data:
                with open(data['file'], 'rb') as f:
                    del data['file']
                    return requests.post(
                        url,
                        data = data,
                        files = {'file': f}
                    )
            
            return requests.post(url, data = data)
        
        return requests.get(url, params = data)
    
    def _sign_request(self, method_name: str | None = None, **kwargs: api_arg) -> dict:
        """Signs a request."""
        log.debug(f'Generating signature for {method_name} {kwargs}')
        kwargs['api_key'] = self.api.api_key
        if self.api.token:
            kwargs['auth_token'] = self.api.token
        
        sig_str = ''.join([
            f'{k}{kwargs[k]}'
            for k in sorted(kwargs.keys())
            if k != 'file'
        ])
        
        if method_name:
            sig_str += method_name
        
        sig_str += self.api.api_secret
        # potentially dangerous log.debug(f'  signature string is {sig_str}')
        kwargs.update({
            'api_sig':  md5(sig_str.encode('utf-8')).hexdigest(),
        })
        return kwargs
    
    def _build_url(self, url: str, **kwargs: api_arg) -> str:
        url = f'{url}?' + urlencode(kwargs)
        log.debug(f'Returning url {url}')
        return url


class DesktopAuthHandler(AuthHandler):
    """
    Desktop authentication handler.
    
    Args:
        api:    The API object to which the handler belongs.
    
    .. seealso::
        *   `Desktop Authentication <http://www.ipernity.com/help/api/auth.soft.html>`_
            at Ipernity
    """
    def getFrob(self) -> dict:
        """
        Get frob for authentication
        
        See 
        """
        return self.api.call('auth.getFrob')
    
    def auth_url(self, perms: Mapping, frob: str) -> str:
        """
        Authorization URL.
        
        See `Ipernity Permissions <http://www.ipernity.com/help/api/permissions.html>`_
        for a description.
        
        Args:
            perms:  Dictionary used to generate the ``perm_XXX`` parameters to the
                    authorization URL. The keys can be ``doc``, ``blog`` etc.
            frob:   Data retrieved from :meth:`~DesktopAuthHandler.getFrob`
        """
        params = {
            'api_key':  self.api._api_key,
            'frob':     frob,
        }
        for name, value in perms.items():
            if name.startswith('perm_'):
                params[name] = value
            else:
                params['perm_' + name] = value
        return self._build_url(
            'http://www.ipernity.com/apps/authorize',
            **self._sign_request(**params)
        )


class WebAuthHandler(AuthHandler):
    """
    Authentication for web applications
    
    Args:
        api:    The :class:`IpernityAPI` object to which the handler belongs.
    
    .. versionadded:: 0.1.3
    
    .. seealso::
        *   `Web Authentication <http://www.ipernity.com/help/api/auth.web.html>`_
            at Ipernity
    """
    def __init__(self, api: IpernityAPI):
        super().__init__(api)
    
    def auth_url(self, perms: Mapping[str, str]) -> str:
        """
        Authorization URL.
        
        See `Ipernity Permissions <http://www.ipernity.com/help/api/permissions.html>`_
        for a description.
        
        Args:
            perms:  Dictionary used to generate the ``perm_XXX`` parameters to the
                    authorization URL. The keys can be ``doc``, ``blog`` etc.
        """
        params = {
            'api_key':  self.api._api_key,
        }
        for name, value in perms.items():
            if name.startswith('perm_'):
                params[name] = value
            else:
                params['perm_' + name] = value
        return self._build_url(
            'http://www.ipernity.com/apps/authorize',
            **self._sign_request(**params)
        )


auth_methods = {
    'desktop':  DesktopAuthHandler,
    'web':      WebAuthHandler,
}

