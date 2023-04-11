

def test_delete(api, changes):
    for docid in changes['docs']:
        api.doc.delete(doc_id = docid)
    
    for albid in changes['albums']:
        api.album.delete(album_id = albid)

