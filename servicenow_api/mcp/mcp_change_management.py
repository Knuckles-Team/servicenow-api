"""MCP tools for change management operations.

Auto-generated from mcp_server.py during ecosystem standardization.
"""

from agent_utilities.mcp_utilities import resolve_action
from fastmcp import Context, FastMCP
from fastmcp.dependencies import Depends
from pydantic import Field

from servicenow_api.auth import get_client


def register_change_management_tools(mcp: FastMCP):
    @mcp.tool(tags={"change_management"})
    async def servicenow_change_management(
        action: str = Field(
            description="Action to perform. Must be one of: 'get_change_requests', 'get_change_request_nextstate', 'get_change_request_schedule', 'get_change_request_tasks', 'get_change_request', 'get_change_request_ci', 'get_change_request_conflict', 'get_standard_change_request_templates', 'get_change_request_models', 'get_standard_change_request_model', 'get_standard_change_request_template', 'get_change_request_worker', 'create_change_request', 'create_change_request_task', 'create_change_request_ci_association', 'calculate_standard_change_request_risk', 'check_change_request_conflict', 'refresh_change_request_impacted_services', 'approve_change_request', 'update_change_request', 'update_change_request_first_available', 'update_change_request_task', 'delete_change_request', 'delete_change_request_task', 'delete_change_request_conflict_scan'"
        ),
        params_json: str = Field(
            default="{}", description="JSON string of parameters to pass to the action."
        ),
        client=Depends(get_client),
        ctx: Context | None = Field(
            default=None, description="MCP context for progress reporting"
        ),
    ) -> dict:
        """Manage servicenow change management operations."""
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
                "get_change_requests",
                "get_change_request_nextstate",
                "get_change_request_schedule",
                "get_change_request_tasks",
                "get_change_request",
                "get_change_request_ci",
                "get_change_request_conflict",
                "get_standard_change_request_templates",
                "get_change_request_models",
                "get_standard_change_request_model",
                "get_standard_change_request_template",
                "get_change_request_worker",
                "create_change_request",
                "create_change_request_task",
                "create_change_request_ci_association",
                "calculate_standard_change_request_risk",
                "check_change_request_conflict",
                "refresh_change_request_impacted_services",
                "approve_change_request",
                "update_change_request",
                "update_change_request_first_available",
                "update_change_request_task",
                "delete_change_request",
                "delete_change_request_task",
                "delete_change_request_conflict_scan",
            ],
            service="servicenow-api",
        )
        if isinstance(resolved, dict):
            return resolved
        action = resolved

        if action == "get_change_requests":
            return client.get_change_requests(**kwargs)
        if action == "get_change_request_nextstate":
            return client.get_change_request_nextstate(**kwargs)
        if action == "get_change_request_schedule":
            return client.get_change_request_schedule(**kwargs)
        if action == "get_change_request_tasks":
            return client.get_change_request_tasks(**kwargs)
        if action == "get_change_request":
            return client.get_change_request(**kwargs)
        if action == "get_change_request_ci":
            return client.get_change_request_ci(**kwargs)
        if action == "get_change_request_conflict":
            return client.get_change_request_conflict(**kwargs)
        if action == "get_standard_change_request_templates":
            return client.get_standard_change_request_templates(**kwargs)
        if action == "get_change_request_models":
            return client.get_change_request_models(**kwargs)
        if action == "get_standard_change_request_model":
            return client.get_standard_change_request_model(**kwargs)
        if action == "get_standard_change_request_template":
            return client.get_standard_change_request_template(**kwargs)
        if action == "get_change_request_worker":
            return client.get_change_request_worker(**kwargs)
        if action == "create_change_request":
            return client.create_change_request(**kwargs)
        if action == "create_change_request_task":
            return client.create_change_request_task(**kwargs)
        if action == "create_change_request_ci_association":
            return client.create_change_request_ci_association(**kwargs)
        if action == "calculate_standard_change_request_risk":
            return client.calculate_standard_change_request_risk(**kwargs)
        if action == "check_change_request_conflict":
            return client.check_change_request_conflict(**kwargs)
        if action == "refresh_change_request_impacted_services":
            return client.refresh_change_request_impacted_services(**kwargs)
        if action == "approve_change_request":
            return client.approve_change_request(**kwargs)
        if action == "update_change_request":
            return client.update_change_request(**kwargs)
        if action == "update_change_request_first_available":
            return client.update_change_request_first_available(**kwargs)
        if action == "update_change_request_task":
            return client.update_change_request_task(**kwargs)
        if action == "delete_change_request":
            return client.delete_change_request(**kwargs)
        if action == "delete_change_request_task":
            return client.delete_change_request_task(**kwargs)
        if action == "delete_change_request_conflict_scan":
            return client.delete_change_request_conflict_scan(**kwargs)
        raise ValueError(f"Unknown action: {action}")
