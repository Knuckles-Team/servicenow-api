import json
import os
from unittest.mock import MagicMock, patch

import pytest

from servicenow_api.mcp_server import get_mcp_instance, mcp_server


@pytest.fixture
def mock_openapi_spec(tmp_path):
    spec = {
        "openapi": "3.0.0",
        "info": {"title": "Test API", "version": "1.0"},
        "paths": {
            "/api/now/table/incident": {
                "get": {
                    "operationId": "getIncidents",
                    "responses": {"200": {"description": "Success"}},
                }
            }
        },
    }
    file_path = tmp_path / "openapi.json"
    with open(file_path, "w") as f:
        json.dump(spec, f)
    return str(file_path)


def test_openapi_delegation_error(mock_openapi_spec):
    mock_args = MagicMock()
    mock_args.openapi_file = mock_openapi_spec
    mock_args.transport = "stdio"

    with patch(
        "servicenow_api.mcp_server.create_mcp_server",
        return_value=(mock_args, MagicMock(), []),
    ):
        with patch("servicenow_api.mcp_server.config", {"enable_delegation": True}):
            with pytest.raises(
                ValueError, match="OpenAPI import not supported with delegation enabled"
            ):
                get_mcp_instance()


def test_openapi_token_missing_error(mock_openapi_spec):
    mock_args = MagicMock()
    mock_args.openapi_file = mock_openapi_spec
    mock_args.openapi_use_token = True
    mock_args.transport = "stdio"

    with patch(
        "servicenow_api.mcp_server.create_mcp_server",
        return_value=(mock_args, MagicMock(), []),
    ):
        with patch("servicenow_api.mcp_server.config", {"enable_delegation": False}):
            with patch("servicenow_api.mcp_server.local", spec=[]):  # no user_token
                with pytest.raises(SystemExit):
                    get_mcp_instance()


def test_openapi_credentials_missing_error(mock_openapi_spec):
    mock_args = MagicMock()
    mock_args.openapi_file = mock_openapi_spec
    mock_args.openapi_use_token = False
    mock_args.openapi_username = None
    mock_args.openapi_password = None
    mock_args.openapi_client_id = None
    mock_args.openapi_client_secret = None
    mock_args.transport = "stdio"

    with patch(
        "servicenow_api.mcp_server.create_mcp_server",
        return_value=(mock_args, MagicMock(), []),
    ):
        with patch("servicenow_api.mcp_server.config", {"enable_delegation": False}):
            with patch.dict(os.environ, {}, clear=True):
                with pytest.raises(SystemExit):
                    get_mcp_instance()


def test_openapi_successful_import(mock_openapi_spec):
    mock_args = MagicMock()
    mock_args.openapi_file = mock_openapi_spec
    mock_args.openapi_use_token = False
    mock_args.openapi_username = "admin"
    mock_args.openapi_password = "password"
    mock_args.openapi_base_url = "https://mock.service-now.com"
    mock_args.transport = "stdio"

    mock_tool = MagicMock()
    mock_resource = MagicMock()

    mock_client = MagicMock()
    mock_client.url = "https://mock.service-now.com"
    mock_client.headers = {}
    mock_client.tls_profile.httpx_kwargs.return_value = {}

    with patch(
        "servicenow_api.mcp_server.create_mcp_server",
        return_value=(mock_args, MagicMock(), []),
    ):
        with patch("servicenow_api.mcp_server.config", {"enable_delegation": False}):
            with patch(
                "servicenow_api.mcp_server.get_client", return_value=mock_client
            ):
                with patch("asyncio.run", return_value=([mock_tool], [mock_resource])):
                    mcp, args, _, _, tools = get_mcp_instance()
                    assert len(tools) == 1
                    assert tools[0] == mock_tool


def test_openapi_import_uses_dedicated_credentials(mock_openapi_spec):
    """WD5-FIX-03 regression pin.

    The OpenAPI-import httpx client must authenticate with its OWN resolved
    ``--openapi-username``/``--openapi-password`` credentials, not the main
    ``get_client()``'s ``SERVICENOW_*`` ones. Before the fix, the resolved
    ``openapi_*`` credentials were validated for presence only and the
    outbound client was built solely from ``get_client()``'s unrelated
    ``SERVICENOW_*``-derived headers -- the token/username/password/
    client_id/client_secret branch gated a ``ValueError`` and had zero effect
    on the request. This test drives the real ``_load_openapi_tools()``
    coroutine body (``asyncio.run`` is NOT mocked, unlike
    ``test_openapi_successful_import`` above) and pins the Basic-auth header
    actually sent.
    """
    mock_args = MagicMock()
    mock_args.openapi_file = mock_openapi_spec
    mock_args.openapi_use_token = False
    mock_args.openapi_username = "openapi_user"
    mock_args.openapi_password = "openapi_pass"
    mock_args.openapi_client_id = None
    mock_args.openapi_client_secret = None
    mock_args.openapi_base_url = None
    mock_args.transport = "stdio"

    captured = {}

    class _FakeAsyncClient:
        def __init__(self, *args, **kwargs):
            captured["base_url"] = kwargs.get("base_url")
            captured["headers"] = kwargs.get("headers")

        async def __aenter__(self):
            return MagicMock()

        async def __aexit__(self, *exc_info):
            return False

    mock_openapi_mcp = MagicMock()

    async def _fake_get_tools():
        return []

    async def _fake_get_resources():
        return []

    mock_openapi_mcp.get_tools = _fake_get_tools
    mock_openapi_mcp.get_resources = _fake_get_resources

    with patch(
        "servicenow_api.mcp_server.create_mcp_server",
        return_value=(mock_args, MagicMock(), []),
    ):
        with patch("servicenow_api.mcp_server.config", {"enable_delegation": False}):
            with patch("servicenow_api.mcp_server.httpx.AsyncClient", _FakeAsyncClient):
                with patch(
                    "servicenow_api.mcp_server.FastMCP.from_openapi",
                    return_value=mock_openapi_mcp,
                ):
                    with patch.dict(
                        os.environ,
                        {
                            "SERVICENOW_INSTANCE": "https://main.service-now.com",
                            "SERVICENOW_USERNAME": "main_user",
                            "SERVICENOW_PASSWORD": "main_pass",
                        },
                        clear=True,
                    ):
                        get_mcp_instance()

    import base64

    openapi_auth = base64.b64encode(b"openapi_user:openapi_pass").decode()
    main_auth = base64.b64encode(b"main_user:main_pass").decode()
    assert captured["headers"]["Authorization"] == f"Basic {openapi_auth}"
    assert captured["headers"]["Authorization"] != f"Basic {main_auth}"


def test_mcp_server_run_stdio():
    mock_mcp = MagicMock()
    mock_args = MagicMock()
    mock_args.transport = "stdio"
    mock_args.auth_type = "basic"
    mock_args.eunomia_type = "none"

    with patch(
        "servicenow_api.mcp_server.get_mcp_instance",
        return_value=(mock_mcp, mock_args, [], [], []),
    ):
        with patch("servicenow_api.mcp_server.config", {"enable_delegation": False}):
            mcp_server()
            mock_mcp.run.assert_called_once_with(transport="stdio")


def test_mcp_server_run_streamable_http():
    mock_mcp = MagicMock()
    mock_args = MagicMock()
    mock_args.transport = "streamable-http"
    mock_args.host = "127.0.0.1"
    mock_args.port = 8000
    mock_args.auth_type = "basic"
    mock_args.eunomia_type = "none"

    with patch(
        "servicenow_api.mcp_server.get_mcp_instance",
        return_value=(mock_mcp, mock_args, [], [], []),
    ):
        with patch("servicenow_api.mcp_server.config", {"enable_delegation": False}):
            mcp_server()
            mock_mcp.run.assert_called_once_with(
                transport="streamable-http", host="127.0.0.1", port=8000
            )


def test_mcp_server_run_sse():
    mock_mcp = MagicMock()
    mock_args = MagicMock()
    mock_args.transport = "sse"
    mock_args.host = "127.0.0.1"
    mock_args.port = 8000
    mock_args.auth_type = "basic"
    mock_args.eunomia_type = "none"

    with patch(
        "servicenow_api.mcp_server.get_mcp_instance",
        return_value=(mock_mcp, mock_args, [], [], []),
    ):
        with patch("servicenow_api.mcp_server.config", {"enable_delegation": False}):
            mcp_server()
            mock_mcp.run.assert_called_once_with(
                transport="sse", host="127.0.0.1", port=8000
            )


def test_mcp_server_invalid_transport():
    mock_mcp = MagicMock()
    mock_args = MagicMock()
    mock_args.transport = "invalid"
    mock_args.auth_type = "basic"
    mock_args.eunomia_type = "none"

    with patch(
        "servicenow_api.mcp_server.get_mcp_instance",
        return_value=(mock_mcp, mock_args, [], [], []),
    ):
        with patch("servicenow_api.mcp_server.config", {"enable_delegation": False}):
            with pytest.raises(SystemExit):
                mcp_server()
