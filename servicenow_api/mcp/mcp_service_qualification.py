"""MCP tools for service qualification operations.

Auto-generated from mcp_server.py during ecosystem standardization.
"""

from fastmcp import Context, FastMCP
from fastmcp.dependencies import Depends
from pydantic import Field

from servicenow_api.auth import get_client


def register_service_qualification_tools(mcp: FastMCP):
    @mcp.tool(tags={"service_qualification"})
    async def servicenow_service_qualification(
        action: str = Field(
            description="Action to perform. Must be one of: 'check_service_qualification', 'get_service_qualification', 'process_service_qualification_result'"
        ),
        params_json: str = Field(
            default="{}", description="JSON string of parameters to pass to the action."
        ),
        client=Depends(get_client),
        ctx: Context | None = Field(
            default=None, description="MCP context for progress reporting"
        ),
    ) -> dict:
        """Manage servicenow service qualification operations."""
        if ctx:
            ctx.info("Executing tool...")
        import json

        try:
            kwargs = json.loads(params_json)
        except Exception as e:
            return {"error": f"Invalid params_json: {e}"}

        kwargs = {k: v for k, v in kwargs.items() if v is not None}

        if action == "check_service_qualification":
            return client.check_service_qualification(**kwargs)
        if action == "get_service_qualification":
            return client.get_service_qualification(**kwargs)
        if action == "process_service_qualification_result":
            return client.process_service_qualification_result(**kwargs)
        raise ValueError(f"Unknown action: {action}")
