"""MCP tools for data classification operations.

Auto-generated from mcp_server.py during ecosystem standardization.
"""

from fastmcp import Context, FastMCP
from fastmcp.dependencies import Depends
from pydantic import Field

from servicenow_api.auth import get_client


def register_data_classification_tools(mcp: FastMCP):
    @mcp.tool(tags={"data_classification"})
    async def servicenow_data_classification(
        action: str = Field(
            description="Action to perform. Must be one of: 'get_data_classification'"
        ),
        params_json: str = Field(
            default="{}", description="JSON string of parameters to pass to the action."
        ),
        client=Depends(get_client),
        ctx: Context | None = Field(
            default=None, description="MCP context for progress reporting"
        ),
    ) -> dict:
        """Manage servicenow data classification operations."""
        if ctx:
            ctx.info("Executing tool...")
        import json

        try:
            kwargs = json.loads(params_json)
        except Exception as e:
            return {"error": f"Invalid params_json: {e}"}

        kwargs = {k: v for k, v in kwargs.items() if v is not None}

        if action == "get_data_classification":
            return client.get_data_classification(**kwargs)
        raise ValueError(f"Unknown action: {action}")
