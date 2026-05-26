"""MCP tools for source control operations.

Auto-generated from mcp_server.py during ecosystem standardization.
"""

from fastmcp import Context, FastMCP
from fastmcp.dependencies import Depends
from pydantic import Field

from servicenow_api.auth import get_client


def register_source_control_tools(mcp: FastMCP):
    @mcp.tool(tags={"source_control"})
    async def servicenow_source_control(
        action: str = Field(
            description="Action to perform. Must be one of: 'apply_remote_source_control_changes', 'import_repository'"
        ),
        params_json: str = Field(
            default="{}", description="JSON string of parameters to pass to the action."
        ),
        client=Depends(get_client),
        ctx: Context | None = Field(
            default=None, description="MCP context for progress reporting"
        ),
    ) -> dict:
        """Manage servicenow source control operations."""
        if ctx:
            ctx.info("Executing tool...")
        import json

        try:
            kwargs = json.loads(params_json)
        except Exception as e:
            return {"error": f"Invalid params_json: {e}"}

        kwargs = {k: v for k, v in kwargs.items() if v is not None}

        if action == "apply_remote_source_control_changes":
            return client.apply_remote_source_control_changes(**kwargs)
        if action == "import_repository":
            return client.import_repository(**kwargs)
        raise ValueError(f"Unknown action: {action}")
