"""MCP tools for service qualification operations.

Auto-generated from mcp_server.py during ecosystem standardization.
"""

from agent_utilities.mcp_utilities import resolve_action, run_blocking
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

        resolved = resolve_action(
            action,
            [
                "check_service_qualification",
                "get_service_qualification",
                "process_service_qualification_result",
            ],
            service="servicenow-api",
        )
        if isinstance(resolved, dict):
            return resolved
        action = resolved

        if action == "check_service_qualification":
            return await run_blocking(client.check_service_qualification, **kwargs)
        if action == "get_service_qualification":
            return await run_blocking(client.get_service_qualification, **kwargs)
        if action == "process_service_qualification_result":
            return await run_blocking(
                client.process_service_qualification_result, **kwargs
            )
        raise ValueError(f"Unknown action: {action}")
