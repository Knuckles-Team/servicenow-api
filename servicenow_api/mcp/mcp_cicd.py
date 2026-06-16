"""MCP tools for cicd operations.

Auto-generated from mcp_server.py during ecosystem standardization.
"""

from agent_utilities.mcp_utilities import resolve_action
from fastmcp import Context, FastMCP
from fastmcp.dependencies import Depends
from pydantic import Field

from servicenow_api.auth import get_client


def register_cicd_tools(mcp: FastMCP):
    @mcp.tool(tags={"cicd"})
    async def servicenow_cicd(
        action: str = Field(
            description="Action to perform. Must be one of: 'batch_install_result', 'instance_scan_progress', 'progress', 'batch_install', 'batch_rollback', 'app_repo_install', 'app_repo_publish', 'app_repo_rollback', 'full_scan', 'point_scan', 'combo_suite_scan', 'suite_scan'"
        ),
        params_json: str = Field(
            default="{}", description="JSON string of parameters to pass to the action."
        ),
        client=Depends(get_client),
        ctx: Context | None = Field(
            default=None, description="MCP context for progress reporting"
        ),
    ) -> dict:
        """Manage servicenow cicd operations."""
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
                "batch_install_result",
                "instance_scan_progress",
                "progress",
                "batch_install",
                "batch_rollback",
                "app_repo_install",
                "app_repo_publish",
                "app_repo_rollback",
                "full_scan",
                "point_scan",
                "combo_suite_scan",
                "suite_scan",
            ],
            service="servicenow-api",
        )
        if isinstance(resolved, dict):
            return resolved
        action = resolved

        if action == "batch_install_result":
            return client.batch_install_result(**kwargs)
        if action == "instance_scan_progress":
            return client.instance_scan_progress(**kwargs)
        if action == "progress":
            return client.progress(**kwargs)
        if action == "batch_install":
            return client.batch_install(**kwargs)
        if action == "batch_rollback":
            return client.batch_rollback(**kwargs)
        if action == "app_repo_install":
            return client.app_repo_install(**kwargs)
        if action == "app_repo_publish":
            return client.app_repo_publish(**kwargs)
        if action == "app_repo_rollback":
            return client.app_repo_rollback(**kwargs)
        if action == "full_scan":
            return client.full_scan(**kwargs)
        if action == "point_scan":
            return client.point_scan(**kwargs)
        if action == "combo_suite_scan":
            return client.combo_suite_scan(**kwargs)
        if action == "suite_scan":
            return client.suite_scan(**kwargs)
        raise ValueError(f"Unknown action: {action}")
