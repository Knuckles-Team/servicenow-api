"""MCP tools for metricbase operations.

Auto-generated from mcp_server.py during ecosystem standardization.
"""

from agent_utilities.mcp_utilities import resolve_action, run_blocking
from fastmcp import Context, FastMCP
from fastmcp.dependencies import Depends
from pydantic import Field

from servicenow_api.auth import get_client


def register_metricbase_tools(mcp: FastMCP):
    @mcp.tool(tags={"metricbase"})
    async def servicenow_metricbase(
        action: str = Field(
            description="Action to perform. Must be one of: 'metricbase_insert'"
        ),
        params_json: str = Field(
            default="{}", description="JSON string of parameters to pass to the action."
        ),
        client=Depends(get_client),
        ctx: Context | None = Field(
            default=None, description="MCP context for progress reporting"
        ),
    ) -> dict:
        """Manage servicenow metricbase operations."""
        if ctx:
            ctx.info("Executing tool...")
        import json

        try:
            kwargs = json.loads(params_json)
        except Exception as e:
            return {"error": f"Invalid params_json: {e}"}

        kwargs = {k: v for k, v in kwargs.items() if v is not None}

        resolved = resolve_action(
            action, ["metricbase_insert"], service="servicenow-api"
        )
        if isinstance(resolved, dict):
            return resolved
        action = resolved

        if action == "metricbase_insert":
            return await run_blocking(client.metricbase_insert, **kwargs)
        raise ValueError(f"Unknown action: {action}")
