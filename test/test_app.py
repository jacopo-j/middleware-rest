import pytest
import uuid
import base64
from webapp import create_app

TEST_USER_CREDENTIALS = {
    "username": uuid.uuid4().hex,  # Prevent conflicts with existing users
    "password": "testpw"
}

TEST_CLIENT_DATA = {
    "client_name": "testclient",
    "client_uri": "http://0.0.0.0",
    "redirect_uri": "http://0.0.0.0",
    "response_type": "code",
    "scope": "profile",
    "token_endpoint_auth_method": "client_secret_basic",
    "grant_type": "password\ncode\nimplicit"
}

TEST_TOKEN_DATA = {
    **TEST_USER_CREDENTIALS,
    "scope": "profile"
}

oauth_client = None
oauth_token = ""


@pytest.fixture(scope="module")
def client():
    app = create_app()
    app.config["TESTING"] = True
    testing_client = app.test_client()
    ctx = app.app_context()
    ctx.push()
    yield testing_client
    ctx.pop()
    

def test_user_login_not_registered(client):
    response = client.post(
        "auth/login",
        data=TEST_USER_CREDENTIALS,
        follow_redirects=True
    )
    assert response.status_code == 401


def test_user_registration_success(client):
    response = client.post(
        "api/register",
        data=TEST_USER_CREDENTIALS,
        follow_redirects=True
    )
    assert response.status_code == 200


def test_user_double_registration(client):
    response = client.post(
        "api/register",
        data=TEST_USER_CREDENTIALS,
        follow_redirects=True
    )
    assert response.status_code == 400
    

def test_user_login_wrong_password(client):
    response = client.post(
        "auth/login",
        data={**TEST_USER_CREDENTIALS, "password": "testwrongpw"},
        follow_redirects=True
    )
    assert response.status_code == 401


def test_client_creation_not_loggedin(client):
    response = client.post(
        "auth/create_client",
        query_string=TEST_CLIENT_DATA,
        follow_redirects=True
    )
    assert response.status_code == 401
    

def test_user_login_success(client):
    response = client.post(
        "auth/login",
        data=TEST_USER_CREDENTIALS,
        follow_redirects=True
    )
    assert response.status_code == 200


def test_client_creation_success(client):
    global oauth_client
    response = client.post(
        "auth/create_client",
        query_string=TEST_CLIENT_DATA,
        follow_redirects=True
    )
    assert response.status_code == 200
    oauth_client = response.get_json()


def test_request_token_password_wrong_client(client):
    response = client.post(
        "auth/token",
        data={**TEST_TOKEN_DATA, "grant_type": "password"},
        headers={"Authorization": "Basic " + base64.b64encode(
            "{client_id}:wrongclientsecret".format(**oauth_client).encode()
        ).decode()
                 },
        follow_redirects=True
    )
    assert response.status_code == 401


def test_request_token_password_success(client):
    global oauth_token
    response = client.post(
        "auth/token",
        data={**TEST_TOKEN_DATA, "grant_type": "password"},
        headers={"Authorization": "Basic " + base64.b64encode(
                "{client_id}:{client_secret}".format(**oauth_client).encode()
            ).decode()
        },
        follow_redirects=True
    )
    assert response.status_code == 200
    oauth_token = response.get_json()["access_token"]


def test_list_users_wrong_token(client):
    response = client.get(
        "api/users",
        headers={"Authorization": "Bearer wrongtoken123"},
        follow_redirects=True
    )
    assert response.status_code == 401


def test_list_users_success(client):
    response = client.get(
        "api/users",
        headers={"Authorization": "Bearer " + oauth_token},
        follow_redirects=True
    )
    assert response.status_code == 200
