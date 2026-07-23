from unittest.mock import MagicMock, patch

import pytest
import requests
from agent_utilities.core.exceptions import MissingParameterError
from pydantic import ValidationError

from servicenow_api.api_client import Api


class MockResponse(requests.Response):
    def __init__(self, json_data, status_code=200):
        super().__init__()
        self._json_data = json_data
        self.status_code = status_code

    def json(self, **kwargs):
        return self._json_data

    def raise_for_status(self):
        pass


def test_api_missing_url():
    with pytest.raises(MissingParameterError):
        Api(url=None)


def test_api_missing_parameters():
    # If we pass nothing except url, it raises MissingParameterError
    with pytest.raises(MissingParameterError):
        Api(url="https://dev12345.service-now.com")


def test_api_oauth_exception():
    # The client issues the OAuth POST via `self._session.post` (not the
    # module-level `requests.post`) so its TLS profile applies consistently —
    # mock the session itself.
    mock_session = MagicMock()
    mock_session.post.side_effect = RuntimeError("OAuth endpoint offline")
    with patch("requests.Session", return_value=mock_session):
        with pytest.raises(RuntimeError, match="OAuth endpoint offline"):
            Api(
                url="https://dev12345.service-now.com",
                username="admin",
                password="password",
                client_id="cid",
                client_secret="csec",
            )


def test_api_construction_no_eager_network_call():
    # Client construction (token auth) must not touch the network at all —
    # no eager connectivity probe. A `Depends(get_client)` FastMCP dependency
    # that raises here surfaces only as a generic "Failed to resolve
    # dependency" RuntimeError, masking the real cause (CONCEPT reference:
    # see the NOTE in api/api_client_base.py `ServiceNowApiBase.__init__`).
    mock_session = MagicMock()
    with patch("requests.Session", return_value=mock_session):
        Api(url="https://dev12345.service-now.com", token="mock-token")
    mock_session.get.assert_not_called()


def test_api_refresh_token_validation_error():
    mock_session = MagicMock()

    with patch("requests.Session", return_value=mock_session):
        client = Api(url="https://dev12345.service-now.com", token="mock-token")
        client.auth_data = {"client_id": "cid", "client_secret": "csec"}

        # Now mock the oauth refresh POST (issued via `self._session.post`, not
        # the module-level `requests.post`) to return missing/invalid keys to
        # raise ValidationError.
        mock_bad_resp = MockResponse({"not_access_token": "oops"})
        mock_session.post.return_value = mock_bad_resp
        with pytest.raises(KeyError):
            client.refresh_auth_token()

        # If it returns access_token but missing other required fields (causing ValidationError in Pydantic)
        # Note: Authentication model requires access_token, token_type, expires_in.
        mock_partial_resp = MockResponse(
            {"access_token": "token123", "token_type": 123}
        )
        mock_session.post.return_value = mock_partial_resp
        with pytest.raises(ValidationError):
            client.refresh_auth_token()


def test_api_refresh_token_exception():
    mock_session = MagicMock()

    with patch("requests.Session", return_value=mock_session):
        client = Api(url="https://dev12345.service-now.com", token="mock-token")
        client.auth_data = {"client_id": "cid", "client_secret": "csec"}

        # Issued via `self._session.post`, not the module-level `requests.post`.
        mock_session.post.side_effect = RuntimeError("Endpoint timed out")
        with pytest.raises(RuntimeError, match="Endpoint timed out"):
            client.refresh_auth_token()
