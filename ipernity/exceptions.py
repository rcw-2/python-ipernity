"""
Python Ipernity API

Exceptions
"""

from typing import Mapping


class IpernityError(Exception):
    """
    Base class for Ipernity exceptions.
    
    .. property:: message
        Contains the error message.
    """


class UnknownMethod(IpernityError):
    """
    An unknown method was called.
    
    .. property:: method
        The method that was called.
    """
    def __init__(self, method: str|None = None, message: str|None = None):
        if message is None:
            message = f'Unknown method {method}'
        self.method = method
        self.message = message
        super().__init__(message)


class QueryError(IpernityError):
    """
    An API call returned a not 'ok' status.
    
    .. property:: status
        Status returned by Ipernity.
    
    .. property:: code
        Error code returned by Ipernity.
    
    .. property:: message
        Error message returned by Ipernity.
    
    .. property:: method
        Method that was called.
    
    .. property:: params
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


class InvalidTicket(IpernityError):
    """
    :iper:`upload.checkTickets` returned invalid ticket data.
    
    .. property:: ticket
    """
    def __init__(self, ticket: str|None = None, message: str|None = None):
        if message is None:
            message = f'Invalid ticket {ticket}'
        self.ticket = ticket
        self.message = message