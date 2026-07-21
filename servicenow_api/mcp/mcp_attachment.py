"""MCP tools for attachment operations.

Auto-generated from mcp_server.py during ecosystem standardization.
"""

from agent_utilities.mcp.action_dispatch import resolve_action
from agent_utilities.mcp.concurrency import run_blocking
from fastmcp import Context, FastMCP
from fastmcp.dependencies import Depends
from pydantic import Field

from servicenow_api.auth import get_client


def register_attachment_tools(mcp: FastMCP):
    @mcp.tool(tags={"attachment"})
    async def servicenow_attachment(
        action: str = Field(
            description="Action to perform. Must be one of: 'get_attachment', 'upload_attachment', 'delete_attachment'"
        ),
        params_json: str = Field(
            default="{}", description="JSON string of parameters to pass to the action."
        ),
        client=Depends(get_client),
        ctx: Context | None = Field(
            default=None, description="MCP context for progress reporting"
        ),
    ) -> dict:
        """Manage servicenow attachment operations."""
        if ctx:
            ctx.info("Executing tool...")
        import json

        try:
            kwargs = json.loads(params_json)
        except Exception:
            return {"error": "Operation failed"}

        kwargs = {k: v for k, v in kwargs.items() if v is not None}

        resolved = resolve_action(
            action,
            ["get_attachment", "upload_attachment", "delete_attachment"],
            service="servicenow-api",
        )
        if isinstance(resolved, dict):
            return resolved
        action = resolved

        if action == "get_attachment":
            return await run_blocking(client.get_attachment, **kwargs)
        if action == "upload_attachment":
            return await run_blocking(client.upload_attachment, **kwargs)
        if action == "delete_attachment":
            return await run_blocking(client.delete_attachment, **kwargs)
        raise ValueError(f"Unknown action: {action}")
