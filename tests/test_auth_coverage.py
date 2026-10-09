import os
from unittest.mock import patch

import pytest
from agent_connector_sdk.exceptions import AuthError, UnauthorizedError

from servicenow_api.auth import get_client


def test_auth_missing_instance():
    with patch.dict(os.environ, {}, clear=True):
        with pytest.raises(RuntimeError, match="SERVICENOW_INSTANCE not set"):
            get_client()


def test_auth_no_method():
    with patch.dict(
        os.environ, {"SERVICENOW_INSTANCE": "https://dev12345.service-now.com"}
    ):
        with pytest.raises(ValueError, match="No auth method"):
            get_client(username=None, password=None)


def test_auth_oidc_delegation_success():
    from agent_connector_sdk.auth.tokens import AccessToken

    with patch.dict(
        os.environ, {"SERVICENOW_INSTANCE": "https://dev12345.service-now.com"}
    ):
        with patch("servicenow_api.auth._is_delegation_enabled", return_value=True):
            with patch(
                "agent_connector_sdk.auth.delegation.current_user_token",
                return_value="subject-token",
            ):
                with patch(
                    "agent_connector_sdk.auth.delegation.exchange_token",
                    return_value=AccessToken(
                        value="mock-oidc-token", ttl_seconds=300, expires_at=0
                    ),
                ) as mock_exchange:
                    with patch("servicenow_api.auth.Api") as mock_api_cls:
                        client = get_client()
                        assert client is not None
                        assert mock_exchange.called
                        _, kwargs = mock_exchange.call_args
                        assert kwargs["subject_token"] == "subject-token"
                        assert mock_api_cls.called
                        _, kwargs = mock_api_cls.call_args
                        assert kwargs["url"] == "https://dev12345.service-now.com"
                        assert kwargs["token"] == "mock-oidc-token"
                        assert kwargs["tls_profile"].verify_enabled is True


def test_auth_oidc_delegation_failure():
    with patch.dict(
        os.environ, {"SERVICENOW_INSTANCE": "https://dev12345.service-now.com"}
    ):
        with patch("servicenow_api.auth._is_delegation_enabled", return_value=True):
            with patch(
                "agent_connector_sdk.auth.delegation.current_user_token",
                return_value="subject-token",
            ):
                with patch(
                    "agent_connector_sdk.auth.delegation.exchange_token",
                    side_effect=Exception("Delegation server offline"),
                ):
                    with pytest.raises(RuntimeError, match="Token exchange failed"):
                        get_client()


def test_auth_basic_auth_success():
    with patch.dict(
        os.environ, {"SERVICENOW_INSTANCE": "https://dev12345.service-now.com"}
    ):
        with patch("servicenow_api.auth._is_delegation_enabled", return_value=False):
            with patch("servicenow_api.auth.Api") as mock_api_cls:
                client = get_client(username="admin", password="password123")
                assert client is not None
                assert mock_api_cls.called
                _, kwargs = mock_api_cls.call_args
                assert kwargs["username"] == "admin"
                assert kwargs["password"] == "password123"
                assert kwargs["url"] == "https://dev12345.service-now.com"


def test_auth_client_credentials_success():
    with patch.dict(
        os.environ,
        {
            "SERVICENOW_INSTANCE": "https://dev12345.service-now.com",
            "SERVICENOW_GRANT_TYPE": "client_credentials",
        },
    ):
        with patch("servicenow_api.auth._is_delegation_enabled", return_value=False):
            with patch("servicenow_api.auth.Api") as mock_api_cls:
                client = get_client(
                    client_id="my-client-id", client_secret="mock-client-secret"
                )
                assert client is not None
                assert mock_api_cls.called
                _, kwargs = mock_api_cls.call_args
                assert kwargs["client_id"] == "my-client-id"
                assert kwargs["client_secret"] == "mock-client-secret"
                assert kwargs["grant_type"] == "client_credentials"
                assert kwargs["url"] == "https://dev12345.service-now.com"
                # client_credentials must not require or pass a user login
                assert "username" not in kwargs or kwargs["username"] is None
                assert "password" not in kwargs or kwargs["password"] is None


def test_auth_basic_auth_failure_autherror():
    with patch.dict(
        os.environ, {"SERVICENOW_INSTANCE": "https://dev12345.service-now.com"}
    ):
        with patch("servicenow_api.auth._is_delegation_enabled", return_value=False):
            with patch(
                "servicenow_api.auth.Api",
                side_effect=AuthError("Invalid username/password"),
            ):
                with pytest.raises(RuntimeError, match="AUTHENTICATION ERROR"):
                    get_client(username="admin", password="wrongpassword")


def test_auth_basic_auth_failure_unauthorizederror():
    with patch.dict(
        os.environ, {"SERVICENOW_INSTANCE": "https://dev12345.service-now.com"}
    ):
        with patch("servicenow_api.auth._is_delegation_enabled", return_value=False):
            with patch(
                "servicenow_api.auth.Api",
                side_effect=UnauthorizedError("Blocked by OAuth policy"),
            ):
                with pytest.raises(RuntimeError, match="AUTHENTICATION ERROR"):
                    get_client(username="admin", password="wrongpassword")
