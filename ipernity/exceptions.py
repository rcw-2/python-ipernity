"""
Python Ipernity API

Exceptions
"""


class IpernityError(Exception):
    def __init__(
        self,
        status: str = 'error',
        code: int = 0,
        message: str = 'Unspecified Error',
    ):
        self.status = status
        self.code = int(code)
        self.message = message
        super().__init__(f'Ipernity status {status} {code}: {message}')

