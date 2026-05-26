"""MCP tools for ppm operations.

Auto-generated from mcp_server.py during ecosystem standardization.
"""

from fastmcp import Context, FastMCP
from fastmcp.dependencies import Depends
from pydantic import Field

from servicenow_api.auth import get_client


def register_ppm_tools(mcp: FastMCP):
    @mcp.tool(tags={"ppm"})
    async def servicenow_ppm(
        action: str = Field(
            description="Action to perform. Must be one of: 'insert_cost_plans', 'insert_project_tasks'"
        ),
        params_json: str = Field(
            default="{}", description="JSON string of parameters to pass to the action."
        ),
        client=Depends(get_client),
        ctx: Context | None = Field(
            default=None, description="MCP context for progress reporting"
        ),
    ) -> dict:
        """Manage servicenow ppm operations."""
        if ctx:
            ctx.info("Executing tool...")
        import json

        try:
            kwargs = json.loads(params_json)
        except Exception as e:
            return {"error": f"Invalid params_json: {e}"}

        kwargs = {k: v for k, v in kwargs.items() if v is not None}

        if action == "insert_cost_plans":
            return client.insert_cost_plans(**kwargs)
        if action == "insert_project_tasks":
            return client.insert_project_tasks(**kwargs)
        raise ValueError(f"Unknown action: {action}")
