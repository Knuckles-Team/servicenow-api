"""MCP tools for devops operations.

Auto-generated from mcp_server.py during ecosystem standardization.
"""

from agent_utilities.mcp_utilities import resolve_action
from fastmcp import Context, FastMCP
from fastmcp.dependencies import Depends
from pydantic import Field

from servicenow_api.auth import get_client


def register_devops_tools(mcp: FastMCP):
    @mcp.tool(tags={"devops"})
    async def servicenow_devops(
        action: str = Field(
            description="Action to perform. Must be one of: 'check_devops_change_control', 'register_devops_artifact', 'check_devops_step_mapping', 'get_devops_change_info', 'get_devops_code_schema', 'get_devops_onboarding_status', 'get_devops_orchestration_schema', 'get_devops_plan_schema'"
        ),
        params_json: str = Field(
            default="{}", description="JSON string of parameters to pass to the action."
        ),
        client=Depends(get_client),
        ctx: Context | None = Field(
            default=None, description="MCP context for progress reporting"
        ),
    ) -> dict:
        """Manage servicenow devops operations."""
        if ctx:
            await ctx.info("Executing tool...")
        import json

        try:
            kwargs = json.loads(params_json)
        except Exception as e:
            return {"error": f"Invalid params_json: {e}"}

        kwargs = {k: v for k, v in kwargs.items() if v is not None}

        resolved = resolve_action(
            action,
            [
                "check_devops_change_control",
                "register_devops_artifact",
                "check_devops_step_mapping",
                "get_devops_change_info",
                "get_devops_code_schema",
                "get_devops_onboarding_status",
                "get_devops_orchestration_schema",
                "get_devops_plan_schema",
            ],
            service="servicenow-api",
        )
        if isinstance(resolved, dict):
            return resolved
        action = resolved

        if action == "check_devops_change_control":
            return client.check_devops_change_control(**kwargs)
        if action == "register_devops_artifact":
            return client.register_devops_artifact(**kwargs)
        if action == "check_devops_step_mapping":
            return client.check_devops_step_mapping(**kwargs)
        if action == "get_devops_change_info":
            return client.get_devops_change_info(**kwargs)
        if action == "get_devops_code_schema":
            return client.get_devops_code_schema(**kwargs)
        if action == "get_devops_onboarding_status":
            return client.get_devops_onboarding_status(**kwargs)
        if action == "get_devops_orchestration_schema":
            return client.get_devops_orchestration_schema(**kwargs)
        if action == "get_devops_plan_schema":
            return client.get_devops_plan_schema(**kwargs)
        raise ValueError(f"Unknown action: {action}")
