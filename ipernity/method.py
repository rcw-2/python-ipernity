"""
Method Class
==============
"""

from typing import Any


class IpernityMethod:
    """
    Helper class to enable the `APIobj.my.method(**)` syntax.
    
    Args:
        api:    The corresponding API object.
        name:   Name of the (partial) method.
    """
    
    def __init__(
        self,
        api: 'IpernityAPI',                                 # type: ignore # noqa: F821
        name: str
    ):
        self._api = api
        self._name = name
    
    def __getattr__(self, name: str) -> 'IpernityMethod':
        """Returns an IpernityMethod object for the given method"""
        if name.startswith('_'):
            raise AttributeError(f'Attribute {name} not found')
        
        return IpernityMethod(self._api, f'{self._name}.{name}')
    
    def __call__(self, **kwargs: Any) -> Any:
        """Actually calls the method."""
        return self._api.call(self._name, **kwargs)


