"""
Python Ipernity API
"""

import json
import os
from logging import getLogger
from time import sleep
from typing import Any, Dict, Iterable, Mapping, Optional, Union

import requests

from .auth import AuthHandler, auth_methods
from .method import IpernityMethod
from .exceptions import IpernityError


api_arg = Union[str, float, int]

log = getLogger(__name__)

methodsfile = os.path.join(
    os.path.dirname(__file__),
    'methods.json'
)
with open(methodsfile, 'r') as mf:
    _methods = json.load(mf)


class IpernityAPI:
    """
    Encapsulates Ipernity functionality.
    
    Args:
        api_key:    The API key obtained from Ipernity.
        api_secret: The secret belonging to the API key.
        token:      API token. Can be given as a string or as ``dict``. When
                    given as a dict, the actual token is extracted as
                    ``token['token']``.
        auth:       Authentication methop, can be ``desktop`` or ``web``.
        url:        API URL, should normally be left alone.
    
    .. seealso::
        * `Ipernity API methods <http://www.ipernity.com/help/api>`_
    """
    
    # Methods data retrieved from http://api.ipernity.com/api/api.methods.getList/json
    __methods__ = _methods
    
    def __init__(
        self,
        api_key: str,
        api_secret: str,
        token: Union[str, Dict, None] = None,
        auth: str = 'desktop',
        url: str = 'http://api.ipernity.com/api/',
    ):
        log.debug('Creating API object with key %s', api_key)
        self._api_key = api_key
        self._api_secret = api_secret
        self.token = token
        self._url = url
        if auth in auth_methods:
            self._auth = auth_methods[auth](self)
        else:
            raise ValueError(f'Authentication method {auth} is not supported')
    
    def __getattr__(self, name: str) -> IpernityMethod:
        """Returns an IpernityMethod object for the given method"""
        if name.startswith('_'):
            raise AttributeError(f'Attribute {name} not found')
        
        return IpernityMethod(self, name)
    
    @property
    def auth(self) -> AuthHandler:
        """The authentication handler"""
        return self._auth
    
    @property
    def token(self) -> str:
        """
        The authentication token
        
        When setting, the new value can be given as a string or as ``dict``.
        If given as a dict, the actual token is extracted as ``token['token']``.
        """
        return self._token
    
    @token.setter
    def token(self, value: Union[str, Dict, None]):
        if isinstance(value, dict):
            self._token = value['token']
            if 'user' in value:
                self._user = value['user']
            else:
                self._user = None
        else:
            self._token = value
            self._user = None
    
    @property
    def user_info(self) -> Optional[dict]:
        """Information about the current user"""
        if self._user is None:
            if self.token is not None:
                auth = self.auth.checkToken(self.token)['auth']
                self._user = auth['user']
        return self._user
    
    def call(self, method_name: str, **kwargs: api_arg) -> Mapping:
        """
        Makes an API call.
        
        Args:
            method_name:    API method to call
            kwargs:         API arguments
        
        Raises:
            HTTPError:      HTTP access failed.
            IpernityError:  API returned an error.
        """
        if method_name not in self.__methods__:
            raise IpernityError(message = f'Unknown method {method_name}')
        
        url = self._url + method_name + '/json'
        data = self.auth._sign_request(method_name, **kwargs)
        log.debug(
            'Calling %s with %s',
            url,
            ', '.join([
                f'{k}=XXX' if k in ['api_key', 'auth_token'] else f'{k}={v}'
                for k, v in data.items()
            ])      # Censor potencially sensitive data
        )
        
        if int(self.__methods__[method_name]['authentication'].get('post', "0")):
            if 'file' in data:
                with open(data['file'], 'rb') as f:
                    del data['file']
                    response = requests.post(
                        url,
                        data = data,
                        files = {'file': f}
                    )
            else:
                response = requests.post(url, data = data)
        else:
            response = requests.get(url, params = data)
        response.raise_for_status()
        
        result = response.json()
        if result['api']['status'] != 'ok':
            raise IpernityError(
                result['api']['status'],
                result['api']['code'],
                result['api']['message']
                + f', method: {method_name}, params: {data}'
            )
        
        log.debug(f'Returning {result}')
        return result
    
    def upload_file(self, filename: str, **kwargs: api_arg) -> str:
        """
        Simplified interface to uploading a file
        
        Args:
            filename:   The file to be uploaded. Can be relative or absolute.
            kwargs:     Additional attributes for :iper:`upload.file`.
            
        Returns:
            The ``doc_id`` of the uploaded file.
        """                                                 # noqa: E501
        ticket = self.upload.file(file=filename, **kwargs)['ticket']
        done = False
        while not done:
            status = self.upload.checkTickets(tickets = ticket)['tickets']['ticket'][0]
            if status['id'] != ticket:
                raise IpernityError(
                    message = 'Bad id {}, expecting {}'.format(status['id'], ticket)
                )
            if int(status.get('invalid', '0')):
                raise IpernityError(message = f'Ticket {ticket} invalid')
            done = int(status.get('done', '0'))
            if done:
                id_ = status['doc_id']
            else:
                sleep(int(status['eta']))
        log.debug('Got id=%s for filename=%s', id_, filename)
        return id_
    
    def _replace_file(self, filename: str, **kwargs: api_arg) -> str:
        """
        Simplified interface to uploading a file
        
        Does not work, so it is hidden.
        """
        ticket = self.upload.replace(file=filename, **kwargs)['ticket']
        done = False
        while not done:
            status = self.upload.checkTickets(tickets = ticket)['tickets']['ticket'][0]
            if status['id'] != ticket:
                raise IpernityError(
                    message = 'Bad id {}, expecting {}'.format(status['id'], ticket)
                )
            if int(status.get('invalid', '0')):
                raise IpernityError(message = f'Ticket {ticket} invalid')
            done = int(status.get('done', '0'))
            if done:
                id_ = status['doc_id']
            else:
                sleep(int(status['eta']))
        
        return id_
    
    def walk_data(
        self,
        method_name: str,
        elem_name: Optional[str] = None,
        **kwargs: api_arg
    ) -> Iterable[Dict]:
        """
        Iterates over an arbitrary API search/list.
        
        ``walk_data`` guesses the structure of the returned JSON object from the
        API method used. If this does not work, the ``elem_name`` argument can
        be given to specify the object keys:
        
        *   If ``elem_name`` contains dots, the last part is taken to be the
            innermost key that points to the list of elements to iterate over,
            while the preceding parts specify the outer keys.
        *   If ``elem_name`` does not contain dots, the returned JSON is assumed
            to contain a key "``elem_name``+s" pointing to an object that
            contains a key "``elem_name``" that contains the list of results.
        
        Args:
            method_name:    Search method to call. The method must accept
                            the ``page`` argument.
            elem_name:      Name of list elements.
            kwargs:         Argument for the search method. Use ``per_page``
                            to set the number of returned elements per method
                            call.
        Yields:
            ``dict`` containing the element data.
        """
        if elem_name is None:
            # Guess element name if not given.
            mparts = method_name.split('.')
            if len(mparts) == 2:
                elem_name = mparts[0]
                list_name = [elem_name + 's']
            else:
                list_name = mparts[0:-1]
                elem_name = mparts[-2][:-1]
        else:
            if '.' in elem_name:
                mparts = elem_name.split('.')
                list_name = mparts[:-1]
                elem_name = mparts[-1]
            else:
                list_name = [elem_name + 's']
        
        if 'page' in kwargs:
            page = kwargs['page']
            del kwargs['page']
        else:
            page = 1
        pages = page       # total pages
        
        while page <= pages:
            log.debug(f'Fetching page {page} of {method_name} {kwargs}')
            res = self.call(method_name, page = page, **kwargs)
            for key in list_name:
                res = res[key]
            if 'pages' in res:
                pages = int(res['pages'])
            else:
                total = int(res['total'])
                per_page = int(res['per_page'])
                pages = total // per_page
                if total % per_page:
                    pages += 1
            
            if elem_name in res:
                yield from res[elem_name]
            else:
                log.debug('No key %s in result', elem_name)
            page += 1

    def walk_albums(self, **kwargs: api_arg) -> Iterable[Dict]:
        """
        Iterates over a user's albums.
        
        See the `album.getList documentation
        <http://www.ipernity.com/help/api/method/album.getList>`_
        for possible arguments.
        """
        return self.walk_data('album.getList', **kwargs)
    
    def walk_album_docs(self, album_id: int, **kwargs: api_arg) -> Iterable[Dict]:
        """
        Iterates over the documents of an album.
        
        See the `album.docs.getList documentation
        <http://www.ipernity.com/help/api/method/album.docs.getList>`_
        for optional arguments.
        
        Args:
            album_id:   The album's ID.
            kwargs:     Additional arguments for :iper:`album.docs.getList`
        
        """
        return self.walk_data(
            'album.docs.getList',
            album_id = album_id,
            **kwargs
        )
        
    def walk_doc_search(self, **kwargs: api_arg) -> Iterable[Dict]:
        """
        Iterates over a search result.
        
        See the `doc.search documentation
        <http://www.ipernity.com/help/api/method/doc.search>`_
        for possible arguments.
        """
        return self.walk_data('doc.search', **kwargs)
    
    def walk_docs(self, **kwargs: api_arg) -> Iterable[Dict]:
        """
        Iterates over a user's documents.
        
        See the `doc.getList documentation
        <http://www.ipernity.com/help/api/method/doc.getList>`_
        for possible arguments.
        """
        return self.walk_data('doc.getList', **kwargs)
    
    def walk_folders(self, **kwargs: api_arg) -> Iterable[Dict]:
        """
        Iterates over a user's folders.
        
        See the `folder.getList documentation
        <http://www.ipernity.com/help/api/method/folder.getList>`_
        for possible arguments.
        """
        return self.walk_data('folder.getList', **kwargs)
    
    def walk_folder_albums(self, folder_id: int, **kwargs: api_arg) -> Iterable[Dict]:
        """
        Iterates over the albums of a folder.
        
        See the `folder.albums.getList documentation
        <http://www.ipernity.com/help/api/method/folder.albums.getList>`_
        for optional arguments.
        
        Args:
            folder_id:  The folder's ID.
            kwargs:     Additional arguments for :iper:`folder.albums.getList`
        
        """
        return self.walk_data(
            'folder.albums.getList',
            folder_id = folder_id,
            **kwargs
        )
    



