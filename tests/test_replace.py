
import os

import pytest


filename = os.path.join(os.path.dirname(__file__), 'tischdecke2.jpg')


@pytest.mark.skip('Probably bug in Ipernity')
def test_replace(api, changes):
    docid = api.replace_file(filename, doc_id = changes['replace_docid'])
    assert docid == changes['replace_docid']


