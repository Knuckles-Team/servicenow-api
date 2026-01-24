
import asyncio
import os
import logging
import json
from mcp import ClientSession
from mcp.client.sse import sse_client
# Note: mcp.client.http.http_client might be different depending on version.
# Let's try importing compatible modules.

# Check for streamable http support if not SSE.
# servicenow_agent uses MCPServerStreamableHTTP.
# Let's assume the endpoint provided defaults to SSE if we use the right client, or we use a custom http client.

# However, standard mcp 1.0+ usually has sse_client. 
# Let's try sse_client first as it's common for /mcp endpoints.
# If the URL is just /mcp, it might be the SSE endpoint.

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("inspect_mcp")

async def verify_tools():
    mcp_url = os.getenv("MCP_URL", "http://servicenow-mcp:8004/mcp")
    logger.info(f"Connecting to MCP URL: {mcp_url}")

    # Try SSE client since that's most common for simple http endpoints
    try:
        async with sse_client(mcp_url) as (read, write):
            async with ClientSession(read, write) as session:
                logger.info("Initializing session...")
                await session.initialize()
                
                logger.info("Listing tools...")
                result = await session.list_tools()
                
                logger.info(f"Found {len(result.tools)} tools.")
                
                for tool in result.tools:
                    print(f"\nTool: {tool.name}")
                    print(f"  Description: {tool.description}")
                    # Tags might be in tool definition (unlikely in standard schema?) 
                    # or in a custom dict.
                    # Standard Tool model has: name, description, inputSchema.
                    # Metadata?
                    # Let's inspect the raw object or attributes
                    
                    # It seems 'tags' is a community convention or fastmcp extension?
                    # fastmcp uses decorator tagging.
                    # Let's print all attributes to find where tags are hiding.
                    if hasattr(tool, "tags"):
                        print(f"  Tags (direct): {tool.tags}")
                    
                    # Check for extra attributes (pydantic model)
                    if hasattr(tool, "model_dump"):
                        dump = tool.model_dump()
                        print(f"  Dump: {json.dumps(dump, default=str)}")
                        
    except Exception as e:
        logger.error(f"Error fetching tools: {e}")

if __name__ == "__main__":
    asyncio.run(verify_tools())
