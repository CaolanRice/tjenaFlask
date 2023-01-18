from tjenaFlask import create_app


def test_config():
    assert not create_app().testing
    assert create_app({'TESTING': True}).testing

#tests the hello function in the factory app (init.py)
def test_hello(client):
    response = client.get('/hello')
    assert response.data == b'Hello, World!'