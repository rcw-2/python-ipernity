"""
Exceptions
============

Exception hierarchy:

.. inheritance-diagram:: ipernity.exceptions
    :parts: 1

"""

from __future__ import annotations

from typing import Mapping


class IpernityError(Exception):
    """
    Base class for Ipernity exceptions.
    
    .. versionchanged:: 0.2.0
        IpernityError is the the parent of several specialized exceptions. The
        Ipernity-specific attributes were moved to :class:`APIRequestError`.
    
    .. property:: message
        :type: str
        
        Contains the error message.
    """


class UnknownMethod(IpernityError):
    """
    An unknown method was called.
    
    .. versionadded:: 0.2.0
    
    .. property:: method
        :type: str

        The method that was called.
    """
    def __init__(self, method: str|None = None, message: str|None = None):
        if message is None:
            message = f'Unknown method {method}'
        self.method = method
        self.message = message
        super().__init__(message)


class APIRequestError(IpernityError):
    """
    An API request did not succeed.
    
    .. versionadded:: 0.2.0
    
    .. property:: status
        :type: str
        
        Result status of the request.
        
        The value ``'httperror'`` indicates that the HTTP request to the API
        failed. Otherwise, this attribute contains the status returned by
        Ipernity.
    
    .. property:: code
        :type: str|int
        
        Error code.
        
        If :attr:`status` is ``'httperror'``, this attribute contains the HTTP
        result code. Otherwise, it is the error code returned by Ipernity.
    
    .. property:: message
        :type: str
        
        Error message returned by Ipernity, or generic message for HTTP errors.
    
    .. property:: method
        :type: str
        
        Method that was called.
    
    .. property:: params
        :type: dict[str,str|int]
        
        Parameters with that the method was called.
        
        .. warning::
            This may contain confidential information like ``access_token``!
    """
    def __init__(
        self,
        status: str = 'error',
        code: int = 0,
        message: str = 'Unspecified Error',
        method: str|None = None,
        params: Mapping|None = None,
    ):
        self.status = status
        self.code = int(code)
        self.message = message
        self.method = method
        self.params = params
        super().__init__(f'Ipernity status {status} {code}: {message}')


class UploadError(IpernityError):
    """
    :iper:`upload.checkTickets` returned invalid ticket data during upload.
    
    .. versionadded:: 0.2.0
    
    .. property:: filename
        :type: str
        
        File that was being uploaded.
    
    .. property:: ticket
        :type: str
        
        Ipernity's upload ticket.
    """
    def __init__(
        self,
        filename: str|None = None,
        ticket: str|None = None,
        message: str|None = None
    ):
        if message is None:
            message = f'Error uploading {filename}, ticket {ticket}'
        self.filename = filename
        self.ticket = ticket
        self.message = message