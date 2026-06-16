"""MCP tools for knowledge management operations.

Auto-generated from mcp_server.py during ecosystem standardization.
"""

from agent_utilities.mcp_utilities import resolve_action
from fastmcp import Context, FastMCP
from fastmcp.dependencies import Depends
from pydantic import Field

from servicenow_api.auth import get_client


def register_knowledge_management_tools(mcp: FastMCP):
    @mcp.tool(tags={"knowledge_management"})
    async def servicenow_knowledge_management(
        action: str = Field(
            description="Action to perform. Must be one of: 'get_knowledge_articles', 'get_knowledge_article', 'get_knowledge_article_attachment', 'get_featured_knowledge_article', 'get_most_viewed_knowledge_articles'"
        ),
        params_json: str = Field(
            default="{}", description="JSON string of parameters to pass to the action."
        ),
        client=Depends(get_client),
        ctx: Context | None = Field(
            default=None, description="MCP context for progress reporting"
        ),
    ) -> dict:
        """Manage servicenow knowledge management operations."""
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
                "get_knowledge_articles",
                "get_knowledge_article",
                "get_knowledge_article_attachment",
                "get_featured_knowledge_article",
                "get_most_viewed_knowledge_articles",
            ],
            service="servicenow-api",
        )
        if isinstance(resolved, dict):
            return resolved
        action = resolved

        if action == "get_knowledge_articles":
            return client.get_knowledge_articles(**kwargs)
        if action == "get_knowledge_article":
            return client.get_knowledge_article(**kwargs)
        if action == "get_knowledge_article_attachment":
            return client.get_knowledge_article_attachment(**kwargs)
        if action == "get_featured_knowledge_article":
            return client.get_featured_knowledge_article(**kwargs)
        if action == "get_most_viewed_knowledge_articles":
            return client.get_most_viewed_knowledge_articles(**kwargs)
        raise ValueError(f"Unknown action: {action}")
