from unittest.mock import MagicMock, patch

import pytest
import requests
from agent_utilities.core.exceptions import (
    AuthError,
    MissingParameterError,
    ParameterError,
    UnauthorizedError,
)
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
    # Test lines 466-471 (OAuth exception)
    with patch("requests.post", side_effect=RuntimeError("OAuth endpoint offline")):
        with pytest.raises(RuntimeError, match="OAuth endpoint offline"):
            Api(
                url="https://dev12345.service-now.com",
                username="admin",
                password="password",
                client_id="cid",
                client_secret="csec",
            )


def test_api_subscriber_status_codes():
    # Mocking standard subscriber checks in __init__
    mock_session = MagicMock()

    # 1. 403 Forbidden -> raises UnauthorizedError
    mock_response_403 = MagicMock()
    mock_response_403.status_code = 403
    mock_session.get.return_value = mock_response_403
    with patch("requests.Session", return_value=mock_session):
        with pytest.raises(UnauthorizedError):
            Api(url="https://dev12345.service-now.com", token="mock-token")

    # 2. 401 Unauthorized -> raises AuthError
    mock_response_401 = MagicMock()
    mock_response_401.status_code = 401
    mock_session.get.return_value = mock_response_401
    with patch("requests.Session", return_value=mock_session):
        with pytest.raises(AuthError):
            Api(url="https://dev12345.service-now.com", token="mock-token")

    # 3. 404 Not Found -> raises ParameterError
    mock_response_404 = MagicMock()
    mock_response_404.status_code = 404
    mock_session.get.return_value = mock_response_404
    with patch("requests.Session", return_value=mock_session):
        with pytest.raises(ParameterError):
            Api(url="https://dev12345.service-now.com", token="mock-token")


def test_api_refresh_token_validation_error():
    # Mock subscriber check to succeed on init
    mock_session = MagicMock()
    mock_response_200 = MagicMock()
    mock_response_200.status_code = 200
    mock_session.get.return_value = mock_response_200

    with patch("requests.Session", return_value=mock_session):
        client = Api(url="https://dev12345.service-now.com", token="mock-token")
        client.auth_data = {"client_id": "cid", "client_secret": "csec"}

        # Now mock oauth refresh POST to return missing or invalid keys to raise ValidationError
        mock_bad_resp = MockResponse({"not_access_token": "oops"})
        with patch("requests.post", return_value=mock_bad_resp):
            with pytest.raises(KeyError):
                client.refresh_auth_token()

        # If it returns access_token but missing other required fields (causing ValidationError in Pydantic)
        # Note: Authentication model requires access_token, token_type, expires_in.
        mock_partial_resp = MockResponse(
            {"access_token": "token123", "token_type": 123}
        )
        with patch("requests.post", return_value=mock_partial_resp):
            with pytest.raises(ValidationError):
                client.refresh_auth_token()


def test_api_refresh_token_exception():
    # Mock subscriber check to succeed on init
    mock_session = MagicMock()
    mock_response_200 = MagicMock()
    mock_response_200.status_code = 200
    mock_session.get.return_value = mock_response_200

    with patch("requests.Session", return_value=mock_session):
        client = Api(url="https://dev12345.service-now.com", token="mock-token")
        client.auth_data = {"client_id": "cid", "client_secret": "csec"}

        with patch("requests.post", side_effect=RuntimeError("Endpoint timed out")):
            with pytest.raises(RuntimeError, match="Endpoint timed out"):
                client.refresh_auth_token()
