
import os
import sys
import asyncio
import logging
from servicenow_api.servicenow_agent import create_agent

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("test_agent")

async def test_tools():
    mcp_url = "http://localhost:8004/mcp"
    print(f"Testing agent with MCP URL: {mcp_url}")
    
    try:
        agent = create_agent(mcp_url=mcp_url)
        print("Agent created. Running task...")
        
        # We need to run the agent to trigger tool loading.
        # We'll ask it to list change requests, which should delegate to change_management agent.
        
        # Note: We need a model that won't fail or mock it.
        # The agent uses DEFAULT_PROVIDER. If validation fails, we might need a dummy model.
        # But let's try running it. If it fails on LLM call, we might still see the tool filter logs 
        # as it prepares the context (which includes tools).
        
        # To avoid actual LLM calls which might not work or cost money, we can mock the model?
        # create_agent allows passing provider/model.
        
        # We can try to use a dummy/test model if pydantic_ai supports it.
        # Otherwise, just running it and failing on API key is fine as long as tools are loaded first.
        # Tools are usually rendered into system prompt/schema before LLM call.
        
        try:
            await agent.run("List all change requests")
        except Exception as e:
            print(f"Agent run failed (expected if no LLM): {e}")
            
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_tools())
