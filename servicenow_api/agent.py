#!/usr/bin/python
# coding: utf-8
import os
import logging

from agent_utilities import (
    build_system_prompt_from_workspace,
    create_agent_parser,
    create_agent_server,
    initialize_workspace,
    load_identities,
)

__version__ = "1.6.26"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()],
)
logger = logging.getLogger(__name__)

# Load identity and system prompt from workspace
initialize_workspace()
identities = load_identities()

# Prepare supervisor identity
supervisor_meta = identities.get("supervisor", identities.get("default", {}))
DEFAULT_AGENT_NAME = os.getenv(
    "DEFAULT_AGENT_NAME", supervisor_meta.get("name", "Servicenow Api")
)
DEFAULT_AGENT_DESCRIPTION = os.getenv(
    "AGENT_DESCRIPTION",
    supervisor_meta.get("description", "A multi-agent system."),
)
DEFAULT_AGENT_SYSTEM_PROMPT = os.getenv(
    "AGENT_SYSTEM_PROMPT",
    supervisor_meta.get("content") or build_system_prompt_from_workspace(),
)

# Prepare child agent definitions from IDENTITY.md sections
CHILD_AGENT_DEFS = {
    tag: (data["content"], data["name"])
    for tag, data in identities.items()
    if tag not in ["supervisor", "default"]
}


def agent_server():
    print(f"{DEFAULT_AGENT_NAME} v{__version__}")
    parser = create_agent_parser()

    args = parser.parse_args()

    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)
        logger.debug("Debug mode enabled")

    create_agent_server(
        provider=args.provider,
        model_id=args.model_id,
        base_url=args.base_url,
        api_key=args.api_key,
        mcp_url=args.mcp_url,
        mcp_config=args.mcp_config,
        custom_skills_directory=args.custom_skills_directory,
        debug=args.debug,
        host=args.host,
        port=args.port,
        enable_web_ui=args.web,
        ssl_verify=not args.insecure,
        name=DEFAULT_AGENT_NAME,
        system_prompt=DEFAULT_AGENT_SYSTEM_PROMPT,
        enable_otel=args.otel,
        otel_endpoint=args.otel_endpoint,
        otel_headers=args.otel_headers,
        otel_public_key=args.otel_public_key,
        otel_secret_key=args.otel_secret_key,
        otel_protocol=args.otel_protocol,
        agent_definitions=CHILD_AGENT_DEFS if CHILD_AGENT_DEFS else None,
    )


if __name__ == "__main__":
    agent_server()
