
import pytest

def test_walk_albums(api, changes):
    n = 0
    for album in api.walk_albums():
        assert album['owner']['user_id'] == changes['user']['user_id']
        n += 1
        if n > 10:
            break
    assert n > 0

def test_walk_album_docs(api, changes):
    albid = changes['albums'][0]
    n = 0
    for doc in api.walk_album_docs(albid):
        assert doc['doc_id'] in changes['docs']
        n += 1
    assert n == len(changes['docs'])


@pytest.mark.skip('Does not work - need a better test case')
def test_walk_doc_search(api, changes):
    n = 0
    for doc in api.walk_doc_search(
        user_id = changes['user']['user_id'],#
        text = 'Test',
#        posted_min = changes['start']-10,
    ):
#        if doc['doc_id'] in changes['docs']:
        n += 1
#    assert n == len(changes['docs'])
    assert n > 0


