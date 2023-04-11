

def test_method_list(api):
    mlist = api.api.methods.getList()
    selected = [
        m
        for m in mlist['methods']['method']
        if m['name'] in ['user.get', 'test.echo', 'doc.get']
    ]
    assert len(selected) == 3

def test_method(api):
    name = 'test.echo'
    minfo = api.api.methods.get(method = name)
    assert minfo['method']['name'] == name

