"""MCP tools for cmdb operations.

Auto-generated from mcp_server.py during ecosystem standardization.
"""

from fastmcp import Context, FastMCP
from fastmcp.dependencies import Depends
from pydantic import Field

from servicenow_api.auth import get_client


def register_cmdb_tools(mcp: FastMCP):
    @mcp.tool(tags={"cmdb"})
    async def servicenow_cmdb(
        action: str = Field(
            description="Action to perform. Must be one of: 'get_cmdb', 'delete_cmdb_relation', 'get_cmdb_instances', 'get_cmdb_instance', 'create_cmdb_instance', 'update_cmdb_instance', 'patch_cmdb_instance', 'create_cmdb_relation', 'ingest_cmdb_data'"
        ),
        params_json: str = Field(
            default="{}", description="JSON string of parameters to pass to the action."
        ),
        client=Depends(get_client),
        ctx: Context | None = Field(
            default=None, description="MCP context for progress reporting"
        ),
    ) -> dict:
        """Manage servicenow cmdb operations."""
        if ctx:
            ctx.info("Executing tool...")
        import json

        try:
            kwargs = json.loads(params_json)
        except Exception as e:
            return {"error": f"Invalid params_json: {e}"}

        kwargs = {k: v for k, v in kwargs.items() if v is not None}

        if action == "get_cmdb":
            return client.get_cmdb(**kwargs)
        if action == "delete_cmdb_relation":
            return client.delete_cmdb_relation(**kwargs)
        if action == "get_cmdb_instances":
            return client.get_cmdb_instances(**kwargs)
        if action == "get_cmdb_instance":
            return client.get_cmdb_instance(**kwargs)
        if action == "create_cmdb_instance":
            return client.create_cmdb_instance(**kwargs)
        if action == "update_cmdb_instance":
            return client.update_cmdb_instance(**kwargs)
        if action == "patch_cmdb_instance":
            return client.patch_cmdb_instance(**kwargs)
        if action == "create_cmdb_relation":
            return client.create_cmdb_relation(**kwargs)
        if action == "ingest_cmdb_data":
            return client.ingest_cmdb_data(**kwargs)
        raise ValueError(f"Unknown action: {action}")
