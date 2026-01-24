import asyncio
from mcp.client.streamable_http import StreamableHTTPSession
from mcp.types import ListToolsRequest

async def main():
    async with StreamableHTTPSession("http://localhost:8004/mcp") as session:
        result = await session.list_tools()
        print(f"Total Tools: {len(result.tools)}")
        for tool in result.tools:
            print(f"Tool: {tool.name}, Tags: {getattr(tool, 'tags', 'N/A')}")
            if tool.name == 'get_incidents':
                print("FOUND get_incidents!")

if __name__ == "__main__":
    asyncio.run(main())
