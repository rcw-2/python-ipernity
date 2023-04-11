
import pytest

from ipernity import IpernityError


def test_unknown_method(api):
    with pytest.raises(IpernityError):
        api.unknown.method()

