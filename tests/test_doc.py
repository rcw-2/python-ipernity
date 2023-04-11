
import random

def test_doc_set(api, changes):
    docid = random.choice(changes['docs'])
    
    res = api.doc.set(
        doc_id = docid,
        title = 'New Title',
        description = 'New description'
    )
    assert res['doc']['doc_id'] == docid
    assert res['doc']['title'] == 'New Title'
    assert res['doc']['description'] == 'New description'
    
    doc = api.doc.get(doc_id = docid)['doc']
    assert doc['title'] == 'New Title'
    assert doc['description'] == 'New description'

