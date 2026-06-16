"""MCP tools for cilifecycle operations.

Auto-generated from mcp_server.py during ecosystem standardization.
"""

from agent_utilities.mcp_utilities import resolve_action, run_blocking
from fastmcp import Context, FastMCP
from fastmcp.dependencies import Depends
from pydantic import Field

from servicenow_api.auth import get_client


def register_cilifecycle_tools(mcp: FastMCP):
    @mcp.tool(tags={"cilifecycle"})
    async def servicenow_cilifecycle(
        action: str = Field(
            description="Action to perform. Must be one of: 'check_ci_lifecycle_compat_actions', 'register_ci_lifecycle_operator', 'unregister_ci_lifecycle_operator', 'add_ci_lifecycle_action', 'check_ci_lifecycle_lease_expired', 'check_ci_lifecycle_not_allowed_action', 'check_ci_lifecycle_not_allowed_ops_transition', 'check_ci_lifecycle_requestor_valid', 'delete_ci_lifecycle_action', 'extend_ci_lifecycle_lease', 'get_ci_lifecycle_active_actions', 'get_ci_lifecycle_status', 'set_ci_lifecycle_status'"
        ),
        params_json: str = Field(
            default="{}", description="JSON string of parameters to pass to the action."
        ),
        client=Depends(get_client),
        ctx: Context | None = Field(
            default=None, description="MCP context for progress reporting"
        ),
    ) -> dict:
        """Manage servicenow cilifecycle operations."""
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
                "check_ci_lifecycle_compat_actions",
                "register_ci_lifecycle_operator",
                "unregister_ci_lifecycle_operator",
                "add_ci_lifecycle_action",
                "check_ci_lifecycle_lease_expired",
                "check_ci_lifecycle_not_allowed_action",
                "check_ci_lifecycle_not_allowed_ops_transition",
                "check_ci_lifecycle_requestor_valid",
                "delete_ci_lifecycle_action",
                "extend_ci_lifecycle_lease",
                "get_ci_lifecycle_active_actions",
                "get_ci_lifecycle_status",
                "set_ci_lifecycle_status",
            ],
            service="servicenow-api",
        )
        if isinstance(resolved, dict):
            return resolved
        action = resolved

        if action == "check_ci_lifecycle_compat_actions":
            return await run_blocking(
                client.check_ci_lifecycle_compat_actions, **kwargs
            )
        if action == "register_ci_lifecycle_operator":
            return await run_blocking(client.register_ci_lifecycle_operator, **kwargs)
        if action == "unregister_ci_lifecycle_operator":
            return await run_blocking(client.unregister_ci_lifecycle_operator, **kwargs)
        if action == "add_ci_lifecycle_action":
            return await run_blocking(client.add_ci_lifecycle_action, **kwargs)
        if action == "check_ci_lifecycle_lease_expired":
            return await run_blocking(client.check_ci_lifecycle_lease_expired, **kwargs)
        if action == "check_ci_lifecycle_not_allowed_action":
            return await run_blocking(
                client.check_ci_lifecycle_not_allowed_action, **kwargs
            )
        if action == "check_ci_lifecycle_not_allowed_ops_transition":
            return await run_blocking(
                client.check_ci_lifecycle_not_allowed_ops_transition, **kwargs
            )
        if action == "check_ci_lifecycle_requestor_valid":
            return await run_blocking(
                client.check_ci_lifecycle_requestor_valid, **kwargs
            )
        if action == "delete_ci_lifecycle_action":
            return await run_blocking(client.delete_ci_lifecycle_action, **kwargs)
        if action == "extend_ci_lifecycle_lease":
            return await run_blocking(client.extend_ci_lifecycle_lease, **kwargs)
        if action == "get_ci_lifecycle_active_actions":
            return await run_blocking(client.get_ci_lifecycle_active_actions, **kwargs)
        if action == "get_ci_lifecycle_status":
            return await run_blocking(client.get_ci_lifecycle_status, **kwargs)
        if action == "set_ci_lifecycle_status":
            return await run_blocking(client.set_ci_lifecycle_status, **kwargs)
        raise ValueError(f"Unknown action: {action}")
