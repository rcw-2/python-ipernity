

def test_echo(api):
    echo = api.test.echo(echo = 'Hallo Echo!')
    assert echo['echo'] == 'Hallo Echo!'


def test_hello(api):
    hello = api.test.hello()
    assert hello['hello'] == 'hello world!'

