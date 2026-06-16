"""MCP tools for plugins operations.

Auto-generated from mcp_server.py during ecosystem standardization.
"""

from agent_utilities.mcp_utilities import resolve_action
from fastmcp import Context, FastMCP
from fastmcp.dependencies import Depends
from pydantic import Field

from servicenow_api.auth import get_client


def register_plugins_tools(mcp: FastMCP):
    @mcp.tool(tags={"plugins"})
    async def servicenow_plugins(
        action: str = Field(
            description="Action to perform. Must be one of: 'activate_plugin', 'rollback_plugin'"
        ),
        params_json: str = Field(
            default="{}", description="JSON string of parameters to pass to the action."
        ),
        client=Depends(get_client),
        ctx: Context | None = Field(
            default=None, description="MCP context for progress reporting"
        ),
    ) -> dict:
        """Manage servicenow plugins operations."""
        if ctx:
            ctx.info("Executing tool...")
        import json

        try:
            kwargs = json.loads(params_json)
        except Exception as e:
            return {"error": f"Invalid params_json: {e}"}

        kwargs = {k: v for k, v in kwargs.items() if v is not None}

        resolved = resolve_action(
            action, ["activate_plugin", "rollback_plugin"], service="servicenow-api"
        )
        if isinstance(resolved, dict):
            return resolved
        action = resolved

        if action == "activate_plugin":
            return client.activate_plugin(**kwargs)
        if action == "rollback_plugin":
            return client.rollback_plugin(**kwargs)
        raise ValueError(f"Unknown action: {action}")
