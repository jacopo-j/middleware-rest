import pytest
from webapp import create_app


@pytest.fixture(scope="module")
def client():
    app = create_app()
    app.config["TESTING"] = True
    testing_client = app.test_client()
    ctx = app.app_context()
    ctx.push()
    yield testing_client
    ctx.pop()


def test_user_registration_and_login(client):

    # User registration
    response = client.post(
        "api/register",
        data={"username": "testuser1", "password": "testpw"},
        follow_redirects=True
    )
    assert response.status_code == 200

    # Double registration with same username
    response = client.post(
        "api/register",
        data={"username": "testuser1", "password": "testpw"},
        follow_redirects=True
    )
    assert response.status_code == 400

    # Login with wrong username
    response = client.post(
        "auth/login",
        data={"username": "testuser2", "password": "testpw"},
        follow_redirects=True
    )
    assert response.status_code == 401

    # Login with wrong password
    response = client.post(
        "auth/login",
        data={"username": "testuser1", "password": "testwrongpw"},
        follow_redirects=True
    )
    assert response.status_code == 401

    # Login with correct username & password
    response = client.post(
        "auth/login",
        data={"username": "testuser1", "password": "testpw"},
        follow_redirects=True
    )
    assert response.status_code == 200


def test_list_users(client):  # TODO: does not work

    # Before login
    response = client.get(
        "api/users",
        follow_redirects=True
    )
    assert response.status_code == 401

    response = client.post(
        "auth/login",
        data={"username": "documentation", "password": "documentation"},
        follow_redirects=True
    )
    assert response.status_code == 200

    # After login
    response = client.get(
        "api/users",
        follow_redirects=True
    )
    assert response.status_code == 200
