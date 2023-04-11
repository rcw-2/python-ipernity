
import os

import pytest


filename = os.path.join(os.path.dirname(__file__), 'tischdecke.jpg')
filename2 = os.path.join(os.path.dirname(__file__), 'tischdecke.jpg')

@pytest.mark.parametrize(
    'filename, title, description',
    [
        (
            os.path.join(os.path.dirname(__file__), 'tischdecke.jpg'),
            'Tischdecke 1',
            '(leer)',
        ),
        (
            os.path.join(os.path.dirname(__file__), 'tischdecke2.jpg'),
            'Tischdecke 2',
            'Beschreibung für den Test',
        )
    ],
)
def test_upload(
    api,
    changes,
    filename,
    title,
    description,
):
    docid = api.upload_file(
        filename,
        public = 0,
        title = title,
        description = description,
    )
    
    doc = api.doc.get(doc_id = docid)['doc']
    assert doc['title'] == title
    assert doc['description'] == description
    changes['docs'].append(docid)
    changes.update({'replace_docid': docid})


