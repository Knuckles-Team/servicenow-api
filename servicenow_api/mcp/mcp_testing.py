"""MCP tools for testing operations.

Auto-generated from mcp_server.py during ecosystem standardization.
"""

from agent_utilities.mcp_utilities import resolve_action, run_blocking
from fastmcp import Context, FastMCP
from fastmcp.dependencies import Depends
from pydantic import Field

from servicenow_api.auth import get_client


def register_testing_tools(mcp: FastMCP):
    @mcp.tool(tags={"testing"})
    async def servicenow_testing(
        action: str = Field(
            description="Action to perform. Must be one of: 'run_test_suite'"
        ),
        params_json: str = Field(
            default="{}", description="JSON string of parameters to pass to the action."
        ),
        client=Depends(get_client),
        ctx: Context | None = Field(
            default=None, description="MCP context for progress reporting"
        ),
    ) -> dict:
        """Manage servicenow testing operations."""
        if ctx:
            await ctx.info("Executing tool...")
        import json

        try:
            kwargs = json.loads(params_json)
        except Exception as e:
            return {"error": f"Invalid params_json: {e}"}

        kwargs = {k: v for k, v in kwargs.items() if v is not None}

        resolved = resolve_action(action, ["run_test_suite"], service="servicenow-api")
        if isinstance(resolved, dict):
            return resolved
        action = resolved

        if action == "run_test_suite":
            return await run_blocking(client.run_test_suite, **kwargs)
        raise ValueError(f"Unknown action: {action}")
