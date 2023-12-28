
import pytest

from ipernity import APIRequestError, UnknownMethod


def test_unknown_method(api):
    with pytest.raises(UnknownMethod):
        api.call('unknown.method')
    with pytest.raises(UnknownMethod):
        api.unknown.method()
    with pytest.raises(AttributeError):
        api._unknown.method()
    with pytest.raises(AttributeError):
        api.unknown._method()


def test_api_request_error(api):
    with pytest.raises(APIRequestError):
        api.doc.get(doc_id = 1)

