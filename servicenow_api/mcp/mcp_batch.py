"""MCP tools for batch operations.

Auto-generated from mcp_server.py during ecosystem standardization.
"""

from agent_utilities.mcp_utilities import resolve_action, run_blocking
from fastmcp import Context, FastMCP
from fastmcp.dependencies import Depends
from pydantic import Field

from servicenow_api.auth import get_client


def register_batch_tools(mcp: FastMCP):
    @mcp.tool(tags={"batch"})
    async def servicenow_batch(
        action: str = Field(
            description="Action to perform. Must be one of: 'batch_request'"
        ),
        params_json: str = Field(
            default="{}", description="JSON string of parameters to pass to the action."
        ),
        client=Depends(get_client),
        ctx: Context | None = Field(
            default=None, description="MCP context for progress reporting"
        ),
    ) -> dict:
        """Manage servicenow batch operations."""
        if ctx:
            await ctx.info("Executing tool...")
        import json

        try:
            kwargs = json.loads(params_json)
        except Exception as e:
            return {"error": f"Invalid params_json: {e}"}

        kwargs = {k: v for k, v in kwargs.items() if v is not None}

        resolved = resolve_action(action, ["batch_request"], service="servicenow-api")
        if isinstance(resolved, dict):
            return resolved
        action = resolved

        if action == "batch_request":
            return await run_blocking(client.batch_request, **kwargs)
        raise ValueError(f"Unknown action: {action}")
