from typing import Any
from pydantic_ai import Agent, RunContext
import asyncio
import sys

# Mocking model so we don't need real API keys
from pydantic_ai.models.test import TestModel

def create_agents() -> Agent:
    """
    Factory function using the user's proposed nested pattern.
    """
    # 1. Create a sub-agent
    delegate_agent = Agent(
        model=TestModel(),
        system_prompt="I am a worker.",
        name="Worker_Agent"
    )

    # 2. Create the orchestrator
    orchestrator = Agent(
        model=TestModel(),
        system_prompt="I am the boss.",
        name="Orchestrator_Agent"
    )

    # 3. Define & register tool capturing the delegate_agent
    @orchestrator.tool
    async def delegate_task(ctx: RunContext[Any], task: str) -> str:
        """Delegate a task."""
        print(f"Delegating: {task}")
        # Capture delegate_agent from closure
        result = await delegate_agent.run(task)
        return result.output

    return orchestrator

async def main():
    try:
        agent = create_agents()
        print("Agent created successfully.")
        
        # Run it to see if pickling happens during run
        result = await agent.run("Do something")
        print("Run result:", result.output)
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
