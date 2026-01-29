#!/usr/bin/env python3
import asyncio
import sys
from servicenow_api.servicenow_agent import stream_chat, chat, node_chat

# Attempt to import assuming dependencies are installed
import os

__version__ = "0.1.0"

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

try:
    from servicenow_api.servicenow_agent import create_agent
except ImportError as e:
    print(f"Import Error: {e}")
    print("Please install dependencies via `pip install .[all]`")
    sys.exit(1)


async def main():
    print("Initializing A2A Agent...")
    try:
        agent = create_agent(
            provider="openai",
            model_id=os.getenv("MODEL_ID", "qwen/qwen3-4b-2507"),
            base_url=os.getenv(
                "OPENAI_BASE_URL", "http://host.docker.internal:1234/v1"
            ),  # 127.0.0.1
            api_key=os.getenv("OPENAI_API_KEY", "llama"),
            mcp_url=os.getenv("MCP_URL", "http://localhost:8005/mcp"),  # 127.0.0.1
            mcp_config=None,
        )

        print("Agent initialized successfully.")

        # Define sample questions
        questions = [
            "Can you list the incidents",
            # "Can you create an incident with the description: Test, Title: Test, ...."
        ]

        print("\n--- Starting Sample Chat Validation ---\n")

        for q in questions:
            print(f"\n\n\nUser: {q}")
            try:
                # Only run one to test
                await stream_chat(agent=agent, prompt=q)
                await chat(agent=agent, prompt=q)
                await node_chat(agent=agent, prompt=q)
                if hasattr(agent, "tools"):
                    print(f"Agent Tools: {[t.__name__ for t in agent.tools]}")
                elif hasattr(agent, "_tools"):
                    print(f"Agent Tools: {[t.__name__ for t in agent._tools]}")

            except Exception as e:
                print(f"\n\nError processing question '{q}': {e}")

    except Exception as e:
        print(f"Validation failed with error: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
