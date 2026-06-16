"""Action-discovery standardization tests.

Verifies the shared agent-utilities resolve_action helper is wired into the
action-routed MCP tools so callers get list_actions discovery and a rich
did-you-mean error on unknown actions.
"""

import json
from unittest.mock import MagicMock

import pytest
from fastmcp import FastMCP

from servicenow_api.mcp_server import register_incidents_tools


async def _get_tool_fn(register):
    mcp = FastMCP(name="test")
    register(mcp)
    tools = await mcp._list_tools()
    # Exactly one action-routed tool per register_* function.
    (tool,) = tools
    return tool.fn


@pytest.mark.asyncio
async def test_list_actions_returns_names():
    fn = await _get_tool_fn(register_incidents_tools)
    result = await fn(
        action="list_actions", params_json="{}", client=MagicMock(), ctx=None
    )
    assert isinstance(result, dict)
    assert result["service"] == "servicenow-api"
    assert "get_incident" in result["actions"]
    assert "create_incident" in result["actions"]


@pytest.mark.asyncio
async def test_bogus_action_raises_with_list_actions_hint():
    fn = await _get_tool_fn(register_incidents_tools)
    with pytest.raises(ValueError) as exc:
        await fn(
            action="definitely_not_real",
            params_json="{}",
            client=MagicMock(),
            ctx=None,
        )
    assert "list_actions" in str(exc.value)


@pytest.mark.asyncio
async def test_valid_action_dispatches_to_client():
    fn = await _get_tool_fn(register_incidents_tools)
    client = MagicMock()
    client.get_incident.return_value = {"ok": True}
    result = await fn(
        action="get_incident",
        params_json=json.dumps({"incident_id": "INC1"}),
        client=client,
        ctx=None,
    )
    assert result == {"ok": True}
    client.get_incident.assert_called_once_with(incident_id="INC1")
