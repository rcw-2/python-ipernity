"""
Python Ipernity Library

Authentication
"""

from abc import ABC, abstractmethod
from hashlib import md5
from logging import getLogger
from urllib.parse import urlencode
from typing import Any, Mapping, Optional


log = getLogger(__name__)


class AuthHandler(ABC):
    """
    Generic authentication handler
    
    Args:
        api:    The :class:`IpernityAPI` object to which the handler belongs.
    """
    def __init__(
        self,
        api: 'IpernityAPI',                                 # type: ignore # noqa: F821
    ):
        log.debug(
            'Initializing %s with API key %s',
            self.__class__.__name__,
            api._api_key
        )
        self._api = api
    
    @property
    def api(self) -> 'IpernityAPI':                         # type: ignore # noqa: F821
        """The corresponding :class:`IpernityAPI` object"""
        return self._api
    
    def _sign_request(self, method_name: Optional[str] = None, **kwargs) -> Mapping:
        """Signs a request."""
        log.debug(f'Generating signature for {method_name} {kwargs}')
        kwargs['api_key'] = self._api._api_key
        if self.api.token:
            kwargs['auth_token'] = self.api.token
        
        sig_str = ''.join([
            f'{k}{kwargs[k]}'
            for k in sorted(kwargs.keys())
            if k != 'file'
        ])
        
        if method_name:
            sig_str += method_name
        
        sig_str += self.api._api_secret
        log.debug(f'  signature string is {sig_str}')
        kwargs.update({
            'api_sig':  md5(sig_str.encode('utf-8')).hexdigest(),
        })
        return kwargs
    
    def getToken(self, frob: str, store_token: bool = True, **kwargs) -> Mapping:
        """
        Runs the :iper:`auth.getToken` API method.
        
        Args:
            frob:           String gotten via :meth:`~DesktopAuthHandler.getFrob`
                            or callback.
            store_token:    If ``True``, the token will be stored in the API object.
            kwargs:         Passed to Ipernity as additional parameters.
        """
        result = self.api.call('auth.getToken', frob = frob, **kwargs)
        if store_token:
            self.api.token = result['auth']
        return result
    
    def checkToken(self, auth_token: str, **kwargs) -> Mapping:
        """Runs the :iper:`auth.checkToken` API method"""
        return self.api.call(
            'auth.checkToken',
            auth_token = auth_token,
            **kwargs
        )
    
    @abstractmethod
    def auth_url(self, perms: Mapping, **kwargs):
        """
        URL to pass to a web browser for authorization.
        
        Args:
            perms:  Dictionary used to generate the ``perm_XXX`` parameters to the
                    authorization URL. The keys can be ``doc``, ``blog`` etc.
        """
        pass
    
    def _build_url(self, url: str, **kwargs: str) -> str:
        url = f'{url}?' + urlencode(kwargs)
        log.debug(f'Returning url {url}')
        return url


class DesktopAuthHandler(AuthHandler):
    """
    Desktop authentication handler.
    
    Args:
        api:    The :class:`IpernityAPI` object to which the handler belongs.
    
    .. seealso::
        *   `Desktop Authentication <http://www.ipernity.com/help/api/auth.soft.html>`_
            at Ipernity
    """
    def getFrob(self) -> Mapping:
        """Get frob for authentication"""
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
    
    .. seealso::
        *   `Web Authentication <http://www.ipernity.com/help/api/auth.web.html>`_
            at Ipernity
    """
    def __init__(self, api: 'IpernityAPI'):                 # type: ignore # noqa: F821
        super().__init__(api)
    
    def auth_url(self, perms: Mapping) -> str:
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

