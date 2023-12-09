
import os

import pytest


def test_00clean(tabula_rasa, api):
    assert int(api.user.get()['user']['count']['docs']) == 0


def test_upload(images, test_data, changes):
    for img in images:
        assert img['title'] == test_data['images'][img['filename']]['title']
        assert img['description'] == test_data['images'][img['filename']]['desc']
        changes['docs'].append(img['doc_id'])
        changes.update({'replace_docid': img['doc_id']})


