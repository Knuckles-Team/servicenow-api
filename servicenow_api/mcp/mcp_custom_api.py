"""MCP tools for custom api operations.

Auto-generated from mcp_server.py during ecosystem standardization.
"""

from agent_utilities.mcp_utilities import resolve_action
from fastmcp import Context, FastMCP
from fastmcp.dependencies import Depends
from pydantic import Field

from servicenow_api.auth import get_client


def register_custom_api_tools(mcp: FastMCP):
    @mcp.tool(tags={"custom_api"})
    async def servicenow_custom_api(
        action: str = Field(
            description="Action to perform. Must be one of: 'api_request'"
        ),
        params_json: str = Field(
            default="{}", description="JSON string of parameters to pass to the action."
        ),
        client=Depends(get_client),
        ctx: Context | None = Field(
            default=None, description="MCP context for progress reporting"
        ),
    ) -> dict:
        """Manage servicenow custom api operations."""
        if ctx:
            ctx.info("Executing tool...")
        import json

        try:
            kwargs = json.loads(params_json)
        except Exception as e:
            return {"error": f"Invalid params_json: {e}"}

        kwargs = {k: v for k, v in kwargs.items() if v is not None}

        resolved = resolve_action(action, ["api_request"], service="servicenow-api")
        if isinstance(resolved, dict):
            return resolved
        action = resolved

        if action == "api_request":
            return client.api_request(**kwargs)
        raise ValueError(f"Unknown action: {action}")
