import os
import argparse
import uvicorn
from typing import List, Optional
from pydantic_ai import Agent
from pydantic_ai.models.openai import OpenAIChatModel
from pydantic_ai.models.anthropic import AnthropicModel
from pydantic_ai.models.google import GoogleModel
from pydantic_ai.models.huggingface import HuggingFaceModel
from pydantic_ai.toolsets.fastmcp import FastMCPToolset
from fasta2a import Skill

# Default Configuration
DEFAULT_PROVIDER = "openai"
DEFAULT_MODEL_ID = "qwen3:4b"
DEFAULT_OPENAI_BASE_URL = os.getenv("OPENAI_BASE_URL", "http://ollama.arpa/v1")
DEFAULT_OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "ollama")
DEFAULT_MCP_URL = "http://media-downloader-mcp.arpa/mcp"
DEFAULT_ALLOWED_TOOLS: List[str] = [
    "download_media",
]

AGENT_NAME = "MediaDownloaderAgent"
AGENT_DESCRIPTION = "A specialist agent for downloading media content from the web."
INSTRUCTIONS = (
    "You are a friendly media retrieval expert specialized in downloading media files.\n\n"
    "Your primary tool is 'download_media', which allows you to download videos or audio "
    "from various platforms (e.g., YouTube). "
    "By default, save downloaded files to the ~/Downloads directory "
    "unless the user explicitly directs you to use a different directory.\n\n"
    "Key capabilities:\n"
    "- Download either full video or audio-only formats.\n"
    "- Support batch downloading of multiple media files in a single request.\n\n"
    "Always clearly state the full save path(s) of the downloaded file(s) in your final response.\n\n"
    "Maintain a warm, friendly, and helpful tone in all interactions with the user.\n"
    "Handle any errors gracefully: if a download fails, explain the issue politely and suggest alternatives if possible."
)


def create_agent(
    provider: str = DEFAULT_PROVIDER,
    model_id: str = DEFAULT_MODEL_ID,
    base_url: Optional[str] = None,
    api_key: Optional[str] = None,
    mcp_url: str = DEFAULT_MCP_URL,
    allowed_tools: List[str] = DEFAULT_ALLOWED_TOOLS,
) -> Agent:
    """
    Factory function to create the AGENT_NAME with configuration.
    """
    # Define the model based on provider
    model = None

    if provider == "openai":
        # Configure environment for OpenAI compatible model (e.g. Ollama)
        # Use defaults if not provided to ensure we point to the expected local server by default
        target_base_url = base_url or DEFAULT_OPENAI_BASE_URL
        target_api_key = api_key or DEFAULT_OPENAI_API_KEY

        if target_base_url:
            os.environ["OPENAI_BASE_URL"] = target_base_url
        if target_api_key:
            os.environ["OPENAI_API_KEY"] = target_api_key
        model = OpenAIChatModel(model_id, provider="openai")

    elif provider == "anthropic":
        if api_key:
            os.environ["ANTHROPIC_API_KEY"] = api_key
        model = AnthropicModel(model_id)

    elif provider == "google":
        if api_key:
            # google-genai usually looks for GOOGLE_API_KEY or GEMINI_API_KEY
            os.environ["GEMINI_API_KEY"] = api_key
            os.environ["GOOGLE_API_KEY"] = api_key
        model = GoogleModel(model_id)

    elif provider == "huggingface":
        if api_key:
            os.environ["HF_TOKEN"] = api_key
        model = HuggingFaceModel(model_id)

    else:
        raise ValueError(f"Unsupported provider: {provider}")

    # Define the toolset using FastMCPToolset with the streamable HTTP URL
    # and filter for allowed tools only
    toolset = FastMCPToolset(client=mcp_url)
    filtered_toolset = toolset.filtered(
        lambda ctx, tool_def: tool_def.name in allowed_tools
    )

    # Define the agent
    agent_definition = Agent(
        model,
        system_prompt=INSTRUCTIONS,
        name=AGENT_NAME,
        toolsets=[filtered_toolset],
    )

    return agent_definition


# Expose as A2A server (Default instance for ASGI runners)
agent = create_agent()

# Define skills for the Agent Card
skills = [
    Skill(
        id="download_media",
        name="Download Media",
        description="Download videos or audio from various platforms (YouTube, Twitter, etc.) to the local filesystem.",
        tags=["media", "video", "audio", "download"],
        examples=["Download this youtube video: https://youtu.be/example"],
        input_modes=["text"],
        output_modes=["text"],
    )
]


def agent_server():
    parser = argparse.ArgumentParser(description=f"Run the {AGENT_NAME} A2A Server")
    parser.add_argument("--host", default="0.0.0.0", help="Host to bind the server to")
    parser.add_argument(
        "--port", type=int, default=8000, help="Port to bind the server to"
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
    parser.add_argument(
        "--allowed-tools",
        nargs="*",
        default=DEFAULT_ALLOWED_TOOLS,
        help="List of allowed MCP tools",
    )

    args = parser.parse_args()

    base_url = args.base_url
    api_key = args.api_key

    if args.provider == "openai":
        if base_url is None:
            base_url = DEFAULT_OPENAI_BASE_URL
        if api_key is None:
            api_key = DEFAULT_OPENAI_API_KEY

    print(
        f"Starting {AGENT_NAME} with provider={args.provider}, model={args.model_id}, mcp={args.mcp_url}"
    )

    cli_agent = create_agent(
        provider=args.provider,
        model_id=args.model_id,
        base_url=base_url,
        api_key=api_key,
        mcp_url=args.mcp_url,
        allowed_tools=args.allowed_tools,
    )
    cli_app = cli_agent.to_a2a(
        name=AGENT_NAME, description=AGENT_DESCRIPTION, version="1.3.29", skills=skills
    )

    uvicorn.run(
        cli_app,
        host=args.host,
        port=args.port,
    )


if __name__ == "__main__":
    agent_server()
