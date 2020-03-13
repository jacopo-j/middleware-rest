import io
import os

import boto3
import pytest
import uuid
import base64

from botocore.stub import Stubber
from moto import mock_s3
from webapp import create_app
from webapp.modules import client_s3, config

BUCKET = config["bucket_name"]

IMAGE_FILE = b'GIF89a\x01\x00\x01\x00\x00\xff\x00,\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02\x00;'

TEST_USER_CREDENTIALS = {
    "username": uuid.uuid4().hex,  # Prevent conflicts with existing users
    "password": "testpw"
}

TEST_CLIENT_DATA = {
    "client_name": "testclient",
    "client_uri": "http://0.0.0.0",
    "redirect_uri": "http://0.0.0.0",
    "response_type": "code",
    "scope": "read write",
    "token_endpoint_auth_method": "client_secret_basic",
    "grant_type": "password\ncode\nimplicit"
}

TEST_TOKEN_DATA = {
    **TEST_USER_CREDENTIALS,
    "scope": "read write"
}

oauth_client = None
oauth_token_password = ""
max_id = 2


@pytest.fixture(scope='module')
def aws_credentials():
    """Mocked AWS Credentials for moto."""
    os.environ['AWS_ACCESS_KEY_ID'] = 'testing'
    os.environ['AWS_SECRET_ACCESS_KEY'] = 'testing'
    os.environ['AWS_SECURITY_TOKEN'] = 'testing'
    os.environ['AWS_SESSION_TOKEN'] = 'testing'


@pytest.fixture(scope="module", autouse=True)
def moto_boto(aws_credentials):
    # setup: start moto server and create the bucket
    mocks3 = mock_s3()
    mocks3.start()
    res = boto3.resource('s3')
    res.create_bucket(Bucket=BUCKET)
    yield
    # teardown: stop moto server
    mocks3.stop()


@pytest.fixture(scope="module")
def client(moto_boto):
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
    global max_id
    global oauth_token_password
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
    oauth_token_password = response.get_json()["access_token"]
    max_id += 1


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
        headers={"Authorization": "Bearer " + oauth_token_password},
        follow_redirects=True
    )
    assert response.status_code == 200


def test_upload_image_success(client):
    # Upload image
    client.post(
        "api/upload",
        data={"title": "test", "image": (io.BytesIO(IMAGE_FILE), "file.jpg")},
        headers={"Authorization": "Bearer " + oauth_token_password},
        follow_redirects=True
    )
    # Check the image exists
    response = client.get(
        "api/user/3/image/1",
        headers={"Authorization": "Bearer " + oauth_token_password},
        follow_redirects=True
    )
    assert response.status_code == 200
    assert response.json["title"] == "test"


def test_upload_image_wrong_token(client):
    response = client.post(
        "api/upload",
        data={"title": "test", "image": (io.BytesIO(b"abcdef"), "file.jpg")},
        headers={"Authorization": "Bearer wrongtoken123"},
        follow_redirects=True
    )
    assert response.status_code == 401


def test_upload_delete_image_success(client):
    # Check the image exists
    response = client.get(
        "api/user/3/image/1",
        headers={"Authorization": "Bearer " + oauth_token_password},
        follow_redirects=True
    )
    assert response.status_code == 200
    assert response.json["title"] == "test"

    # Delete image
    client.delete(
        "api/user/3/image/1",
        headers={"Authorization": "Bearer " + oauth_token_password},
        follow_redirects=True
    )

    # Check no image is present
    response = client.get(
        "api/user/3/image/1",
        headers={"Authorization": "Bearer " + oauth_token_password},
        follow_redirects=True
    )
    assert response.status_code == 404


def test_upload_delete_image_wrong_token(client):
    # Upload image
    response = client.post(
        "api/upload",
        data={"title": "to_delete", "image": (io.BytesIO(b"abcdef"), "file.jpg")},
        headers={"Authorization": "Bearer wrongtoken123"},
        follow_redirects=True
    )

    assert response.status_code == 401

    # Delete image
    response = client.delete(
        "api/user/3/image/1",
        data={"title": "to_delete", "image": (io.BytesIO(b"abcdef"), "file.jpg")},
        headers={"Authorization": "Bearer wrongtoken123"},
        follow_redirects=True
    )

    assert response.status_code == 401


def test_get_delete_image_not_present(client):
    # Get image not present
    response = client.get(
        "api/user/3/image/1",
        data={"title": "to_delete", "image": (io.BytesIO(b"abcdef"), "file.jpg")},
        headers={"Authorization": "Bearer " + oauth_token_password},
        follow_redirects=True
    )

    assert response.status_code == 404

    # Delete image not present
    response = client.delete(
        "api/user/3/image/1",
        data={"title": "to_delete", "image": (io.BytesIO(b"abcdef"), "file.jpg")},
        headers={"Authorization": "Bearer " + oauth_token_password},
        follow_redirects=True
    )

    assert response.status_code == 404

    # Get image no user
    response = client.get(
        "api/user/100/image/1",
        data={"title": "to_delete", "image": (io.BytesIO(b"abcdef"), "file.jpg")},
        headers={"Authorization": "Bearer " + oauth_token_password},
        follow_redirects=True
    )

    assert response.status_code == 404


def test_get_images(client):
    response = client.get(
        "api/user/3",
        headers={"Authorization": "Bearer " + oauth_token_password},
        follow_redirects=True
    )

    assert response.status_code == 200
    assert response.json["id"] == '3'


def test_get_images_wrong_token(client):
    response = client.get(
        "api/user/3",
        headers={"Authorization": "Bearer wrongtoken123"},
        follow_redirects=True
    )

    assert response.status_code == 401


def test_get_images_user_not_present(client):
    response = client.get(
        "api/user/{}".format(max_id+1),
        headers={"Authorization": "Bearer " + oauth_token_password},
        follow_redirects=True
    )

    assert response.status_code == 404
