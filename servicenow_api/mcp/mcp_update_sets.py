"""MCP tools for update sets operations.

Auto-generated from mcp_server.py during ecosystem standardization.
"""

from agent_utilities.mcp_utilities import resolve_action, run_blocking
from fastmcp import Context, FastMCP
from fastmcp.dependencies import Depends
from pydantic import Field

from servicenow_api.auth import get_client


def register_update_sets_tools(mcp: FastMCP):
    @mcp.tool(tags={"update_sets"})
    async def servicenow_update_sets(
        action: str = Field(
            description="Action to perform. Must be one of: 'update_set_create', 'update_set_retrieve', 'update_set_preview', 'update_set_commit', 'update_set_commit_multiple', 'update_set_back_out'"
        ),
        params_json: str = Field(
            default="{}", description="JSON string of parameters to pass to the action."
        ),
        client=Depends(get_client),
        ctx: Context | None = Field(
            default=None, description="MCP context for progress reporting"
        ),
    ) -> dict:
        """Manage servicenow update sets operations."""
        if ctx:
            ctx.info("Executing tool...")
        import json

        try:
            kwargs = json.loads(params_json)
        except Exception as e:
            return {"error": f"Invalid params_json: {e}"}

        kwargs = {k: v for k, v in kwargs.items() if v is not None}

        resolved = resolve_action(
            action,
            [
                "update_set_create",
                "update_set_retrieve",
                "update_set_preview",
                "update_set_commit",
                "update_set_commit_multiple",
                "update_set_back_out",
            ],
            service="servicenow-api",
        )
        if isinstance(resolved, dict):
            return resolved
        action = resolved

        if action == "update_set_create":
            return await run_blocking(client.update_set_create, **kwargs)
        if action == "update_set_retrieve":
            return await run_blocking(client.update_set_retrieve, **kwargs)
        if action == "update_set_preview":
            return await run_blocking(client.update_set_preview, **kwargs)
        if action == "update_set_commit":
            return await run_blocking(client.update_set_commit, **kwargs)
        if action == "update_set_commit_multiple":
            return await run_blocking(client.update_set_commit_multiple, **kwargs)
        if action == "update_set_back_out":
            return await run_blocking(client.update_set_back_out, **kwargs)
        raise ValueError(f"Unknown action: {action}")
