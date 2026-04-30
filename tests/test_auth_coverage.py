import pytest
import os
from unittest.mock import MagicMock, patch
from servicenow_api.auth import get_client
import requests


def test_get_client_no_instance():
    with patch.dict(os.environ, {}, clear=True):
        with pytest.raises(RuntimeError, match="SERVICENOW_INSTANCE not set"):
            get_client()


def test_get_client_basic_auth():
    with patch.dict(os.environ, {"SERVICENOW_INSTANCE": "test.com"}, clear=True):
        with patch("servicenow_api.auth.Api") as mock_api:
            client = get_client(username="user", password="pass")
            mock_api.assert_called_with(
                url="test.com",
                username="user",
                password="pass",
                client_id=None,
                client_secret=None,
                verify=True,
            )


def test_get_client_delegation_failure():
    with patch.dict(
        os.environ,
        {
            "SERVICENOW_INSTANCE": "test.com",
            "ENABLE_DELEGATION": "True",
            "SERVICENOW_AUDIENCE": "aud",
        },
        clear=True,
    ):
        from servicenow_api.auth import local

        local.user_token = "mcp_token"

        with patch("requests.post") as mock_post:
            mock_post.side_effect = Exception("failed")
            with pytest.raises(Exception):
                get_client()


def test_get_client_no_auth_method():
    with patch.dict(os.environ, {"SERVICENOW_INSTANCE": "test.com"}, clear=True):
        with pytest.raises(ValueError, match="No auth method"):
            get_client(username=None, password=None)


if __name__ == "__main__":
    import pytest

    pytest.main([__file__])
