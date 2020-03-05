import os
import tempfile
import pytest
from webapp import create_app


@pytest.fixture
def client():
    app = create_app()
    app.config['TESTING'] = True
    testing_client = app.test_client()
    ctx = app.app_context()
    ctx.push()
    yield testing_client
    ctx.pop()


def test_skeleton(client):
    response = client.get('api/users', follow_redirects=True)


