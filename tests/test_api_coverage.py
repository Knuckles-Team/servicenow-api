from unittest.mock import MagicMock, patch

import pytest
import requests

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

        # The client issues OAuth/refresh POSTs via `self._session.post` (not the
        # module-level `requests.post`) so its TLS profile applies consistently —
        # mock the session's own post, matching `session.get` above.
        session.post.return_value = auth_resp

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


# --- Regression coverage: systemic double /api/api/ URL bug --------------------------
# api_client_base.py sets self.url = f"{base_url}/api" (api_client_base.py:433); methods
# must build f"{self.url}/..." never f"{self.url}/api/...". Assert the exact URL used.


def test_batch_request_url_has_no_doubled_api_segment(mock_session):
    client = Api(url="http://test.com", username="user", password="pass")

    resp = MagicMock(spec=requests.Response)
    resp.status_code = 200
    resp.json.return_value = {"batch_request_id": "1", "serviced_requests": []}
    mock_session.post.return_value = resp

    client.batch_request(rest_requests=[])
    called_url = mock_session.post.call_args.kwargs["url"]
    assert called_url == "http://test.com/api/now/v1/batch"
    assert "/api/api/" not in called_url


def test_get_devops_onboarding_status_url_has_no_doubled_api_segment(mock_session):
    client = Api(url="http://test.com", username="user", password="pass")

    resp = MagicMock(spec=requests.Response)
    resp.status_code = 200
    resp.json.return_value = {"result": {"status": "complete"}}
    mock_session.get.return_value = resp

    client.get_devops_onboarding_status(id="evt123")
    called_url = mock_session.get.call_args.kwargs["url"]
    assert called_url == "http://test.com/api/sn_devops/devops/onboarding/status"
    assert "/api/api/" not in called_url


def test_get_ci_lifecycle_status_url_has_no_doubled_api_segment(mock_session):
    client = Api(url="http://test.com", username="user", password="pass")

    resp = MagicMock(spec=requests.Response)
    resp.status_code = 200
    resp.json.return_value = {"result": True}
    mock_session.get.return_value = resp

    client.get_ci_lifecycle_status(sys_id="ci123")
    called_url = mock_session.get.call_args.kwargs["url"]
    assert called_url == "http://test.com/api/now/cilifecyclemgmt/statuses/ci123"
    assert "/api/api/" not in called_url


# --- Regression coverage: DELETE crashing on ServiceNow's empty 204 body -------------


def test_delete_table_record_handles_empty_204(mock_session):
    client = Api(url="http://test.com", username="user", password="pass")

    del_resp = MagicMock(spec=requests.Response)
    del_resp.status_code = 204
    del_resp.content = b""
    mock_session.delete.return_value = del_resp

    response = client.delete_table_record(
        table="incident", table_record_sys_id="inc123"
    )
    assert response.result == {"status": "deleted"}


def test_delete_change_request_handles_empty_204(mock_session):
    client = Api(url="http://test.com", username="user", password="pass")

    del_resp = MagicMock(spec=requests.Response)
    del_resp.status_code = 204
    del_resp.content = b""
    mock_session.delete.return_value = del_resp

    response = client.delete_change_request(change_request_sys_id="chg123")
    assert response.result == {"status": "deleted"}


def test_delete_ci_lifecycle_action_handles_empty_204(mock_session):
    client = Api(url="http://test.com", username="user", password="pass")

    del_resp = MagicMock(spec=requests.Response)
    del_resp.status_code = 204
    del_resp.content = b""
    mock_session.delete.return_value = del_resp

    response = client.delete_ci_lifecycle_action(
        actionName="retire", requestorId="req1", sysIds="ci1,ci2"
    )
    assert response.result == {"status": "deleted"}


# --- Regression coverage: get_stats stats field rejecting a JSON bool ----------------


def test_get_stats_accepts_bool_stats(mock_session):
    client = Api(url="http://test.com", username="user", password="pass")

    resp = MagicMock(spec=requests.Response)
    resp.status_code = 200
    resp.json.return_value = {"result": {"stats": {"count": 5}}}
    mock_session.get.return_value = resp

    # Previously raised a pydantic ValidationError: stats was declared str-only.
    response = client.get_stats(table_name="incident", stats=True)
    assert response.result == {"stats": {"count": 5}}
    called_params = mock_session.get.call_args.kwargs["params"]
    assert called_params["sysparm_count"] == "true"


# --- Regression coverage: refresh_auth_token opaque TypeError under basic auth -------


def test_refresh_auth_token_requires_oauth_credentials(mock_session):
    from agent_utilities.core.exceptions import MissingParameterError

    client = Api(url="http://test.com", username="user", password="pass")
    assert client.auth_data is None

    with pytest.raises(MissingParameterError, match="OAuth client credentials"):
        client.refresh_auth_token()


# --- Phase-5 coverage gap-close: Incident Management update/delete -------------------


def test_update_incident(mock_session):
    client = Api(url="http://test.com", username="user", password="pass")

    resp = MagicMock(spec=requests.Response)
    resp.status_code = 200
    resp.json.return_value = {"result": {"sys_id": "inc123", "priority": "1"}}
    mock_session.patch.return_value = resp

    response = client.update_incident(incident_id="inc123", data={"priority": "1"})
    assert response.result.sys_id == "inc123"
    called_url = mock_session.patch.call_args.kwargs["url"]
    assert called_url == "http://test.com/api/now/table/incident/inc123"


def test_delete_incident_handles_empty_204(mock_session):
    client = Api(url="http://test.com", username="user", password="pass")

    del_resp = MagicMock(spec=requests.Response)
    del_resp.status_code = 204
    del_resp.content = b""
    mock_session.delete.return_value = del_resp

    response = client.delete_incident(incident_id="inc123")
    assert response.result == {"status": "deleted"}


if __name__ == "__main__":
    pytest.main([__file__])
