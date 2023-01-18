import pytest
from flask import g, session
from tjenaFlask.db import get_db


def test_register(client, app):
    '''client.get() makes a GET request and returns the Response object returned by Flask. 
    Similarly, client.post() makes a POST request, converting the data dict into form data.'''
    assert client.get('/auth/register').status_code == 200 
    response = client.post(
        '/auth/register', data={'username': 'a', 'password': 'a'}
    )
    assert response.headers["Location"] == "/auth/login" #headers will have a Location header with the login URL when the register view redirects to the login view.

    with app.app_context():
        assert get_db().execute(
            "SELECT * FROM user WHERE username = 'a'",
        ).fetchone() is not None


@pytest.mark.parametrize(('username', 'password', 'message'), ( #pytest.mark.parametrize tells Pytest to run the same test function with different arguments
    ('', '', b'Username is required.'),
    ('a', '', b'Password is required.'),
    ('test', 'test', b'already registered'),
))
def test_register_validate_input(client, username, password, message):
    response = client.post(
        '/auth/register',
        data={'username': username, 'password': password}
    )
    assert message in response.data


def test_login(client, auth):
    assert client.get('/auth/login').status_code == 200
    response = auth.login()
    assert response.headers["Location"] == "/"

    with client:
        client.get('/')
        assert session['user_id'] == 1 #Tests for the login view are similar to those for register. Rather than testing the data in the database, session should have user_id set after logging in.
        assert g.user['username'] == 'test'


@pytest.mark.parametrize(('username', 'password', 'message'), (
    ('a', 'test', b'Incorrect username.'),
    ('test', 'a', b'Incorrect password.'),
))
def test_login_validate_input(auth, username, password, message):
    response = auth.login(username, password)
    assert message in response.data


def test_logout(client, auth):
    auth.login()

    #Using client in a with block allows accessing context variables such as session after the response is returned. 
    # Normally, accessing session outside of a request would raise an error.
    with client:
        auth.logout()
        assert 'user_id' not in session