"""MCP tools for incidents operations.

Auto-generated from mcp_server.py during ecosystem standardization.
"""

from agent_utilities.mcp.action_dispatch import resolve_action
from agent_utilities.mcp.concurrency import run_blocking
from fastmcp import Context, FastMCP
from fastmcp.dependencies import Depends
from pydantic import Field

from servicenow_api.auth import get_client


def register_incidents_tools(mcp: FastMCP):
    @mcp.tool(tags={"incidents"})
    async def servicenow_incidents(
        action: str = Field(
            description="Action to perform. Must be one of: 'get_incidents', 'create_incident', 'get_incident'"
        ),
        params_json: str = Field(
            default="{}", description="JSON string of parameters to pass to the action."
        ),
        client=Depends(get_client),
        ctx: Context | None = Field(
            default=None, description="MCP context for progress reporting"
        ),
    ) -> dict:
        """Manage servicenow incidents operations."""
        if ctx:
            await ctx.info("Executing tool...")
        import json

        try:
            kwargs = json.loads(params_json)
        except Exception:
            return {"error": "Operation failed"}

        kwargs = {k: v for k, v in kwargs.items() if v is not None}

        resolved = resolve_action(
            action,
            ["get_incidents", "create_incident", "get_incident"],
            service="servicenow-api",
        )
        if isinstance(resolved, dict):
            return resolved
        action = resolved

        if action == "get_incidents":
            return await run_blocking(client.get_incidents, **kwargs)
        if action == "create_incident":
            return await run_blocking(client.create_incident, **kwargs)
        if action == "get_incident":
            return await run_blocking(client.get_incident, **kwargs)
        raise ValueError(f"Unknown action: {action}")
