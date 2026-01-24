
import asyncio
import logging
import os
from pydantic_ai.mcp import MCPServerStreamableHTTP

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("debug_filter")

async def run_debug():
    url = "http://localhost:8004/mcp"
    tag = "change_management"
    
    logger.info(f"Connecting to {url} to filter for tag: {tag}")
    
    async with MCPServerStreamableHTTP(url=url) as server:
        # Note: MCPServerStreamableHTTP context manager might not be needed if not using context vars, 
        # but let's be safe.
        
        # We need to manually trigger tool fetching to inspect them.
        # list_tools() usually returns a list of ToolDefinition.
        
        logger.info("Fetching tools...")
        tools = await server.list_tools()
        logger.info(f"Fetched {len(tools)} tools.")
        
        for tool_def in tools:
            # Replicate the logic from servicenow_agent.py
            metadata = tool_def.metadata or {}
            meta = metadata.get("meta") or {}
            fastmcp_meta = meta.get("_fastmcp") or {}
            tags = fastmcp_meta.get("tags", [])
            
            if not tags:
                tags = metadata.get("tags", [])
                
            # Log specific details for change related tools or the tag
            is_change_tool = "change" in tool_def.name
            has_tag = tag in tags
            
            if is_change_tool or has_tag:
                 logger.info(f"Tool: {tool_def.name}")
                 logger.info(f"  Tags: {tags}")
                 logger.info(f"  Match '{tag}': {has_tag}")
                 logger.info(f"  Metadata: {tool_def.metadata}")
                 print("-" * 20)

if __name__ == "__main__":
    asyncio.run(run_debug())
