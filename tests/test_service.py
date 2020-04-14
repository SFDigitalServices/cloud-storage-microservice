# pylint: disable=redefined-outer-name
"""Tests for microservice"""
import json
import jsend
import pytest
import boto3
from moto import mock_s3
from falcon import testing
import service.microservice

CLIENT_HEADERS = {
    "ACCESS_KEY": "1234567"
}

AWS_ACCESS_KEY_ID = "12345"
AWS_SECRET_ACCESS_KEY = "shhhhh!"
AWS_BUCKET_NAME = "its-a-secret"
LOCAL_FILE_PATH = "tests/resources/ninja.png"
OBJECT_NAME = "dirname/ninja.png"

@pytest.fixture()
def client():
    """ client fixture """
    return testing.TestClient(app=service.microservice.start_service(), headers=CLIENT_HEADERS)

@pytest.fixture
def mock_env_access_key(monkeypatch):
    """ mock environment access key """
    monkeypatch.setenv("ACCESS_KEY", CLIENT_HEADERS["ACCESS_KEY"])
    monkeypatch.setenv("BUCKETEER_AWS_ACCESS_KEY_ID", AWS_ACCESS_KEY_ID)
    monkeypatch.setenv("BUCKETEER_AWS_SECRET_ACCESS_KEY", AWS_SECRET_ACCESS_KEY)
    monkeypatch.setenv("BUCKETEER_AWS_BUCKET_NAME", AWS_BUCKET_NAME)

@pytest.fixture
def mock_env_no_access_key(monkeypatch):
    """ mock environment with no access key """
    monkeypatch.delenv("ACCESS_KEY", raising=False)

@pytest.fixture
@mock_s3
def amazon_s3():
    """ sets up amazon s3 mock """
    client = boto3.client(
        "s3",
        aws_access_key_id=AWS_ACCESS_KEY_ID,
        aws_secret_access_key=AWS_SECRET_ACCESS_KEY
    )
    client.create_bucket(Bucket=AWS_BUCKET_NAME)
    with open(LOCAL_FILE_PATH, "rb") as f: # pylint: disable=invalid-name
        client.upload_fileobj(f, AWS_BUCKET_NAME, OBJECT_NAME)

def test_welcome(client, mock_env_access_key):
    # pylint: disable=unused-argument
    # mock_env_access_key is a fixture and creates a false positive for pylint
    """Test welcome message response"""
    response = client.simulate_get('/welcome')
    assert response.status_code == 200

    expected_msg = jsend.success({'message': 'Welcome'})
    assert json.loads(response.content) == expected_msg

    # Test welcome request with no ACCESS_KEY in header
    client_no_access_key = testing.TestClient(service.microservice.start_service())
    response = client_no_access_key.simulate_get('/welcome')
    assert response.status_code == 403

def test_welcome_no_access_key(client, mock_env_no_access_key):
    # pylint: disable=unused-argument
    # mock_env_no_access_key is a fixture and creates a false positive for pylint
    """Test welcome request with no ACCESS_key environment var set"""
    response = client.simulate_get('/welcome')
    assert response.status_code == 403


def test_default_error(client, mock_env_access_key):
    # pylint: disable=unused-argument
    """Test default error response"""
    response = client.simulate_get('/some_page_that_does_not_exist')

    assert response.status_code == 404

    expected_msg_error = jsend.error('404 - Not Found')
    assert json.loads(response.content) == expected_msg_error

@mock_s3
def test_file(mock_env_access_key, client):
    # pylint: disable=unused-argument
    """Test file functionality"""

    # set up amazon s3 mock
    s3_client = boto3.client(
        "s3",
        aws_access_key_id=AWS_ACCESS_KEY_ID,
        aws_secret_access_key=AWS_SECRET_ACCESS_KEY
    )
    s3_client.create_bucket(Bucket=AWS_BUCKET_NAME)
    with open(LOCAL_FILE_PATH, "rb") as f: # pylint: disable=invalid-name
        s3_client.upload_fileobj(f, AWS_BUCKET_NAME, OBJECT_NAME)

    # non provider specified
    response = client.simulate_get(
        '/file',
        params={'name': 'foo.png'}
    )
    assert response.status_code == 500

    # retrieve non existing file
    response = client.simulate_get(
        '/file',
        params={
            'name': 'non-existant-file.png',
            'provider': 'bucketeer'
        }
    )
    print(response.text)
    assert response.status_code == 404

    # invalid provider
    response = client.simulate_get(
        '/file',
        params={
            'name': 'non-existant-file.png',
            'provider': 'icloud'
        }
    )
    print(response.text)
    assert response.status_code == 500

    # retrieve png which was uploaded in setup
    response = client.simulate_get(
        '/file',
        params={
            'name': OBJECT_NAME,
            'provider': 'bucketeer'
        }
    )
    assert response.status_code == 200
    assert response.headers['content-type'] == 'image/png'

    # api call with missing parameter
    response = client.simulate_get('/file')
    assert response.status_code == 500
    assert response.json['status'] == "error"

    # boto3 client throws unexpected error
    bucket = boto3.resource('s3').Bucket(AWS_BUCKET_NAME) # pylint: disable=no-member
    for key in bucket.objects.all():
        key.delete()
    bucket.delete()
    response = client.simulate_get(
        '/file',
        params={
            'name': OBJECT_NAME,
            'provider': 'bucketeer'
        }
    )
    assert response.status_code == 500
