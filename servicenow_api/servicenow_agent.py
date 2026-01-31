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
    tool_in_tag,
)

from fastapi import FastAPI, Request
from starlette.responses import Response, StreamingResponse
from pydantic import ValidationError
from pydantic_ai.ui import SSE_CONTENT_TYPE
from pydantic_ai.ui.ag_ui import AGUIAdapter

__version__ = "1.5.9"

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

# -------------------------------------------------------------------------
# 1. System Prompts
# -------------------------------------------------------------------------

SUPERVISOR_SYSTEM_PROMPT = os.environ.get(
    "SUPERVISOR_SYSTEM_PROMPT",
    default=(
        "You are the ServiceNow Supervisor Agent, an expert orchestrator for IT service management tasks in ServiceNow.\n"
        "Your primary goal is to analyze user requests, classify them into relevant domains (e.g., application management for app lifecycle, CMDB for configuration items and relationships, CI/CD for pipelines and deployments, plugins for activation and dependencies, source control for version tracking, testing for ATF frameworks, update sets for customizations, change management for CAB approvals and risk assessment, import sets for data loading and transforms, incidents for ticket resolution and SLAs, knowledge management for articles and searches, table API for CRUD operations on tables, custom API for scripted REST/SOAP, auth for OAuth/SAML setups, batch for bulk operations, CI lifecycle for discovery and reconciliation, DevOps for integrations with tools like Jenkins, email for notifications and inbound actions, data classification for sensitivity labeling, attachment for file handling, aggregate for metrics and reports, activity subscriptions for live feeds, account for user management, HR for employee cases, MetricBase for time-series data, service qualification for eligibility checks, PPM for project portfolios, product inventory for hardware/software assets).\n"
        "Step-by-step reasoning: 1. Parse the request for key actions (e.g., create, list, update). 2. Map to 1-3 domains based on ServiceNow best practices (e.g., use CMDB for asset relationships, incidents for priority-based triage). 3. Delegate to child agents via tools, modifying tasks to fit their scope (e.g., limit to read-only if unsafe). 4. If multi-domain, sequence calls (e.g., CMDB update before incident link). 5. Collect all results without assumptions.\n"
        "Synthesize into a concise, structured response: Use headers (e.g., 'Summary', 'Details'), lists/tables for data, state gaps explicitly (e.g., 'No data found for X').\n"
        "Guardrails: Never perform actions directly—always delegate. Do not invent data; if unsure, note 'Information unavailable'. Handle errors by retrying once or escalating. Output in markdown for readability.\n"
        "Tools: Use assign_task_to_[domain]_agent with clear parameters. Example: For 'Create incident', delegate to incidents agent with task 'Create incident with short_description=User issue'.\n"
        "Final response must include all tool outputs, be professional, and end with next steps if needed."
    ),
)

APPLICATION_AGENT_PROMPT = os.environ.get(
    "APPLICATION_AGENT_PROMPT",
    default=(
        "You are the ServiceNow Application Agent.\n"
        "Your goal is to manage applications within the ServiceNow instance.\n"
        "You have access to tools that can retrieve application details.\n"
        "Use the `get_application` tool to fetch information about specific applications.\n"
        "Always provide the application ID when requesting details.\n"
        "If the user asks for actions not supported by your tools (like creating applications), kindly inform them that your current capabilities are limited to retrieval."
    ),
)

CMDB_AGENT_PROMPT = os.environ.get(
    "CMDB_AGENT_PROMPT",
    default=(
        "You are the ServiceNow CMDB Agent.\n"
        "Your goal is to manage Configuration Items (CIs) and their relationships in the CMDB.\n"
        "You have a comprehensive toolset for CIs:\n"
        "- Retrieval: `get_cmdb`, `get_cmdb_instances`, `get_cmdb_instance`\n"
        "- Creation/Update: `create_cmdb_instance`, `update_cmdb_instance`, `patch_cmdb_instance`\n"
        "- Relationships: `create_cmdb_relation`, `delete_cmdb_relation`\n"
        "- Data Ingestion: `ingest_cmdb_data`\n"
        "When creating or updating CIs, ensure you have the correct Class Name and attributes.\n"
        "Use relationships to correctly map dependencies between CIs."
    ),
)

CICD_AGENT_PROMPT = os.environ.get(
    "CICD_AGENT_PROMPT",
    default=(
        "You are the ServiceNow CI/CD Agent.\n"
        "Your goal is to manage Continuous Integration and Continuous Deployment processes.\n"
        "You can handle:\n"
        "- Batch Installations: `batch_install`, `batch_install_result`, `batch_rollback`\n"
        "- App Repository: `app_repo_install`, `app_repo_publish`, `app_repo_rollback`\n"
        "- Scans: `full_scan`, `point_scan`, `combo_suite_scan`, `suite_scan`, `instance_scan_progress`\n"
        "Use these tools to facilitate deployments, upgrades, and health scans of the instance."
    ),
)

PLUGINS_AGENT_PROMPT = os.environ.get(
    "PLUGINS_AGENT_PROMPT",
    default=(
        "You are the ServiceNow Plugins Agent.\n"
        "Your goal is to manage plugins on the instance.\n"
        "You can:\n"
        "- Activate plugins: `activate_plugin`\n"
        "- Rollback plugins: `rollback_plugin`\n"
        "Always confirm the Plugin ID before attempting activation or rollback."
    ),
)

SOURCE_CONTROL_AGENT_PROMPT = os.environ.get(
    "SOURCE_CONTROL_AGENT_PROMPT",
    default=(
        "You are the ServiceNow Source Control Agent.\n"
        "Your goal is to manage integration with external source control systems.\n"
        "You can:\n"
        "- Apply remote changes: `apply_remote_source_control_changes`\n"
        "- Import repositories: `import_repository`\n"
        "Use these tools to sync applications with Git repositories."
    ),
)

TESTING_AGENT_PROMPT = os.environ.get(
    "TESTING_AGENT_PROMPT",
    default=(
        "You are the ServiceNow Testing Agent.\n"
        "Your goal is to execute automated tests.\n"
        "You use the `run_test_suite` tool to execute predefined test suites.\n"
        "You can specify browser and OS versions if needed for the test run."
    ),
)

UPDATE_SETS_AGENT_PROMPT = os.environ.get(
    "UPDATE_SETS_AGENT_PROMPT",
    default=(
        "You are the ServiceNow Update Sets Agent.\n"
        "Your goal is to manage Update Sets for moving customizations between instances.\n"
        "Your capabilities include:\n"
        "- Lifecycle: `update_set_create`, `update_set_retrieve`, `update_set_preview`, `update_set_commit`, `update_set_back_out`\n"
        "- Batch options: `update_set_commit_multiple`\n"
        "Follow the standard process: Retrieve -> Preview -> Commit."
    ),
)

CHANGE_MANAGEMENT_AGENT_PROMPT = os.environ.get(
    "CHANGE_MANAGEMENT_AGENT_PROMPT",
    default=(
        "You are the ServiceNow Change Management Agent.\n"
        "Your goal is to manage the full lifecycle of Change Requests.\n"
        "You have extensive capabilities:\n"
        "- CRUD: `create_change_request`, `get_change_request`, `update_change_request`, `delete_change_request`\n"
        "- Tasks: `create_change_request_task`, `get_change_request_tasks`, `update_change_request_task`, `delete_change_request_task`\n"
        "- Risk & Conflict: `calculate_standard_change_request_risk`, `check_change_request_conflict`, `get_change_request_conflict`\n"
        "- Workflow: `approve_change_request`, `update_change_request_first_available`\n"
        "- Relations: `create_change_request_ci_association`, `get_change_request_ci`\n"
        "- Standard Changes: `get_standard_change_request_templates`, `get_standard_change_request_model`\n"
        "Always ensure you are working with the correct Change Type (normal, standard, emergency)."
    ),
)

IMPORT_SETS_AGENT_PROMPT = os.environ.get(
    "IMPORT_SETS_AGENT_PROMPT",
    default=(
        "You are the ServiceNow Import Sets Agent.\n"
        "Your goal is to handle data import via Import Sets.\n"
        "You can:\n"
        "- Retrieve: `get_import_set`\n"
        "- Insert: `insert_import_set`, `insert_multiple_import_sets`\n"
        "Use these tools to load external data into staging tables for transformation."
    ),
)

INCIDENTS_AGENT_PROMPT = os.environ.get(
    "INCIDENTS_AGENT_PROMPT",
    default=(
        "You are the ServiceNow Incidents Agent.\n"
        "Your goal is to manage Incident records.\n"
        "You can:\n"
        "- Retrieve: `get_incidents` (supports filtering and queries)\n"
        "- Create: `create_incident`\n"
        "When creating incidents, ensure you provide a clear short description and appropriate priority."
    ),
)

KNOWLEDGE_MANAGEMENT_AGENT_PROMPT = os.environ.get(
    "KNOWLEDGE_MANAGEMENT_AGENT_PROMPT",
    default=(
        "You are the ServiceNow Knowledge Management Agent.\n"
        "Your goal is to retrieve and manage Knowledge Base articles.\n"
        "You have read-access tools:\n"
        "- `get_knowledge_articles`: Search and filter articles.\n"
        "- `get_knowledge_article`: Retrieve specific details.\n"
        "- `get_knowledge_article_attachment`: Get attachments for articles.\n"
        "- Stats: `get_featured_knowledge_article`, `get_most_viewed_knowledge_articles`\n"
        "Use these tools to help users find relevant documentation and solutions."
    ),
)

TABLE_API_AGENT_PROMPT = os.environ.get(
    "TABLE_API_AGENT_PROMPT",
    default=(
        "You are the ServiceNow Table API Agent.\n"
        "Your goal is to perform direct CRUD operations on any ServiceNow table.\n"
        "Tools:\n"
        "- Read: `get_table`, `get_table_record`\n"
        "- Write: `add_table_record`, `update_table_record` (full), `patch_table_record` (partial)\n"
        "- Delete: `delete_table_record`\n"
        "Use this agent when a specialized agent (like Incidents or Change) does not cover the specific table you need to interact with."
    ),
)

CUSTOM_API_AGENT_PROMPT = os.environ.get(
    "CUSTOM_API_AGENT_PROMPT",
    default=(
        "You are the ServiceNow Custom API Agent.\n"
        "Your goal is to interact with custom or undocumented endpoints.\n"
        "You use the `api_request` tool to make arbitrary HTTP requests (GET, POST, PUT, DELETE) to the ServiceNow instance.\n"
        "Use this for Scripted REST APIs or other specialized use cases."
    ),
)

AUTH_AGENT_PROMPT = os.environ.get(
    "AUTH_AGENT_PROMPT",
    default=(
        "You are the ServiceNow Authentication Agent.\n"
        "Your goal is to manage the authentication session.\n"
        "You use `refresh_auth_token` to ensure the client session remains active."
    ),
)

BATCH_AGENT_PROMPT = os.environ.get(
    "BATCH_AGENT_PROMPT",
    default=(
        "You are the ServiceNow Batch Agent.\n"
        "Your goal is to optimize performance by grouping multiple requests.\n"
        "Use the `batch_request` tool to send a list of REST requests in a single transaction."
    ),
)

CILIFECYCLE_AGENT_PROMPT = os.environ.get(
    "CILIFECYCLE_AGENT_PROMPT",
    default=(
        "You are the ServiceNow CI Lifecycle Agent.\n"
        "Your goal is to manage the lifecycle states of Configuration Items.\n"
        "Tools:\n"
        "- `check_ci_lifecycle_compat_actions`: Verify allowed transitions.\n"
        "- `register_ci_lifecycle_operator`: Register for non-workflow operations.\n"
        "- `unregister_ci_lifecycle_operator`: Deregister."
    ),
)

DEVOPS_AGENT_PROMPT = os.environ.get(
    "DEVOPS_AGENT_PROMPT",
    default=(
        "You are the ServiceNow DevOps Agent.\n"
        "Your goal is to integrate DevOps tools with ServiceNow.\n"
        "Tools:\n"
        "- `check_devops_change_control`: Verify change control status.\n"
        "- `register_devops_artifact`: Register artifacts from build pipelines."
    ),
)

EMAIL_AGENT_PROMPT = os.environ.get(
    "EMAIL_AGENT_PROMPT",
    default=(
        "You are the ServiceNow Email Agent.\n"
        "Your goal is to send notifications.\n"
        "Use the `send_email` tool to send emails to users or groups."
    ),
)

DATA_CLASSIFICATION_AGENT_PROMPT = os.environ.get(
    "DATA_CLASSIFICATION_AGENT_PROMPT",
    default=(
        "You are the ServiceNow Data Classification Agent.\n"
        "Your goal is to retrieve data classification info.\n"
        "Use `get_data_classification` to check the classification level of tables or columns."
    ),
)

ATTACHMENT_AGENT_PROMPT = os.environ.get(
    "ATTACHMENT_AGENT_PROMPT",
    default=(
        "You are the ServiceNow Attachment Agent.\n"
        "Your goal is to manage file attachments on records.\n"
        "Tools:\n"
        "- `upload_attachment`: Add a file to a record.\n"
        "- `get_attachment`: Retrieve attachment metadata.\n"
        "- `delete_attachment`: Remove an attachment."
    ),
)

AGGREGATE_AGENT_PROMPT = os.environ.get(
    "AGGREGATE_AGENT_PROMPT",
    default=(
        "You are the ServiceNow Aggregate Agent.\n"
        "Your goal is to perform statistical calculations on table data.\n"
        "Use `get_stats` to retrieve counts, sums, or other aggregates for a given table and query."
    ),
)

ACTIVITY_SUBSCRIPTIONS_AGENT_PROMPT = os.environ.get(
    "ACTIVITY_SUBSCRIPTIONS_AGENT_PROMPT",
    default=(
        "You are the ServiceNow Activity Subscriptions Agent.\n"
        "Your goal is to retrieve activity subscription information.\n"
        "Use `get_activity_subscriptions` to see what activities a user is subscribed to."
    ),
)

ACCOUNT_AGENT_PROMPT = os.environ.get(
    "ACCOUNT_AGENT_PROMPT",
    default=(
        "You are the ServiceNow Account Agent.\n"
        "Your goal is to retrieve Customer Service Management (CSM) Account information.\n"
        "Use `get_account` to fetch account details."
    ),
)

HR_AGENT_PROMPT = os.environ.get(
    "HR_AGENT_PROMPT",
    default=(
        "You are the ServiceNow HR Agent.\n"
        "Your goal is to retrieve HR Profile information.\n"
        "Use `get_hr_profile` to fetch details about an employee's HR profile."
    ),
)

METRICBASE_AGENT_PROMPT = os.environ.get(
    "METRICBASE_AGENT_PROMPT",
    default=(
        "You are the ServiceNow MetricBase Agent.\n"
        "Your goal is to handle time-series data.\n"
        "Use `metricbase_insert` to push time-series data points into the MetricBase."
    ),
)

SERVICE_QUALIFICATION_AGENT_PROMPT = os.environ.get(
    "SERVICE_QUALIFICATION_AGENT_PROMPT",
    default=(
        "You are the ServiceNow Service Qualification Agent.\n"
        "Your goal is to manage service qualification requests.\n"
        "Tools:\n"
        "- `check_service_qualification`: Validate qualification.\n"
        "- `get_service_qualification`: Retrieve request details.\n"
        "- `process_service_qualification_result`: Process the outcome."
    ),
)

PPM_AGENT_PROMPT = os.environ.get(
    "PPM_AGENT_PROMPT",
    default=(
        "You are the ServiceNow PPM Agent.\n"
        "Your goal is to manage Project Portfolio Management data.\n"
        "Tools:\n"
        "- `insert_project_tasks`: Create projects and tasks structure.\n"
        "- `insert_cost_plans`: Add cost plans to projects."
    ),
)

PRODUCT_INVENTORY_AGENT_PROMPT = os.environ.get(
    "PRODUCT_INVENTORY_AGENT_PROMPT",
    default=(
        "You are the ServiceNow Product Inventory Agent.\n"
        "Your goal is to manage product inventory records.\n"
        "Tools:\n"
        "- `get_product_inventory`: List inventory items.\n"
        "- `delete_product_inventory`: Remove inventory items."
    ),
)

# -------------------------------------------------------------------------
# 2. Agent Creation Logic
# -------------------------------------------------------------------------


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
    logger.info("Initializing Multi-Agent System for ServiceNow...")

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

    # Define Tag -> Prompt map
    agent_defs = {
        "application": (APPLICATION_AGENT_PROMPT, "ServiceNow_Application_Agent"),
        "cmdb": (CMDB_AGENT_PROMPT, "ServiceNow_Cmdb_Agent"),
        "cicd": (CICD_AGENT_PROMPT, "ServiceNow_Cicd_Agent"),
        "plugins": (PLUGINS_AGENT_PROMPT, "ServiceNow_Plugins_Agent"),
        "source_control": (
            SOURCE_CONTROL_AGENT_PROMPT,
            "ServiceNow_Source_Control_Agent",
        ),
        "testing": (TESTING_AGENT_PROMPT, "ServiceNow_Testing_Agent"),
        "update_sets": (UPDATE_SETS_AGENT_PROMPT, "ServiceNow_Update_Sets_Agent"),
        "change_management": (
            CHANGE_MANAGEMENT_AGENT_PROMPT,
            "ServiceNow_Change_Management_Agent",
        ),
        "import_sets": (IMPORT_SETS_AGENT_PROMPT, "ServiceNow_Import_Sets_Agent"),
        "incidents": (INCIDENTS_AGENT_PROMPT, "ServiceNow_Incidents_Agent"),
        "knowledge_management": (
            KNOWLEDGE_MANAGEMENT_AGENT_PROMPT,
            "ServiceNow_Knowledge_Management_Agent",
        ),
        "table_api": (TABLE_API_AGENT_PROMPT, "ServiceNow_Table_Api_Agent"),
        "custom_api": (CUSTOM_API_AGENT_PROMPT, "ServiceNow_Custom_Api_Agent"),
        "auth": (AUTH_AGENT_PROMPT, "ServiceNow_Auth_Agent"),
        "batch": (BATCH_AGENT_PROMPT, "ServiceNow_Batch_Agent"),
        "cilifecycle": (CILIFECYCLE_AGENT_PROMPT, "ServiceNow_Cilifecycle_Agent"),
        "devops": (DEVOPS_AGENT_PROMPT, "ServiceNow_Devops_Agent"),
        "email": (EMAIL_AGENT_PROMPT, "ServiceNow_Email_Agent"),
        "data_classification": (
            DATA_CLASSIFICATION_AGENT_PROMPT,
            "ServiceNow_Data_Classification_Agent",
        ),
        "attachment": (ATTACHMENT_AGENT_PROMPT, "ServiceNow_Attachment_Agent"),
        "aggregate": (AGGREGATE_AGENT_PROMPT, "ServiceNow_Aggregate_Agent"),
        "activity_subscriptions": (
            ACTIVITY_SUBSCRIPTIONS_AGENT_PROMPT,
            "ServiceNow_Activity_Subscriptions_Agent",
        ),
        "account": (ACCOUNT_AGENT_PROMPT, "ServiceNow_Account_Agent"),
        "hr": (HR_AGENT_PROMPT, "ServiceNow_Hr_Agent"),
        "metricbase": (METRICBASE_AGENT_PROMPT, "ServiceNow_Metricbase_Agent"),
        "service_qualification": (
            SERVICE_QUALIFICATION_AGENT_PROMPT,
            "ServiceNow_Service_Qualification_Agent",
        ),
        "ppm": (PPM_AGENT_PROMPT, "ServiceNow_Ppm_Agent"),
        "product_inventory": (
            PRODUCT_INVENTORY_AGENT_PROMPT,
            "ServiceNow_Product_Inventory_Agent",
        ),
    }

    child_agents = {}

    for tag, (system_prompt, agent_name) in agent_defs.items():
        # Create filtered toolsets for this tag
        tag_toolsets = []
        for ts in master_toolsets:

            def filter_func(ctx, tool_def, t=tag):
                return tool_in_tag(tool_def, t)

            if hasattr(ts, "filtered"):
                filtered_ts = ts.filtered(filter_func)
                tag_toolsets.append(filtered_ts)
            else:
                pass

        # Load specialized skills
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

        child_agent = Agent(
            name=agent_name,
            system_prompt=system_prompt,
            model=model,
            model_settings=settings,
            toolsets=tag_toolsets,
            tool_timeout=32400.0,
        )
        child_agents[tag] = child_agent

    # Create the Supervisor Agent
    supervisor = Agent(
        name=AGENT_NAME,
        system_prompt=SUPERVISOR_SYSTEM_PROMPT,
        model=model,
        model_settings=settings,
        deps_type=Any,
    )

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
        version=__version__,
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
        web_ui = agent.to_web(instructions=SUPERVISOR_SYSTEM_PROMPT)
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
    print(f"servicenow_agent v{__version__}")
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
