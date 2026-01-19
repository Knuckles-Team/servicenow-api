#!/usr/bin/python
# coding: utf-8
import json
import os
import argparse
import logging
import uvicorn
from typing import Optional, Any, List
from contextlib import asynccontextmanager

from fastmcp import Client
from pydantic_ai import Agent, ModelSettings
from pydantic_ai.mcp import load_mcp_servers
from pydantic_ai.toolsets.fastmcp import FastMCPToolset
from pydantic_ai_skills import SkillsToolset
from pydantic_ai.models.openai import OpenAIChatModel
from pydantic_ai.models.anthropic import AnthropicModel
from pydantic_ai.models.google import GoogleModel
from pydantic_ai.models.huggingface import HuggingFaceModel
from fasta2a import Skill
from servicenow_api.utils import (
    to_integer,
    to_boolean,
    get_mcp_config_path,
    get_skills_path,
    load_skills_from_directory,
)

from fastapi import FastAPI, Request
from starlette.responses import Response, StreamingResponse
from pydantic import ValidationError
from pydantic_ai.ui import SSE_CONTENT_TYPE
from pydantic_ai.ui.ag_ui import AGUIAdapter

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()],  # Output to console
)
logging.getLogger("pydantic_ai").setLevel(logging.INFO)
logging.getLogger("fastmcp").setLevel(logging.INFO)
logging.getLogger("httpx").setLevel(logging.INFO)
logger = logging.getLogger(__name__)

DEFAULT_HOST = os.getenv("HOST", "0.0.0.0")
DEFAULT_PORT = to_integer(string=os.getenv("PORT", "9000"))
DEFAULT_DEBUG = to_boolean(string=os.getenv("DEBUG", "False"))
DEFAULT_PROVIDER = os.getenv("PROVIDER", "openai")
DEFAULT_MODEL_ID = os.getenv("MODEL_ID", "qwen/qwen3-8b")
DEFAULT_OPENAI_BASE_URL = os.getenv("OPENAI_BASE_URL", "http://127.0.0.1:1234/v1")
DEFAULT_OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "ollama")
DEFAULT_MCP_URL = os.getenv("MCP_URL", None)
DEFAULT_MCP_CONFIG = os.getenv("MCP_CONFIG", get_mcp_config_path())
DEFAULT_SKILLS_DIRECTORY = os.getenv("SKILLS_DIRECTORY", get_skills_path())
DEFAULT_ENABLE_WEB_UI = to_boolean(os.getenv("ENABLE_WEB_UI", "False"))

AGENT_NAME = "ServiceNow"
AGENT_DESCRIPTION = "An agent built with Agent Skills and ServiceNow MCP tools to maximize ServiceNow interactivity."
AGENT_SYSTEM_PROMPT = (
    "You are the ServiceNow Orchestrator Agent. "
    "Your goal is to assist the user by delegating tasks to specialized child agents. "
    "Analyze the user's request and determine which domain(s) it falls into "
    "(e.g., incidents, change_management, cmdb). "
    "Then, call the appropriate delegation tool(s) with a specific task description. "
    "Synthesize the results from the child agents into a final helpful response. "
    "Do not attempt to perform ServiceNow actions directly; always delegate."
)


def create_model(
    provider: str = DEFAULT_PROVIDER,
    model_id: str = DEFAULT_MODEL_ID,
    base_url: Optional[str] = DEFAULT_OPENAI_BASE_URL,
    api_key: Optional[str] = DEFAULT_OPENAI_API_KEY,
):
    if provider == "openai":
        target_base_url = base_url or DEFAULT_OPENAI_BASE_URL
        target_api_key = api_key or DEFAULT_OPENAI_API_KEY
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


def create_agent(
    provider: str = DEFAULT_PROVIDER,
    model_id: str = DEFAULT_MODEL_ID,
    base_url: Optional[str] = None,
    api_key: Optional[str] = None,
    mcp_url: str = DEFAULT_MCP_URL,
    mcp_config: str = DEFAULT_MCP_CONFIG,
    skills_directory: str = DEFAULT_SKILLS_DIRECTORY,
) -> Agent:
    agent_toolsets = []

    if mcp_config:
        mcp_toolset = load_mcp_servers(mcp_config)
        agent_toolsets.extend(mcp_toolset)
        logger.info(f"Connected to MCP Config JSON: {mcp_toolset}")
    elif mcp_url:
        fastmcp_toolset = FastMCPToolset(Client[Any](mcp_url, timeout=3600))
        agent_toolsets.append(fastmcp_toolset)
        logger.info(f"Connected to MCP Server: {mcp_url}")

    if skills_directory and os.path.exists(skills_directory):
        logger.debug(f"Loading skills {skills_directory}")
        skills = SkillsToolset(directories=[str(skills_directory)])
        agent_toolsets.append(skills)
        logger.info(f"Loaded Skills at {skills_directory}")

    # Create the Model
    model = create_model(provider, model_id, base_url, api_key)

    logger.info("Initializing Agent...")

    settings = ModelSettings(timeout=3600.0)

    return Agent(
        model=model,
        system_prompt=AGENT_SYSTEM_PROMPT,
        name="GitLab_Agent",
        toolsets=agent_toolsets,
        deps_type=Any,
        model_settings=settings,
    )


async def chat(agent: Agent, prompt: str):
    result = await agent.run(prompt)
    print(f"Response:\n\n{result.output}")


async def node_chat(agent: Agent, prompt: str) -> List:
    nodes = []
    async with agent.iter(prompt) as agent_run:
        async for node in agent_run:
            nodes.append(node)
            print(node)
    return nodes


async def stream_chat(agent: Agent, prompt: str) -> None:
    # Option A: Easiest & most common - just stream the final text output
    async with agent.run_stream(prompt) as result:
        async for text_chunk in result.stream_text(
            delta=True
        ):  # ← streams partial text deltas
            print(text_chunk, end="", flush=True)
        print("\nDone!")  # optional


def create_agent_server(
    provider: str = DEFAULT_PROVIDER,
    model_id: str = DEFAULT_MODEL_ID,
    base_url: Optional[str] = None,
    api_key: Optional[str] = None,
    mcp_url: str = DEFAULT_MCP_URL,
    mcp_config: str = DEFAULT_MCP_CONFIG,
    skills_directory: Optional[str] = DEFAULT_SKILLS_DIRECTORY,
    debug: Optional[bool] = DEFAULT_DEBUG,
    host: Optional[str] = DEFAULT_HOST,
    port: Optional[int] = DEFAULT_PORT,
    enable_web_ui: bool = DEFAULT_ENABLE_WEB_UI,
):
    print(
        f"Starting {AGENT_NAME} with provider={provider}, model={model_id}, mcp={mcp_url} | {mcp_config}"
    )
    agent = create_agent(
        provider=provider,
        model_id=model_id,
        base_url=base_url,
        api_key=api_key,
        mcp_url=mcp_url,
        mcp_config=mcp_config,
        skills_directory=skills_directory,
    )

    # Define Skills for Agent Card (High-level capabilities)
    if skills_directory and os.path.exists(skills_directory):
        skills = load_skills_from_directory(skills_directory)
        logger.info(f"Loaded {len(skills)} skills from {skills_directory}")
    else:
        skills = [
            Skill(
                id="servicenow_agent",
                name="ServiceNow Agent",
                description="This ServiceNow skill grants access to all ServiceNow tools provided by the ServiceNow MCP Server",
                tags=["servicenow"],
                input_modes=["text"],
                output_modes=["text"],
            )
        ]
    # Create A2A app explicitly before main app to bind lifespan
    a2a_app = agent.to_a2a(
        name=AGENT_NAME,
        description=AGENT_DESCRIPTION,
        version="1.4.5",
        skills=skills,
        debug=debug,
    )

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        # Trigger A2A (sub-app) startup/shutdown events
        # This is critical for TaskManager initialization in A2A
        if hasattr(a2a_app, "router"):
            async with a2a_app.router.lifespan_context(a2a_app):
                yield
        else:
            yield

    # Create main FastAPI app
    app = FastAPI(
        title=f"{AGENT_NAME} - A2A + AG-UI Server",
        description=AGENT_DESCRIPTION,
        debug=debug,
        lifespan=lifespan,
    )

    # Mount A2A as sub-app at /a2a
    app.mount("/a2a", a2a_app)

    # Add AG-UI endpoint (POST to /ag-ui)
    @app.post("/ag-ui")
    async def ag_ui_endpoint(request: Request) -> Response:
        accept = request.headers.get("accept", SSE_CONTENT_TYPE)
        try:
            # Parse incoming AG-UI RunAgentInput from request body
            run_input = AGUIAdapter.build_run_input(await request.body())
        except ValidationError as e:
            return Response(
                content=json.dumps(e.json()),
                media_type="application/json",
                status_code=422,
            )

        # Create adapter and run the agent → stream AG-UI events
        adapter = AGUIAdapter(agent=agent, run_input=run_input, accept=accept)
        event_stream = adapter.run_stream()  # Runs agent, yields events
        sse_stream = adapter.encode_stream(event_stream)  # Encodes to SSE

        return StreamingResponse(
            sse_stream,
            media_type=accept,
        )

    # Mount Web UI if enabled
    if enable_web_ui:
        web_ui = agent.to_web(instructions=AGENT_SYSTEM_PROMPT)
        app.mount("/", web_ui)
        logger.info(
            "Starting server on %s:%s (A2A at /a2a, AG-UI at /ag-ui, Web UI: %s)",
            host,
            port,
            "Enabled at /" if enable_web_ui else "Disabled",
        )

    uvicorn.run(
        app,
        host=host,
        port=port,
        timeout_keep_alive=1800, # 30 minute timeout
        timeout_graceful_shutdown=60,
        log_level="debug" if debug else "info",
    )


def agent_server():
    parser = argparse.ArgumentParser(
        description=f"Run the {AGENT_NAME} A2A + AG-UI Server"
    )
    parser.add_argument(
        "--host", default=DEFAULT_HOST, help="Host to bind the server to"
    )
    parser.add_argument(
        "--port", type=int, default=DEFAULT_PORT, help="Port to bind the server to"
    )
    parser.add_argument(
        "--web",
        action="store_true",
        default=DEFAULT_ENABLE_WEB_UI,
        help="Enable Pydantic AI Web UI",
    )
    parser.add_argument("--debug", type=bool, default=DEFAULT_DEBUG, help="Debug mode")
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
        default=DEFAULT_OPENAI_BASE_URL,
        help="LLM Base URL (for OpenAI compatible providers)",
    )
    parser.add_argument("--api-key", default=DEFAULT_OPENAI_API_KEY, help="LLM API Key")
    parser.add_argument("--mcp-url", default=DEFAULT_MCP_URL, help="MCP Server URL")
    parser.add_argument(
        "--mcp-config", default=DEFAULT_MCP_CONFIG, help="MCP Server Config"
    )
    args = parser.parse_args()

    if args.debug:
        # Force reconfiguration of logging
        for handler in logging.root.handlers[:]:
            logging.root.removeHandler(handler)

        logging.basicConfig(
            level=logging.DEBUG,
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            handlers=[logging.StreamHandler()],  # Output to console
            force=True,
        )
        logging.getLogger("pydantic_ai").setLevel(logging.DEBUG)
        logging.getLogger("fastmcp").setLevel(logging.DEBUG)
        logging.getLogger("httpcore").setLevel(logging.DEBUG)
        logging.getLogger("httpx").setLevel(logging.DEBUG)
        logger.setLevel(logging.DEBUG)
        logger.debug("Debug mode enabled")

    # Create the agent with CLI args
    # Create the agent with CLI args
    create_agent_server(
        provider=args.provider,
        model_id=args.model_id,
        base_url=args.base_url,
        api_key=args.api_key,
        mcp_url=args.mcp_url,
        mcp_config=args.mcp_config,
        debug=args.debug,
        host=args.host,
        port=args.port,
        enable_web_ui=args.web,
    )


if __name__ == "__main__":
    agent_server()
