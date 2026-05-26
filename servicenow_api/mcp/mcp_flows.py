"""MCP tools for flows operations.

Auto-generated from mcp_server.py during ecosystem standardization.
"""

from fastmcp import Context, FastMCP
from fastmcp.dependencies import Depends
from pydantic import Field

from servicenow_api.auth import get_client


def register_flows_tools(mcp: FastMCP):
    @mcp.tool(tags={"flows"})
    async def servicenow_flows(
        action: str = Field(
            description="Action to perform. Must be one of: 'workflow_to_mermaid', 'collect_graph_for_roots', 'get_flow_metadata'"
        ),
        params_json: str = Field(
            default="{}", description="JSON string of parameters to pass to the action."
        ),
        client=Depends(get_client),
        ctx: Context | None = Field(
            default=None, description="MCP context for progress reporting"
        ),
    ) -> dict:
        """Manage servicenow flows operations."""
        if ctx:
            ctx.info("Executing tool...")
        import json

        try:
            kwargs = json.loads(params_json)
        except Exception as e:
            return {"error": f"Invalid params_json: {e}"}

        kwargs = {k: v for k, v in kwargs.items() if v is not None}

        if action == "workflow_to_mermaid":
            return client.workflow_to_mermaid(**kwargs)
        if action == "collect_graph_for_roots":
            return client.collect_graph_for_roots(**kwargs)
        if action == "get_flow_metadata":
            return client.get_flow_metadata(**kwargs)
        raise ValueError(f"Unknown action: {action}")
