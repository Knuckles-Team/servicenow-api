"""MCP tools for table api operations.

Auto-generated from mcp_server.py during ecosystem standardization.
"""

from agent_utilities.mcp_utilities import resolve_action
from fastmcp import Context, FastMCP
from fastmcp.dependencies import Depends
from pydantic import Field

from servicenow_api.auth import get_client


def register_table_api_tools(mcp: FastMCP):
    @mcp.tool(tags={"table_api"})
    async def servicenow_table_api(
        action: str = Field(
            description="Action to perform. Must be one of: 'delete_table_record', 'get_table', 'get_table_record', 'patch_table_record', 'update_table_record', 'add_table_record'"
        ),
        params_json: str = Field(
            default="{}", description="JSON string of parameters to pass to the action."
        ),
        client=Depends(get_client),
        ctx: Context | None = Field(
            default=None, description="MCP context for progress reporting"
        ),
    ) -> dict:
        """Manage servicenow table api operations."""
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
                "delete_table_record",
                "get_table",
                "get_table_record",
                "patch_table_record",
                "update_table_record",
                "add_table_record",
            ],
            service="servicenow-api",
        )
        if isinstance(resolved, dict):
            return resolved
        action = resolved

        if action == "delete_table_record":
            return client.delete_table_record(**kwargs)
        if action == "get_table":
            return client.get_table(**kwargs)
        if action == "get_table_record":
            return client.get_table_record(**kwargs)
        if action == "patch_table_record":
            return client.patch_table_record(**kwargs)
        if action == "update_table_record":
            return client.update_table_record(**kwargs)
        if action == "add_table_record":
            return client.add_table_record(**kwargs)
        raise ValueError(f"Unknown action: {action}")
