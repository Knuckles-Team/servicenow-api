import os
import argparse
import uvicorn
from typing import Optional, Dict
from pydantic_ai import Agent, RunContext
from pydantic_ai.models.openai import OpenAIChatModel
from pydantic_ai.models.anthropic import AnthropicModel
from pydantic_ai.models.google import GoogleModel
from pydantic_ai.models.huggingface import HuggingFaceModel
from pydantic_ai.toolsets.fastmcp import FastMCPToolset
from fasta2a import Skill

# Default Configuration
DEFAULT_PROVIDER = "openai"
DEFAULT_MODEL_ID = "qwen3:4b"  # Or "gpt-4o" if using OpenAI
DEFAULT_OPENAI_BASE_URL = os.getenv("OPENAI_BASE_URL", "http://ollama.arpa/v1")
DEFAULT_OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "ollama")
DEFAULT_MCP_URL = "http://localhost:8000/mcp"

# Detected tags from servicenow_mcp.py
TAGS = [
    "application",
    "cmdb",
    "cicd",
    "plugins",
    "source_control",
    "testing",
    "update_sets",
    "change_management",
    "import_sets",
    "incidents",
    "knowledge_management",
    "table_api",
    "auth",
    "custom_api",
]

AGENT_NAME = "ServiceNowOrchestrator"
AGENT_DESCRIPTION = (
    "A multi-agent system for managing ServiceNow tasks via delegated specialists."
)


def create_model(
    provider: str,
    model_id: str,
    base_url: Optional[str] = None,
    api_key: Optional[str] = None,
):
    if provider == "openai":
        target_base_url = base_url or DEFAULT_OPENAI_BASE_URL
        target_api_key = api_key or DEFAULT_OPENAI_API_KEY
        # Set env vars for the specialized agents if needed by the model init
        # (Though we pass them explicitly usually, some libs fallback to env)
        if target_base_url:
            os.environ["OPENAI_BASE_URL"] = target_base_url
        if target_api_key:
            os.environ["OPENAI_API_KEY"] = target_api_key
        return OpenAIChatModel(model_id, provider="openai")

    elif provider == "anthropic":
        if api_key:
            os.environ["ANTHROPIC_API_KEY"] = api_key
        return AnthropicModel(model_id)

    elif provider == "google":
        if api_key:
            os.environ["GEMINI_API_KEY"] = api_key
            os.environ["GOOGLE_API_KEY"] = api_key
        return GoogleModel(model_id)

    elif provider == "huggingface":
        if api_key:
            os.environ["HF_TOKEN"] = api_key
        return HuggingFaceModel(model_id)

    else:
        raise ValueError(f"Unsupported provider: {provider}")


def create_child_agent(
    tag: str,
    mcp_url: str,
    provider: str,
    model_id: str,
    base_url: Optional[str] = None,
    api_key: Optional[str] = None,
) -> Agent:
    """
    Creates a specialized child agent for a specific tag.
    """
    model = create_model(provider, model_id, base_url, api_key)

    # Create toolset and filter by tag
    toolset = FastMCPToolset(client=mcp_url)

    # filtered returns a new toolset with only tools that match the predicate
    # The predicate receives (context, tool_definition)
    # We check if the 'tag' is present in tool_definition.tags
    filtered_toolset = toolset.filtered(
        lambda ctx, tool_def: tag in (tool_def.tags or [])
    )

    system_prompt = (
        f"You are a specialized ServiceNow agent focused on '{tag}' tasks. "
        f"You have access to tools tagged with '{tag}'. "
        "Use them to fulfill the user's request efficiently. "
        "If a task is outside your scope, kindly indicate that."
    )

    return Agent(
        model,
        system_prompt=system_prompt,
        name=f"ServiceNow_{tag}_Specialist",
        toolsets=[filtered_toolset],
    )


def create_orchestrator(
    provider: str = DEFAULT_PROVIDER,
    model_id: str = DEFAULT_MODEL_ID,
    base_url: Optional[str] = None,
    api_key: Optional[str] = None,
    mcp_url: str = DEFAULT_MCP_URL,
) -> Agent:
    """
    Creates the parent Orchestrator agent with tools to delegate to children.
    """
    # 1. Create all child agents
    children: Dict[str, Agent] = {}
    for tag in TAGS:
        children[tag] = create_child_agent(
            tag, mcp_url, provider, model_id, base_url, api_key
        )

    # 2. Create Model for Parent
    model = create_model(provider, model_id, base_url, api_key)

    # 3. Create Delegation Tools
    # We create a list of callables that the parent can use as tools.
    delegation_tools = []

    for tag, child_agent in children.items():

        # Define the tool function.
        # CAUTION: Python closures capture variables by reference.
        # We must bind 'child_agent' and 'tag' to the function scope using default args.
        async def delegate_task(
            ctx: RunContext, task_description: str, _agent=child_agent, _tag=tag
        ) -> str:
            # We don't have a docstring here yet, we'll set it below.
            print(
                f"[Orchestrator] Delegating task to {_tag} specialist: {task_description[:50]}..."
            )
            try:
                result = await _agent.run(task_description)
                return result.data
            except Exception as e:
                return f"Error executing task with {_tag} specialist: {str(e)}"

        # Set metadata for the tool
        delegate_task.__name__ = f"delegate_to_{tag}"
        delegate_task.__doc__ = (
            f"Delegate a task related to '{tag}' (e.g., {tag} management, queries) "
            f"to the dedicated {tag} specialist agent. "
            f"Provide a clear, self-contained description of the subtask."
        )

        delegation_tools.append(delegate_task)

    # 4. Create Parent Agent
    system_prompt = (
        "You are the ServiceNow Orchestrator Agent. "
        "Your goal is to assist the user by delegating tasks to specialized child agents. "
        "Analyze the user's request and determine which domain(s) it falls into "
        "(e.g., incidents, change_management, cmdb). "
        "Then, call the appropriate delegation tool(s) with a specific task description. "
        "Synthesize the results from the child agents into a final helpful response. "
        "Do not attempt to perform ServiceNow actions directly; always delegate."
    )

    orchestrator = Agent(
        model,
        system_prompt=system_prompt,
        name=AGENT_NAME,
        tools=delegation_tools,  # Register the wrapper functions as tools
    )

    return orchestrator


# Create the default instance for A2A
agent = create_orchestrator()

# Define Skills for Agent Card (High-level capabilities)
skills = []
for tag in TAGS:
    skills.append(
        Skill(
            id=f"servicenow_{tag}",
            name=f"ServiceNow {tag.replace('_', ' ').title()}",
            description=f"Manage and query ServiceNow {tag.replace('_', ' ')}.",
            tags=[tag, "servicenow"],
            input_modes=["text"],
            output_modes=["text"],
        )
    )


def agent_server():
    parser = argparse.ArgumentParser(description=f"Run the {AGENT_NAME} A2A Server")
    parser.add_argument("--host", default="0.0.0.0", help="Host to bind the server to")
    parser.add_argument(
        "--port", type=int, default=9000, help="Port to bind the server to"
    )
    parser.add_argument("--reload", action="store_true", help="Enable auto-reload")

    parser.add_argument(
        "--provider",
        default=DEFAULT_PROVIDER,
        choices=["openai", "anthropic", "google", "huggingface"],
        help="LLM Provider",
    )
    parser.add_argument("--model-id", default=DEFAULT_MODEL_ID, help="LLM Model ID")
    parser.add_argument(
        "--base-url",
        default=None,
        help="LLM Base URL (for OpenAI compatible providers)",
    )
    parser.add_argument("--api-key", default=None, help="LLM API Key")
    parser.add_argument("--mcp-url", default=DEFAULT_MCP_URL, help="MCP Server URL")

    args = parser.parse_args()

    print(
        f"Starting {AGENT_NAME} with provider={args.provider}, model={args.model_id}, mcp={args.mcp_url}"
    )

    # Create the agent with CLI args
    cli_agent = create_orchestrator(
        provider=args.provider,
        model_id=args.model_id,
        base_url=args.base_url,
        api_key=args.api_key,
        mcp_url=args.mcp_url,
    )

    # Create A2A App
    cli_app = cli_agent.to_a2a(
        name=AGENT_NAME, description=AGENT_DESCRIPTION, version="1.3.30", skills=skills
    )

    uvicorn.run(
        cli_app,
        host=args.host,
        port=args.port,
    )


if __name__ == "__main__":
    agent_server()
