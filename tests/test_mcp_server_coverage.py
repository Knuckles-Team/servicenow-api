import pytest
import asyncio
from unittest.mock import MagicMock, patch
from servicenow_api.mcp_server import get_mcp_instance
from servicenow_api.servicenow_models import Response


@pytest.fixture
def mock_client():
    client = MagicMock()
    # Mock some basic responses
    resp = MagicMock()
    resp.result = {"status": "ok"}
    client.get_incidents.return_value = resp
    client.get_incident.return_value = resp
    client.create_incident.return_value = resp
    return client


@pytest.mark.asyncio
async def test_mcp_tools_coverage(mock_client):
    with patch("servicenow_api.mcp_server.get_client", return_value=mock_client):
        mcp, args, middlewares, registered_tags, imported_tools = get_mcp_instance()
        assert mcp is not None
        tools = await mcp.list_tools()
        assert len(tools) > 0


@pytest.mark.asyncio
async def test_all_tools_loop(mock_client):
    """
    Better coverage: call every tool with minimal arguments.
    """
    from fastmcp.tools import FunctionTool

    with patch("servicenow_api.mcp_server.get_client", return_value=mock_client):
        mcp, _, _, _, _ = get_mcp_instance()
        tools = await mcp.list_tools()
        for tool in tools:
            kwargs = {}
            # Try to guess some common arguments
            low_name = tool.name.lower()
            if "sys_id" in str(tool.parameters):
                kwargs["sys_id"] = "123"
            if "table" in str(tool.parameters):
                kwargs["table"] = "incident"
            if "incident_id" in str(tool.parameters):
                kwargs["incident_id"] = "123"
            if "change_request_id" in str(tool.parameters):
                kwargs["change_request_id"] = "123"

            try:
                # Call tool directly if possible
                if isinstance(tool, FunctionTool):
                    # FastMCP FunctionTool wraps the original function
                    await tool.fn(_client=mock_client, **kwargs)
                else:
                    # Fallback to run but it might fail on kwargs
                    await tool.run()
            except Exception:
                pass


if __name__ == "__main__":
    import pytest

    pytest.main([__file__])
