import os
from unittest.mock import patch

import pytest
from agent_utilities.core.exceptions import AuthError, UnauthorizedError

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
    with patch.dict(
        os.environ, {"SERVICENOW_INSTANCE": "https://dev12345.service-now.com"}
    ):
        with patch(
            "agent_utilities.mcp.delegated_auth.is_delegation_enabled",
            return_value=True,
        ):
            with patch(
                "agent_utilities.mcp.delegated_auth.get_delegated_token",
                return_value="mock-oidc-token",
            ) as mock_get_token:
                with patch(
                    "agent_utilities.mcp.delegated_auth.get_user_identity",
                    return_value={"email": "test@example.com"},
                ):
                    with patch("servicenow_api.auth.Api") as mock_api_cls:
                        client = get_client(verify=True)
                        assert client is not None
                        mock_get_token.assert_called_with(
                            audience="https://dev12345.service-now.com",
                            scopes="api",
                            verify=True,
                        )
                        assert mock_api_cls.called
                        _, kwargs = mock_api_cls.call_args
                        assert kwargs["url"] == "https://dev12345.service-now.com"
                        assert kwargs["token"] == "mock-oidc-token"
                        assert kwargs["verify"] is True


def test_auth_oidc_delegation_failure():
    with patch.dict(
        os.environ, {"SERVICENOW_INSTANCE": "https://dev12345.service-now.com"}
    ):
        with patch(
            "agent_utilities.mcp.delegated_auth.is_delegation_enabled",
            return_value=True,
        ):
            with patch(
                "agent_utilities.mcp.delegated_auth.get_delegated_token",
                side_effect=Exception("Delegation server offline"),
            ):
                with pytest.raises(Exception, match="Delegation server offline"):
                    get_client()


def test_auth_basic_auth_success():
    with patch.dict(
        os.environ, {"SERVICENOW_INSTANCE": "https://dev12345.service-now.com"}
    ):
        with patch(
            "agent_utilities.mcp.delegated_auth.is_delegation_enabled",
            return_value=False,
        ):
            with patch("servicenow_api.auth.Api") as mock_api_cls:
                client = get_client(username="admin", password="password123")
                assert client is not None
                assert mock_api_cls.called
                _, kwargs = mock_api_cls.call_args
                assert kwargs["username"] == "admin"
                assert kwargs["password"] == "password123"
                assert kwargs["url"] == "https://dev12345.service-now.com"


def test_auth_basic_auth_failure_autherror():
    with patch.dict(
        os.environ, {"SERVICENOW_INSTANCE": "https://dev12345.service-now.com"}
    ):
        with patch(
            "agent_utilities.mcp.delegated_auth.is_delegation_enabled",
            return_value=False,
        ):
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
        with patch(
            "agent_utilities.mcp.delegated_auth.is_delegation_enabled",
            return_value=False,
        ):
            with patch(
                "servicenow_api.auth.Api",
                side_effect=UnauthorizedError("Blocked by OAuth policy"),
            ):
                with pytest.raises(RuntimeError, match="AUTHENTICATION ERROR"):
                    get_client(username="admin", password="wrongpassword")
