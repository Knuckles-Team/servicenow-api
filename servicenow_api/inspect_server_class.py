
import asyncio
import logging
from pydantic_ai.mcp import MCPServerStreamableHTTP

logging.basicConfig(level=logging.INFO)

async def inspect():
    url = "http://localhost:8004/mcp"
    print(f"Connecting to {url}")
    server = MCPServerStreamableHTTP(url=url)
    
    print("Server attributes:", dir(server))
    
    # Try to find a method that fetches tools
    # Expected methods: get_tools, prepare, etc.
    
    # Run async inspection
    try:
        # Pydantic AI usually uses get_tools or similar protocol
        # Let's try to call get_tool_definitions if it exists (internal?)
        pass
    except Exception as e:
        print(e)
        
    # We can try to use the 'tools' property if it's a coroutine
    # or iterate it?
    
    # We'll just look at dir() first.
    
if __name__ == "__main__":
    asyncio.run(inspect())
