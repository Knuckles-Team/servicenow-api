#!/usr/bin/python
# coding: utf-8
import json
import os
import argparse
import logging
import uvicorn
from typing import Optional, Any, List
from contextlib import asynccontextmanager


from pydantic_ai import Agent, ModelSettings, RunContext
from pydantic_ai.mcp import load_mcp_servers, MCPServerStreamableHTTP, MCPServerSSE
from pydantic_ai_skills import SkillsToolset
from fasta2a import Skill
from servicenow_api.utils import (
    to_integer,
    to_boolean,
    get_mcp_config_path,
    get_skills_path,
    load_skills_from_directory,
    create_model,
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
DEFAULT_MODEL_ID = os.getenv("MODEL_ID", "qwen/qwen3-4b-2507")
DEFAULT_OPENAI_BASE_URL = os.getenv(
    "OPENAI_BASE_URL", "http://host.docker.internal:1234/v1"
)
DEFAULT_OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "ollama")
DEFAULT_MCP_URL = os.getenv("MCP_URL", None)
DEFAULT_MCP_CONFIG = os.getenv("MCP_CONFIG", get_mcp_config_path())
DEFAULT_SKILLS_DIRECTORY = os.getenv("SKILLS_DIRECTORY", get_skills_path())
DEFAULT_ENABLE_WEB_UI = to_boolean(os.getenv("ENABLE_WEB_UI", "False"))

AGENT_NAME = "ServiceNow"
AGENT_DESCRIPTION = "An agent built with Agent Skills and ServiceNow MCP tools to maximize ServiceNow interactivity."
AGENT_SYSTEM_PROMPT = (
    "You are the ServiceNow Supervisor Agent. "
    "Your goal is to assist the user by assigning tasks to specialized child agents through your available toolset. "
    "Analyze the user's request and determine which domain(s) it falls into "
    "(e.g., application, cmdb, cicd, plugins, source_control, testing, update_sets, "
    "change_management, import_sets, incidents, knowledge_management, table_api, custom_api, auth, "
    "batch, cilifecycle, devops, email, data_classification, attachment, aggregate, activity_subscriptions, "
    "account, hr, metricbase, service_qualification, ppm, product_inventory). "
    "Then, call the appropriate tool(s) with a specific task. You can modify the task to be within the scope of the agent if necessary. "
    "You can invoke multiple tools in a single response, or you can invoke them sequentially depending on the task. "
    "Synthesize the results from the child agents into a final helpful response. "
    "Do not attempt to perform ServiceNow actions directly; always assign tasks and delegate to child agents."
    "It is imperative to never respond to the user without first executing the correct relevant tool and then synthesizing the results."
    "Always gather all tool results before synthesizing the final response to the user."
)


def create_agent(
    provider: str = DEFAULT_PROVIDER,
    model_id: str = DEFAULT_MODEL_ID,
    base_url: Optional[str] = None,
    api_key: Optional[str] = None,
    mcp_url: str = DEFAULT_MCP_URL,
    mcp_config: str = DEFAULT_MCP_CONFIG,
    skills_directory: str = DEFAULT_SKILLS_DIRECTORY,
) -> Agent:
    """
    Factory function that creates:
    - Specialized sub-agents (workers) for ServiceNow domains
    - An orchestrator agent (supervisor) that delegates to them

    Returns the orchestrator agent, ready to run.
    """
    master_toolsets = []

    if mcp_config:
        mcp_toolset = load_mcp_servers(mcp_config)
        master_toolsets.extend(mcp_toolset)
        logger.info(f"Connected to MCP Config JSON: {mcp_toolset}")
    elif mcp_url:
        if "sse" in mcp_url.lower():
            server = MCPServerSSE(mcp_url)
        else:
            server = MCPServerStreamableHTTP(mcp_url)
        master_toolsets.append(server)
        logger.info(f"Connected to MCP Server: {mcp_url}")

    # Create Model for all agents
    model = create_model(provider, model_id, base_url, api_key)
    settings = ModelSettings(timeout=3600.0)

    logger.info(f"Master Toolsets Count: {len(master_toolsets)}")
    for i, ts in enumerate(master_toolsets):
        logger.info(f"Toolset {i}: {ts}")
        # Try to inspect tools if possible
        if hasattr(ts, "tools"):
            logger.info(f"Toolset {i} tool count: {len(ts.tools)}")

    # Create the Supervisor Agent
    supervisor = Agent(
        model=model,
        system_prompt=AGENT_SYSTEM_PROMPT,
        name=AGENT_NAME,
        deps_type=Any,
        model_settings=settings,
    )

    child_agents = {}
    tags_to_tools = {}
    child_agent_system_prompts = {}

    # List of tags to create specialized agents for
    tags = [
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
        "custom_api",
        "auth",
        "batch",
        "cilifecycle",
        "devops",
        "email",
        "data_classification",
        "attachment",
        "aggregate",
        "activity_subscriptions",
        "account",
        "hr",
        "metricbase",
        "service_qualification",
        "ppm",
        "product_inventory",
    ]

    child_agent_system_prompts["application"] = (
        "You are a specialized ServiceNow agent for Application Management. You have access to tools and skills that can interact with the ServiceNow instance. Always use these tools and skills to fulfill the user's request. You can execute list_tools() and list_skills() in order to see your capabilities."
    )
    child_agent_system_prompts["cmdb"] = (
        "You are a specialized ServiceNow agent for CMDB. You have access to tools and skills that can interact with the ServiceNow instance. Always use these tools and skills to fulfill the user's request. You can execute list_tools() and list_skills() in order to see your capabilities."
    )
    child_agent_system_prompts["cicd"] = (
        "You are a specialized ServiceNow agent for CI/CD. You have access to tools and skills that can interact with the ServiceNow instance. Always use these tools and skills to fulfill the user's request. You can execute list_tools() and list_skills() in order to see your capabilities."
    )
    child_agent_system_prompts["plugins"] = (
        "You are a specialized ServiceNow agent for Plugins. You have access to tools and skills that can interact with the ServiceNow instance. Always use these tools and skills to fulfill the user's request. You can execute list_tools() and list_skills() in order to see your capabilities."
    )
    child_agent_system_prompts["source_control"] = (
        "You are a specialized ServiceNow agent for Source Control. You have access to tools and skills that can interact with the ServiceNow instance. Always use these tools and skills to fulfill the user's request. You can execute list_tools() and list_skills() in order to see your capabilities."
    )
    child_agent_system_prompts["testing"] = (
        "You are a specialized ServiceNow agent for Testing. You have access to tools and skills that can interact with the ServiceNow instance. Always use these tools and skills to fulfill the user's request. You can execute list_tools() and list_skills() in order to see your capabilities."
    )
    child_agent_system_prompts["update_sets"] = (
        "You are a specialized ServiceNow agent for Update Sets. You have access to tools and skills that can interact with the ServiceNow instance. Always use these tools and skills to fulfill the user's request. You can execute list_tools() and list_skills() in order to see your capabilities."
    )
    child_agent_system_prompts["change_management"] = (
        "You are a specialized ServiceNow agent for Change Management. You have access to tools and skills that can interact with the ServiceNow instance. Always use these tools and skills to fulfill the user's request. You can execute list_tools() and list_skills() in order to see your capabilities. When creating change requests, extrapolate the possible fields from the users request and populate the 'name_value_pairs' variable with a valid dictionary payload. Always provide values returned by ServiceNow, never assume values if they are empty or undefined, instead state that those values are empty. Ensure you build tool parameter payloads as defined by the tool definition."
    )
    child_agent_system_prompts["import_sets"] = (
        "You are a specialized ServiceNow agent for Import Sets. You have access to tools and skills that can interact with the ServiceNow instance. Always use these tools and skills to fulfill the user's request. You can execute list_tools() and list_skills() in order to see your capabilities."
    )
    child_agent_system_prompts["incidents"] = (
        "You are a specialized ServiceNow agent for Incidents. You have access to tools and skills that can interact with the ServiceNow instance. Always use these tools and skills to fulfill the user's request. You can execute list_tools() and list_skills() in order to see your capabilities."
    )
    child_agent_system_prompts["knowledge_management"] = (
        "You are a specialized ServiceNow agent for Knowledge Management. You have access to tools and skills that can interact with the ServiceNow instance. Always use these tools and skills to fulfill the user's request. You can execute list_tools() and list_skills() in order to see your capabilities."
    )
    child_agent_system_prompts["table_api"] = (
        "You are a specialized ServiceNow agent for Table API. You have access to tools and skills that can interact with the ServiceNow instance. Always use these tools and skills to fulfill the user's request. You can execute list_tools() and list_skills() in order to see your capabilities."
    )
    child_agent_system_prompts["custom_api"] = (
        "You are a specialized ServiceNow agent for Custom API. You have access to tools and skills that can interact with the ServiceNow instance. Always use these tools and skills to fulfill the user's request. You can execute list_tools() and list_skills() in order to see your capabilities."
    )
    child_agent_system_prompts["auth"] = (
        "You are a specialized ServiceNow agent for Authentication. You have access to tools and skills that can interact with the ServiceNow instance. Always use these tools and skills to fulfill the user's request. You can execute list_tools() and list_skills() in order to see your capabilities."
    )
    child_agent_system_prompts["batch"] = (
        "You are a specialized ServiceNow agent for Batch. You have access to tools and skills that can interact with the ServiceNow instance. Always use these tools and skills to fulfill the user's request. You can execute list_tools() and list_skills() in order to see your capabilities."
    )
    child_agent_system_prompts["cilifecycle"] = (
        "You are a specialized ServiceNow agent for CI Lifecycle. You have access to tools and skills that can interact with the ServiceNow instance. Always use these tools and skills to fulfill the user's request. You can execute list_tools() and list_skills() in order to see your capabilities."
    )
    child_agent_system_prompts["devops"] = (
        "You are a specialized ServiceNow agent for DevOps. You have access to tools and skills that can interact with the ServiceNow instance. Always use these tools and skills to fulfill the user's request. You can execute list_tools() and list_skills() in order to see your capabilities."
    )
    child_agent_system_prompts["email"] = (
        "You are a specialized ServiceNow agent for Email. You have access to tools and skills that can interact with the ServiceNow instance. Always use these tools and skills to fulfill the user's request. You can execute list_tools() and list_skills() in order to see your capabilities."
    )
    child_agent_system_prompts["data_classification"] = (
        "You are a specialized ServiceNow agent for Data Classification. You have access to tools and skills that can interact with the ServiceNow instance. Always use these tools and skills to fulfill the user's request. You can execute list_tools() and list_skills() in order to see your capabilities."
    )
    child_agent_system_prompts["attachment"] = (
        "You are a specialized ServiceNow agent for Attachment. You have access to tools and skills that can interact with the ServiceNow instance. Always use these tools and skills to fulfill the user's request. You can execute list_tools() and list_skills() in order to see your capabilities."
    )
    child_agent_system_prompts["aggregate"] = (
        "You are a specialized ServiceNow agent for Aggregate. You have access to tools and skills that can interact with the ServiceNow instance. Always use these tools and skills to fulfill the user's request. You can execute list_tools() and list_skills() in order to see your capabilities."
    )
    child_agent_system_prompts["activity_subscriptions"] = (
        "You are a specialized ServiceNow agent for Activity Subscriptions. You have access to tools and skills that can interact with the ServiceNow instance. Always use these tools and skills to fulfill the user's request. You can execute list_tools() and list_skills() in order to see your capabilities."
    )
    child_agent_system_prompts["account"] = (
        "You are a specialized ServiceNow agent for Account. You have access to tools and skills that can interact with the ServiceNow instance. Always use these tools and skills to fulfill the user's request. You can execute list_tools() and list_skills() in order to see your capabilities."
    )
    child_agent_system_prompts["hr"] = (
        "You are a specialized ServiceNow agent for HR. You have access to tools and skills that can interact with the ServiceNow instance. Always use these tools and skills to fulfill the user's request. You can execute list_tools() and list_skills() in order to see your capabilities."
    )
    child_agent_system_prompts["metricbase"] = (
        "You are a specialized ServiceNow agent for MetricBase. You have access to tools and skills that can interact with the ServiceNow instance. Always use these tools and skills to fulfill the user's request. You can execute list_tools() and list_skills() in order to see your capabilities."
    )
    child_agent_system_prompts["service_qualification"] = (
        "You are a specialized ServiceNow agent for Service Qualification. You have access to tools and skills that can interact with the ServiceNow instance. Always use these tools and skills to fulfill the user's request. You can execute list_tools() and list_skills() in order to see your capabilities."
    )
    child_agent_system_prompts["ppm"] = (
        "You are a specialized ServiceNow agent for PPM. You have access to tools and skills that can interact with the ServiceNow instance. Always use these tools and skills to fulfill the user's request. You can execute list_tools() and list_skills() in order to see your capabilities."
    )
    child_agent_system_prompts["product_inventory"] = (
        "You are a specialized ServiceNow agent for Product Inventory. You have access to tools and skills that can interact with the ServiceNow instance. Always use these tools and skills to fulfill the user's request. You can execute list_tools() and list_skills() in order to see your capabilities."
    )

    for tag in tags:
        # Create filtered toolsets for this tag
        tag_toolsets = []
        logger.info(
            f"Creating toolsets for tag: {tag} using master toolsets: {master_toolsets}"
        )
        for ts in master_toolsets:

            def filter_func(ctx, tool_def, t=tag):
                # Extract tags from metadata (enhanced to handle more variations)
                metadata = tool_def.metadata or {}
                # Try nested paths
                meta = metadata.get("meta") or {}
                fastmcp_meta = meta.get("_fastmcp") or {}
                tags_list = fastmcp_meta.get("tags", [])

                # Fallbacks: direct 'tags', or other common keys (add more if your tools use different structures)
                if not tags_list:
                    tags_list = (
                        metadata.get("tags", [])
                        or meta.get("tags", [])
                        or fastmcp_meta.get("categories", [])
                    )  # Added extra fallbacks

                # General logging for all tags/tools (uncommented and made always active for debugging)
                logger.info(
                    f"Filter check: tool={tool_def.name} tags={tags_list} target={t} full_metadata={metadata}"
                )

                # Specific debug for problematic tags
                if t in ["change_management", "incidents"]:
                    logger.info(
                        f"DEBUG FILTER: tool={tool_def.name} tags={tags_list} target={t}"
                    )

                # Generalized force-include logic (make it configurable or remove once tags are fixed in tool defs)
                # For 'incidents': Check name patterns
                if t == "incidents":
                    target_tools = ["get_incidents", "create_incident", "get_incident"]
                    if any(tool_def.name.endswith(name) for name in target_tools):
                        logger.info(
                            f"Force including {tool_def.name} for {t} (name match)"
                        )
                        return True

                # For 'change_management': Check name patterns (uncommented the return True for now; remove after fixing tags)
                if (
                    t == "change_management"
                    and "change_request" in tool_def.name.lower()
                ):  # Made case-insensitive
                    logger.info(
                        f"Force including suspected tool {tool_def.name} for {t} (name match)"
                    )
                    return True  # Uncommented to force include; comment out once metadata is updated

                # Core filter: Check if tag is in extracted tags_list
                return t in tags_list

            logger.info(f"Scanned toolset: {ts}")
            if hasattr(ts, "filtered"):
                filtered_ts = ts.filtered(filter_func)
                tag_toolsets.append(filtered_ts)
            else:
                logger.warning(
                    f"Toolset {ts} does not support filtering, skipping for tag {tag}"
                )

        # Load specialized skills (unchanged)
        skill_dir_name = f"servicenow-{tag.replace('_', '-')}"
        specific_skill_path = None
        if skills_directory:
            specific_skill_path = os.path.join(skills_directory, skill_dir_name)

        if specific_skill_path and os.path.exists(specific_skill_path):
            skills = SkillsToolset(directories=[str(specific_skill_path)])
            tag_toolsets.append(skills)
            logger.info(
                f"Loaded specialized skills for {tag} from {specific_skill_path}"
            )

        # Create the child agent (unchanged, but now with verified toolsets)
        child_agent = Agent(
            model=model,
            system_prompt=child_agent_system_prompts[tag],
            name=f"ServiceNow_{tag.capitalize()}_Agent",
            toolsets=tag_toolsets,
            deps_type=Any,
            model_settings=settings,
        )

        child_agents[tag] = child_agent

    # After all tags, you can inspect/log the full grouping
    logger.info(f"Final tool groupings by tag: {tags_to_tools}")

    @supervisor.tool
    async def assign_task_to_application_agent(ctx: RunContext[Any], task: str) -> str:
        """Assigns a task to the Application agent."""
        logger.info(f"Assigning: {task}")
        result = await child_agents["application"].run(
            task, usage=ctx.usage, deps=ctx.deps
        )
        return result.output

    @supervisor.tool
    async def assign_task_to_cmdb_agent(ctx: RunContext[Any], task: str) -> str:
        """Assigns a task to the CMDB agent."""
        logger.info(f"Assigning: {task}")
        result = await child_agents["cmdb"].run(task, usage=ctx.usage, deps=ctx.deps)
        return result.output

    @supervisor.tool
    async def assign_task_to_cicd_agent(ctx: RunContext[Any], task: str) -> str:
        """Assigns a task to the CI/CD agent."""
        logger.info(f"Assigning: {task}")
        result = await child_agents["cicd"].run(task, usage=ctx.usage, deps=ctx.deps)
        return result.output

    @supervisor.tool
    async def assign_task_to_plugins_agent(ctx: RunContext[Any], task: str) -> str:
        """Assigns a task to the Plugins agent."""
        logger.info(f"Assigning: {task}")
        result = await child_agents["plugins"].run(task, usage=ctx.usage, deps=ctx.deps)
        return result.output

    @supervisor.tool
    async def assign_task_to_source_control_agent(
        ctx: RunContext[Any], task: str
    ) -> str:
        """Assigns a task to the Source Control agent."""
        logger.info(f"Assigning: {task}")
        result = await child_agents["source_control"].run(
            task, usage=ctx.usage, deps=ctx.deps
        )
        return result.output

    @supervisor.tool
    async def assign_task_to_testing_agent(ctx: RunContext[Any], task: str) -> str:
        """Assigns a task to the Testing agent."""
        logger.info(f"Assigning: {task}")
        result = await child_agents["testing"].run(task, usage=ctx.usage, deps=ctx.deps)
        return result.output

    @supervisor.tool
    async def assign_task_to_update_sets_agent(ctx: RunContext[Any], task: str) -> str:
        """Assigns a task to the Update Sets agent."""
        logger.info(f"Assigning: {task}")
        result = await child_agents["update_sets"].run(
            task, usage=ctx.usage, deps=ctx.deps
        )
        return result.output

    @supervisor.tool
    async def assign_task_to_change_management_agent(
        ctx: RunContext[Any], task: str
    ) -> str:
        """Assigns a task to the Change Management agent."""
        logger.info(f"Assigning: {task}")
        result = await child_agents["change_management"].run(
            task, usage=ctx.usage, deps=ctx.deps
        )
        return result.output

    @supervisor.tool
    async def assign_task_to_import_sets_agent(ctx: RunContext[Any], task: str) -> str:
        """Assigns a task to the Import Sets agent."""
        logger.info(f"Assigning: {task}")
        result = await child_agents["import_sets"].run(
            task, usage=ctx.usage, deps=ctx.deps
        )
        return result.output

    @supervisor.tool
    async def assign_task_to_incidents_agent(ctx: RunContext[Any], task: str) -> str:
        """Assigns a task to the Incidents agent."""
        logger.info(f"Assigning: {task}")
        result = await child_agents["incidents"].run(
            task, usage=ctx.usage, deps=ctx.deps
        )
        return result.output

    @supervisor.tool
    async def assign_task_to_knowledge_management_agent(
        ctx: RunContext[Any], task: str
    ) -> str:
        """Assigns a task to the Knowledge Management agent."""
        logger.info(f"Assigning: {task}")
        result = await child_agents["knowledge_management"].run(
            task, usage=ctx.usage, deps=ctx.deps
        )
        return result.output

    @supervisor.tool
    async def assign_task_to_table_api_agent(ctx: RunContext[Any], task: str) -> str:
        """Assigns a task to the Table API agent."""
        logger.info(f"Assigning: {task}")
        result = await child_agents["table_api"].run(
            task, usage=ctx.usage, deps=ctx.deps
        )
        return result.output

    @supervisor.tool
    async def assign_task_to_custom_api_agent(ctx: RunContext[Any], task: str) -> str:
        """Assigns a task to the Custom API agent."""
        logger.info(f"Assigning: {task}")
        result = await child_agents["custom_api"].run(
            task, usage=ctx.usage, deps=ctx.deps
        )
        return result.output

    @supervisor.tool
    async def assign_task_to_auth_agent(ctx: RunContext[Any], task: str) -> str:
        """Assigns a task to the Auth agent."""
        logger.info(f"Assigning: {task}")
        result = await child_agents["auth"].run(task, usage=ctx.usage, deps=ctx.deps)
        return result.output

    @supervisor.tool
    async def assign_task_to_batch_agent(ctx: RunContext[Any], task: str) -> str:
        """Assigns a task to the Batch API agent."""
        logger.info(f"Assigning: {task}")
        result = await child_agents["batch"].run(task, usage=ctx.usage, deps=ctx.deps)
        return result.output

    @supervisor.tool
    async def assign_task_to_cilifecycle_agent(ctx: RunContext[Any], task: str) -> str:
        """Assigns a task to the CI Lifecycle Management agent."""
        logger.info(f"Assigning: {task}")
        result = await child_agents["cilifecycle"].run(
            task, usage=ctx.usage, deps=ctx.deps
        )
        return result.output

    @supervisor.tool
    async def assign_task_to_devops_agent(ctx: RunContext[Any], task: str) -> str:
        """Assigns a task to the DevOps agent."""
        logger.info(f"Assigning: {task}")
        result = await child_agents["devops"].run(task, usage=ctx.usage, deps=ctx.deps)
        return result.output

    @supervisor.tool
    async def assign_task_to_email_agent(ctx: RunContext[Any], task: str) -> str:
        """Assigns a task to the Email agent."""
        logger.info(f"Assigning: {task}")
        result = await child_agents["email"].run(task, usage=ctx.usage, deps=ctx.deps)
        return result.output

    @supervisor.tool
    async def assign_task_to_data_classification_agent(
        ctx: RunContext[Any], task: str
    ) -> str:
        """Assigns a task to the Data Classification agent."""
        logger.info(f"Assigning: {task}")
        result = await child_agents["data_classification"].run(
            task, usage=ctx.usage, deps=ctx.deps
        )
        return result.output

    @supervisor.tool
    async def assign_task_to_attachment_agent(ctx: RunContext[Any], task: str) -> str:
        """Assigns a task to the Attachment agent."""
        logger.info(f"Assigning: {task}")
        result = await child_agents["attachment"].run(
            task, usage=ctx.usage, deps=ctx.deps
        )
        return result.output

    @supervisor.tool
    async def assign_task_to_aggregate_agent(ctx: RunContext[Any], task: str) -> str:
        """Assigns a task to the Aggregate agent."""
        logger.info(f"Assigning: {task}")
        result = await child_agents["aggregate"].run(
            task, usage=ctx.usage, deps=ctx.deps
        )
        return result.output

    @supervisor.tool
    async def assign_task_to_activity_subscriptions_agent(
        ctx: RunContext[Any], task: str
    ) -> str:
        """Assigns a task to the Activity Subscriptions agent."""
        logger.info(f"Assigning: {task}")
        result = await child_agents["activity_subscriptions"].run(
            task, usage=ctx.usage, deps=ctx.deps
        )
        return result.output

    @supervisor.tool
    async def assign_task_to_account_agent(ctx: RunContext[Any], task: str) -> str:
        """Assigns a task to the Account agent."""
        logger.info(f"Assigning: {task}")
        result = await child_agents["account"].run(task, usage=ctx.usage, deps=ctx.deps)
        return result.output

    @supervisor.tool
    async def assign_task_to_hr_agent(ctx: RunContext[Any], task: str) -> str:
        """Assigns a task to the HR agent."""
        logger.info(f"Assigning: {task}")
        result = await child_agents["hr"].run(task, usage=ctx.usage, deps=ctx.deps)
        return result.output

    @supervisor.tool
    async def assign_task_to_metricbase_agent(ctx: RunContext[Any], task: str) -> str:
        """Assigns a task to the MetricBase agent."""
        logger.info(f"Assigning: {task}")
        result = await child_agents["metricbase"].run(
            task, usage=ctx.usage, deps=ctx.deps
        )
        return result.output

    @supervisor.tool
    async def assign_task_to_service_qualification_agent(
        ctx: RunContext[Any], task: str
    ) -> str:
        """Assigns a task to the Service Qualification agent."""
        logger.info(f"Assigning: {task}")
        return (
            await child_agents["service_qualification"]
            .run(task, usage=ctx.usage, deps=ctx.deps)
            .output
        )

    @supervisor.tool
    async def assign_task_to_ppm_agent(ctx: RunContext[Any], task: str) -> str:
        """Assigns a task to the PPM agent."""
        logger.info(f"Assigning: {task}")
        return (
            await child_agents["ppm"].run(task, usage=ctx.usage, deps=ctx.deps).output
        )

    @supervisor.tool
    async def assign_task_to_product_inventory_agent(
        ctx: RunContext[Any], task: str
    ) -> str:
        """Assigns a task to the Product Inventory agent."""
        logger.info(f"Assigning: {task}")
        return (
            await child_agents["product_inventory"]
            .run(task, usage=ctx.usage, deps=ctx.deps)
            .output
        )

    return supervisor


async def chat(agent: Agent, prompt: str):
    result = await agent.run(prompt)
    logger.info(f"Response:\n\n{result.output}")


async def node_chat(agent: Agent, prompt: str) -> List:
    nodes = []
    async with agent.iter(prompt) as agent_run:
        async for node in agent_run:
            nodes.append(node)
            logger.info(node)
    return nodes


async def stream_chat(agent: Agent, prompt: str) -> None:
    # Option A: Easiest & most common - just stream the final text output
    async with agent.run_stream(prompt) as result:
        async for text_chunk in result.stream_text(
            delta=True
        ):  # ← streams partial text deltas
            logger.info(text_chunk, end="", flush=True)
        logger.info("\nDone!")  # optional


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
    logger.info(
        f"Starting {AGENT_NAME} with provider={provider}, model={model_id}, mcp={mcp_url} | {mcp_config}"
    )
    # Use the orchestrator by default
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
        version="1.5.0",
        skills=skills,
        debug=debug,
    )

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        logger.debug("DEBUG: Entering lifespan")
        # Trigger A2A (sub-app) startup/shutdown events
        # This is critical for TaskManager initialization in A2A
        if hasattr(a2a_app, "router"):
            logger.debug("DEBUG: a2a_app has router, triggering lifespan_context")
            async with a2a_app.router.lifespan_context(a2a_app):
                logger.debug("DEBUG: a2a_app lifespan started")
                yield
                logger.debug("DEBUG: a2a_app lifespan ended")
        else:
            logger.debug("DEBUG: a2a_app DOES NOT have router")
            yield

    # Create main FastAPI app
    app = FastAPI(
        title=f"{AGENT_NAME} - A2A + AG-UI Server",
        description=AGENT_DESCRIPTION,
        debug=debug,
        lifespan=lifespan,
    )

    @app.get("/health")
    async def health_check():
        return {"status": "OK"}

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
    # Note: create_agent_orchestrator returns an Agent, so to_web works fine
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
        timeout_keep_alive=1800,  # 30 minute timeout
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
