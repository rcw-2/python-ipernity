
import pytest


@pytest.mark.parametrize(
    'title', [
        'Testalbum 1',
        'Testalbum 2',
#        'Testalbum 3'
    ]
)
def test_create(api, changes, title):
    album = api.album.create(title = title)['album']
    changes['albums'].append(album['album_id'])
    assert album['title'] == title


def test_docs_add(api, changes):
    albid = changes['albums'][0]
    docids = ','.join(changes['docs'])
    
    res = api.album.docs.add(album_id = albid, doc_id = docids)
    assert res['album']['album_id'] == albid
    assert len(res['album']['doc']) == len(changes['docs'])
    for doc in res['album']['doc']:
        assert doc['doc_id'] in changes['docs']
    
    docs = api.album.docs.getList(album_id = albid)['album']['docs']['doc']
    assert len(docs) == len(changes['docs'])
    for albdoc, docid in zip(docs, changes['docs']):
        albdoc['doc_id'] == docid


def test_edit(api, changes):
    albid = changes['albums'][0]
    docid = changes['docs'][0]
    
    res = api.album.edit(
        album_id = albid,
        title = 'New Title',
        description = 'New Description',
        cover_id = docid
    )
    assert res['album']['title'] == 'New Title'
    assert res['album']['description'] == 'New Description'
    assert res['album']['cover']['doc_id'] == docid
    
    album_info = api.album.get(album_id = albid)['album']
    assert album_info['album_id'] == albid
    assert album_info['title'] == 'New Title'
    assert album_info['description'] == 'New Description'
    assert album_info['cover']['doc_id'] == docid


@pytest.mark.skip('Method not found - documentation bug')
def test_doc_albums_add(api, changes):
    docid = changes['docs'][0]
    docalbumids = [
        album['album_id']
        for album in api.doc.getContainers(doc_id = docid)['albums']['album']
    ]
    new_albums = [
        albid
        for albid in changes['albums']
        if albid not in docalbumids
    ]
    
    res = api.doc.albums.add(doc_id = docid, album_id = ','.join(new_albums))
    for album in res['albums']['album']:
        assert album['id'] in new_albums
        assert album['added']
        assert docid in [doc['doc_id'] for doc in album['doc']]

