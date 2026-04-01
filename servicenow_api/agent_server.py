#!/usr/bin/python

import os
from pathlib import Path
import logging

import sys
import warnings
from agent_utilities import (
    build_system_prompt_from_workspace,
    create_agent_parser,
    create_graph_agent_server,
    initialize_workspace,
    load_identity,
    get_workspace_path,
)

__version__ = "1.6.56"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()],
)
logger = logging.getLogger(__name__)


initialize_workspace()
meta = load_identity()
DEFAULT_AGENT_NAME = os.getenv("DEFAULT_AGENT_NAME", meta.get("name", "Servicenow Api"))
DEFAULT_AGENT_DESCRIPTION = os.getenv(
    "AGENT_DESCRIPTION",
    meta.get("description", "AI agent for ServiceNow Api management."),
)
DEFAULT_AGENT_SYSTEM_PROMPT = os.getenv(
    "AGENT_SYSTEM_PROMPT",
    meta.get("content") or build_system_prompt_from_workspace(),
)


def agent_template(mcp_url: str = None, mcp_config: str = None, **kwargs):
    from agent_utilities import create_graph_agent
    from servicenow_api.graph_config import TAG_PROMPTS, TAG_ENV_VARS

    effective_mcp_config = mcp_config or os.getenv("MCP_CONFIG") or "mcp_config.json"
    effective_mcp_url = mcp_url or os.getenv("MCP_URL")

    mcp_toolsets = []
    if effective_mcp_config:
        from agent_utilities.mcp_utilities import load_mcp_config

        try:

            config_path = effective_mcp_config
            if not os.path.isabs(config_path) and "/" not in config_path:
                # Check package-relative path first (for robust orchestration)
                pkg_config = Path(__file__).parent / config_path
                if pkg_config.exists():
                    config_path = str(pkg_config)
                else:
                    # Fallback to workspace
                    ws_config = get_workspace_path(config_path)
                    if ws_config.exists():
                        config_path = str(ws_config)

            if os.path.exists(config_path):
                mcp_toolsets = load_mcp_config(config_path)
                logger.info(
                    f"servicenow-api: Loaded {len(mcp_toolsets)} MCP servers from {config_path}"
                )
        except Exception as e:
            logger.error(
                f"servicenow-api: Failed to load MCP config {effective_mcp_config}: {e}"
            )

    return create_graph_agent(
        mcp_url=effective_mcp_url,
        mcp_config=effective_mcp_config or "",
        mcp_toolsets=mcp_toolsets,
        name=f"{DEFAULT_AGENT_NAME} Graph Agent",
        tag_prompts=TAG_PROMPTS,
        tag_env_vars=TAG_ENV_VARS,
        **kwargs,
    )


def agent_server():

    warnings.filterwarnings("ignore", message=".*urllib3.*or chardet.*")
    warnings.filterwarnings("ignore", category=DeprecationWarning, module="fastmcp")

    print(f"{DEFAULT_AGENT_NAME} v{__version__}", file=sys.stderr)
    parser = create_agent_parser()

    args = parser.parse_args()

    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)
        logger.debug("Debug mode enabled")

    graph_bundle = agent_template(
        provider=args.provider,
        agent_model=args.model_id,
        base_url=args.base_url,
        api_key=args.api_key,
        custom_skills_directory=args.custom_skills_directory,
        debug=args.debug,
        ssl_verify=not args.insecure,
    )

    create_graph_agent_server(
        graph_bundle=graph_bundle,
        host=args.host,
        port=args.port,
        enable_web_ui=args.web,
        enable_otel=args.otel,
        otel_endpoint=args.otel_endpoint,
        otel_headers=args.otel_headers,
        otel_public_key=args.otel_public_key,
        otel_secret_key=args.otel_secret_key,
        otel_protocol=args.otel_protocol,
        debug=args.debug,
    )


if __name__ == "__main__":
    agent_server()
