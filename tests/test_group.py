
import pytest


@pytest.fixture
def group(api):
    return api.group.getList()['groups']['group'][0]


@pytest.fixture
def image(images):
    return images[0]


def test_group_add_remove(api, image, group):
    res = api.group.docs.add(
        group_id = group['group_id'],
        doc_id = image['doc_id']
    )
    assert res['group']['doc'][0]['doc_id'] == image['doc_id']
    
    for grp in api.doc.getContainers(doc_id = image['doc_id'])['groups']['group']:
        if grp['group_id'] == group['group_id']:
            break
    else:
        pytest.fail(f"Image {image['doc_id']} is not in group {group['group_id']}")
    
    for img in api.group.docs.getList(group_id = group['group_id'])['group']['docs']['doc']:
        if img['doc_id'] == image['doc_id']:
            break
    else:
        pytest.fail(f"Image {image['doc_id']} not found in group {group['group_id']}")
    
    res = api.group.docs.remove(
        group_id = group['group_id'],
        doc_id = image['doc_id']
    )
    assert res['group']['docs'][0]['doc_id'] == image['doc_id']

    for grp in api.doc.getContainers(doc_id = image['doc_id'])['groups']['group']:
        assert grp['group_id'] != group['group_id']
    
    for img in api.group.docs.getList(
        group_id = group['group_id']
    )['group']['docs'].get('doc', []):
        assert img['doc_id'] != image['doc_id']


