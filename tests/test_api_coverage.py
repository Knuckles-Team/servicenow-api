import pytest
import requests
from unittest.mock import MagicMock, patch
from servicenow_api.api_client import Api
from servicenow_api.servicenow_models import Response


@pytest.fixture
def mock_session():
    with (
        patch("requests.Session") as mock_sess,
        patch("requests.post") as mock_post,
        patch("requests.get") as mock_get,
    ):

        session = mock_sess.return_value

        # Mock OAuth response
        auth_resp = MagicMock(spec=requests.Response)
        auth_resp.json.return_value = {"access_token": "mock_token"}
        auth_resp.status_code = 200
        mock_post.return_value = auth_resp

        # Mock subscribers check
        sub_resp = MagicMock(spec=requests.Response)
        sub_resp.status_code = 200
        sub_resp.json.return_value = {"result": []}
        mock_get.return_value = sub_resp
        session.get.return_value = sub_resp

        yield session


def test_api_init_basic_auth(mock_session):
    client = Api(url="http://test.com", username="user", password="pass")
    assert client.headers["Authorization"].startswith("Basic")
    assert client.base_url == "http://test.com"


def test_api_init_oauth(mock_session):
    client = Api(
        url="http://test.com",
        username="user",
        password="pass",
        client_id="id",
        client_secret="secret",
    )
    assert client.token == "mock_token"
    assert client.headers["Authorization"] == "Bearer mock_token"


def test_get_application(mock_session):
    client = Api(url="http://test.com", username="user", password="pass")

    # Mock specific response for get_application
    app_resp = MagicMock(spec=requests.Response)
    app_resp.status_code = 200
    app_resp.json.return_value = {"result": {"application_id": "app123"}}
    mock_session.get.return_value = app_resp

    response = client.get_application(application_id="app123")
    assert isinstance(response, Response)
    # The result should be parsed into CMDBService (as per api_client.py:554)
    assert response.result is not None


def test_get_cmdb(mock_session):
    client = Api(url="http://test.com", username="user", password="pass")

    cmdb_resp = MagicMock(spec=requests.Response)
    cmdb_resp.status_code = 200
    cmdb_resp.json.return_value = {"result": {"cmdb_id": "cmdb123"}}
    mock_session.get.return_value = cmdb_resp

    response = client.get_cmdb(cmdb_id="cmdb123")
    assert response.result.cmdb_id == "cmdb123"


def test_delete_cmdb_relation(mock_session):
    client = Api(url="http://test.com", username="user", password="pass")

    del_resp = MagicMock(spec=requests.Response)
    del_resp.status_code = 204
    del_resp.content = b""
    mock_session.delete.return_value = del_resp

    response = client.delete_cmdb_relation(
        className="cmdb_ci_server", sys_id="123", rel_sys_id="456"
    )
    assert response.result == {"status": "deleted"}


if __name__ == "__main__":
    pytest.main([__file__])
