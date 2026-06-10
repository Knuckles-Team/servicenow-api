import warnings

from fastmcp import Context, FastMCP
from fastmcp.dependencies import Depends
from fastmcp.utilities.logging import get_logger
from pydantic import Field

with warnings.catch_warnings():
    warnings.simplefilter("ignore")
    try:
        from requests.exceptions import RequestsDependencyWarning

        warnings.filterwarnings("ignore", category=RequestsDependencyWarning)
    except ImportError:
        pass
warnings.filterwarnings("ignore", message=".*urllib3.*or chardet.*")
warnings.filterwarnings("ignore", message=".*urllib3.*or charset_normalizer.*")
import asyncio
import json
import logging
import os
import sys
from threading import local
from typing import Any

import httpx
from agent_utilities.base_utilities import to_boolean
from agent_utilities.mcp_utilities import (
    config,
    create_mcp_server,
)
from dotenv import find_dotenv, load_dotenv

from servicenow_api.auth import get_client

__version__ = "1.34.0"
logger = get_logger(name="ServicenowMCP")
logger.setLevel(logging.DEBUG)
DEFAULT_SERVICENOW_USERNAME = os.getenv("SERVICENOW_USERNAME", None)
DEFAULT_SERVICENOW_PASSWORD = os.getenv("SERVICENOW_PASSWORD", None)
DEFAULT_SERVICENOW_CLIENT_ID = os.getenv("SERVICENOW_CLIENT_ID", None)
DEFAULT_SERVICENOW_CLIENT_SECRET = os.getenv("SERVICENOW_CLIENT_SECRET", None)
DEFAULT_SERVICENOW_SSL_VERIFY = to_boolean(
    string=os.getenv("SERVICENOW_SSL_VERIFY", "True")
)


def register_misc_tools(mcp: FastMCP):
    @mcp.tool(tags={"kg_ingestion"})
    async def ingest_incidents_to_kg(
        action: str = Field(description="Action to perform. Must be one of: "),
        params_json: str = Field(
            default="{}", description="JSON string of parameters to pass to the action."
        ),
        client=Depends(get_client),
        ctx: Context | None = Field(
            default=None, description="MCP context for progress reporting"
        ),
    ) -> dict:
        """Manage ingest incidents to kg operations."""
        if ctx:
            ctx.info("Executing tool...")
        import json

        try:
            kwargs = json.loads(params_json)
        except Exception as e:
            return {"error": f"Invalid params_json: {e}"}

        kwargs = {k: v for k, v in kwargs.items() if v is not None}

        raise ValueError(f"Unknown action: {action}")


def register_flows_tools(mcp: FastMCP):
    @mcp.tool(tags={"flows"})
    async def servicenow_flows(
        action: str = Field(
            description="Action to perform. Must be one of: 'workflow_to_mermaid', 'collect_graph_for_roots', 'get_flow_metadata'"
        ),
        params_json: str = Field(
            default="{}", description="JSON string of parameters to pass to the action."
        ),
        client=Depends(get_client),
        ctx: Context | None = Field(
            default=None, description="MCP context for progress reporting"
        ),
    ) -> dict:
        """Manage servicenow flows operations."""
        if ctx:
            ctx.info("Executing tool...")
        import json

        try:
            kwargs = json.loads(params_json)
        except Exception as e:
            return {"error": f"Invalid params_json: {e}"}

        kwargs = {k: v for k, v in kwargs.items() if v is not None}

        if action == "workflow_to_mermaid":
            return client.workflow_to_mermaid(**kwargs)
        if action == "collect_graph_for_roots":
            return client.collect_graph_for_roots(**kwargs)
        if action == "get_flow_metadata":
            return client.get_flow_metadata(**kwargs)
        raise ValueError(f"Unknown action: {action}")


def register_application_tools(mcp: FastMCP):
    @mcp.tool(tags={"application"})
    async def servicenow_application(
        action: str = Field(
            description="Action to perform. Must be one of: 'get_application'"
        ),
        params_json: str = Field(
            default="{}", description="JSON string of parameters to pass to the action."
        ),
        client=Depends(get_client),
        ctx: Context | None = Field(
            default=None, description="MCP context for progress reporting"
        ),
    ) -> dict:
        """Manage servicenow application operations."""
        if ctx:
            await ctx.info("Executing tool...")
        import json

        try:
            kwargs = json.loads(params_json)
        except Exception as e:
            return {"error": f"Invalid params_json: {e}"}

        kwargs = {k: v for k, v in kwargs.items() if v is not None}

        if action == "get_application":
            return client.get_application(**kwargs)
        raise ValueError(f"Unknown action: {action}")


def register_cmdb_tools(mcp: FastMCP):
    @mcp.tool(tags={"cmdb"})
    async def servicenow_cmdb(
        action: str = Field(
            description="Action to perform. Must be one of: 'get_cmdb', 'delete_cmdb_relation', 'get_cmdb_instances', 'get_cmdb_instance', 'create_cmdb_instance', 'update_cmdb_instance', 'patch_cmdb_instance', 'create_cmdb_relation', 'ingest_cmdb_data'"
        ),
        params_json: str = Field(
            default="{}", description="JSON string of parameters to pass to the action."
        ),
        client=Depends(get_client),
        ctx: Context | None = Field(
            default=None, description="MCP context for progress reporting"
        ),
    ) -> dict:
        """Manage servicenow cmdb operations."""
        if ctx:
            ctx.info("Executing tool...")
        import json

        try:
            kwargs = json.loads(params_json)
        except Exception as e:
            return {"error": f"Invalid params_json: {e}"}

        kwargs = {k: v for k, v in kwargs.items() if v is not None}

        if action == "get_cmdb":
            return client.get_cmdb(**kwargs)
        if action == "delete_cmdb_relation":
            return client.delete_cmdb_relation(**kwargs)
        if action == "get_cmdb_instances":
            return client.get_cmdb_instances(**kwargs)
        if action == "get_cmdb_instance":
            return client.get_cmdb_instance(**kwargs)
        if action == "create_cmdb_instance":
            return client.create_cmdb_instance(**kwargs)
        if action == "update_cmdb_instance":
            return client.update_cmdb_instance(**kwargs)
        if action == "patch_cmdb_instance":
            return client.patch_cmdb_instance(**kwargs)
        if action == "create_cmdb_relation":
            return client.create_cmdb_relation(**kwargs)
        if action == "ingest_cmdb_data":
            return client.ingest_cmdb_data(**kwargs)
        raise ValueError(f"Unknown action: {action}")


def register_cicd_tools(mcp: FastMCP):
    @mcp.tool(tags={"cicd"})
    async def servicenow_cicd(
        action: str = Field(
            description="Action to perform. Must be one of: 'batch_install_result', 'instance_scan_progress', 'progress', 'batch_install', 'batch_rollback', 'app_repo_install', 'app_repo_publish', 'app_repo_rollback', 'full_scan', 'point_scan', 'combo_suite_scan', 'suite_scan'"
        ),
        params_json: str = Field(
            default="{}", description="JSON string of parameters to pass to the action."
        ),
        client=Depends(get_client),
        ctx: Context | None = Field(
            default=None, description="MCP context for progress reporting"
        ),
    ) -> dict:
        """Manage servicenow cicd operations."""
        if ctx:
            ctx.info("Executing tool...")
        import json

        try:
            kwargs = json.loads(params_json)
        except Exception as e:
            return {"error": f"Invalid params_json: {e}"}

        kwargs = {k: v for k, v in kwargs.items() if v is not None}

        if action == "batch_install_result":
            return client.batch_install_result(**kwargs)
        if action == "instance_scan_progress":
            return client.instance_scan_progress(**kwargs)
        if action == "progress":
            return client.progress(**kwargs)
        if action == "batch_install":
            return client.batch_install(**kwargs)
        if action == "batch_rollback":
            return client.batch_rollback(**kwargs)
        if action == "app_repo_install":
            return client.app_repo_install(**kwargs)
        if action == "app_repo_publish":
            return client.app_repo_publish(**kwargs)
        if action == "app_repo_rollback":
            return client.app_repo_rollback(**kwargs)
        if action == "full_scan":
            return client.full_scan(**kwargs)
        if action == "point_scan":
            return client.point_scan(**kwargs)
        if action == "combo_suite_scan":
            return client.combo_suite_scan(**kwargs)
        if action == "suite_scan":
            return client.suite_scan(**kwargs)
        raise ValueError(f"Unknown action: {action}")


def register_plugins_tools(mcp: FastMCP):
    @mcp.tool(tags={"plugins"})
    async def servicenow_plugins(
        action: str = Field(
            description="Action to perform. Must be one of: 'activate_plugin', 'rollback_plugin'"
        ),
        params_json: str = Field(
            default="{}", description="JSON string of parameters to pass to the action."
        ),
        client=Depends(get_client),
        ctx: Context | None = Field(
            default=None, description="MCP context for progress reporting"
        ),
    ) -> dict:
        """Manage servicenow plugins operations."""
        if ctx:
            ctx.info("Executing tool...")
        import json

        try:
            kwargs = json.loads(params_json)
        except Exception as e:
            return {"error": f"Invalid params_json: {e}"}

        kwargs = {k: v for k, v in kwargs.items() if v is not None}

        if action == "activate_plugin":
            return client.activate_plugin(**kwargs)
        if action == "rollback_plugin":
            return client.rollback_plugin(**kwargs)
        raise ValueError(f"Unknown action: {action}")


def register_source_control_tools(mcp: FastMCP):
    @mcp.tool(tags={"source_control"})
    async def servicenow_source_control(
        action: str = Field(
            description="Action to perform. Must be one of: 'apply_remote_source_control_changes', 'import_repository'"
        ),
        params_json: str = Field(
            default="{}", description="JSON string of parameters to pass to the action."
        ),
        client=Depends(get_client),
        ctx: Context | None = Field(
            default=None, description="MCP context for progress reporting"
        ),
    ) -> dict:
        """Manage servicenow source control operations."""
        if ctx:
            ctx.info("Executing tool...")
        import json

        try:
            kwargs = json.loads(params_json)
        except Exception as e:
            return {"error": f"Invalid params_json: {e}"}

        kwargs = {k: v for k, v in kwargs.items() if v is not None}

        if action == "apply_remote_source_control_changes":
            return client.apply_remote_source_control_changes(**kwargs)
        if action == "import_repository":
            return client.import_repository(**kwargs)
        raise ValueError(f"Unknown action: {action}")


def register_testing_tools(mcp: FastMCP):
    @mcp.tool(tags={"testing"})
    async def servicenow_testing(
        action: str = Field(
            description="Action to perform. Must be one of: 'run_test_suite'"
        ),
        params_json: str = Field(
            default="{}", description="JSON string of parameters to pass to the action."
        ),
        client=Depends(get_client),
        ctx: Context | None = Field(
            default=None, description="MCP context for progress reporting"
        ),
    ) -> dict:
        """Manage servicenow testing operations."""
        if ctx:
            await ctx.info("Executing tool...")
        import json

        try:
            kwargs = json.loads(params_json)
        except Exception as e:
            return {"error": f"Invalid params_json: {e}"}

        kwargs = {k: v for k, v in kwargs.items() if v is not None}

        if action == "run_test_suite":
            return client.run_test_suite(**kwargs)
        raise ValueError(f"Unknown action: {action}")


def register_update_sets_tools(mcp: FastMCP):
    @mcp.tool(tags={"update_sets"})
    async def servicenow_update_sets(
        action: str = Field(
            description="Action to perform. Must be one of: 'update_set_create', 'update_set_retrieve', 'update_set_preview', 'update_set_commit', 'update_set_commit_multiple', 'update_set_back_out'"
        ),
        params_json: str = Field(
            default="{}", description="JSON string of parameters to pass to the action."
        ),
        client=Depends(get_client),
        ctx: Context | None = Field(
            default=None, description="MCP context for progress reporting"
        ),
    ) -> dict:
        """Manage servicenow update sets operations."""
        if ctx:
            ctx.info("Executing tool...")
        import json

        try:
            kwargs = json.loads(params_json)
        except Exception as e:
            return {"error": f"Invalid params_json: {e}"}

        kwargs = {k: v for k, v in kwargs.items() if v is not None}

        if action == "update_set_create":
            return client.update_set_create(**kwargs)
        if action == "update_set_retrieve":
            return client.update_set_retrieve(**kwargs)
        if action == "update_set_preview":
            return client.update_set_preview(**kwargs)
        if action == "update_set_commit":
            return client.update_set_commit(**kwargs)
        if action == "update_set_commit_multiple":
            return client.update_set_commit_multiple(**kwargs)
        if action == "update_set_back_out":
            return client.update_set_back_out(**kwargs)
        raise ValueError(f"Unknown action: {action}")


def register_batch_tools(mcp: FastMCP):
    @mcp.tool(tags={"batch"})
    async def servicenow_batch(
        action: str = Field(
            description="Action to perform. Must be one of: 'batch_request'"
        ),
        params_json: str = Field(
            default="{}", description="JSON string of parameters to pass to the action."
        ),
        client=Depends(get_client),
        ctx: Context | None = Field(
            default=None, description="MCP context for progress reporting"
        ),
    ) -> dict:
        """Manage servicenow batch operations."""
        if ctx:
            await ctx.info("Executing tool...")
        import json

        try:
            kwargs = json.loads(params_json)
        except Exception as e:
            return {"error": f"Invalid params_json: {e}"}

        kwargs = {k: v for k, v in kwargs.items() if v is not None}

        if action == "batch_request":
            return client.batch_request(**kwargs)
        raise ValueError(f"Unknown action: {action}")


def register_change_management_tools(mcp: FastMCP):
    @mcp.tool(tags={"change_management"})
    async def servicenow_change_management(
        action: str = Field(
            description="Action to perform. Must be one of: 'get_change_requests', 'get_change_request_nextstate', 'get_change_request_schedule', 'get_change_request_tasks', 'get_change_request', 'get_change_request_ci', 'get_change_request_conflict', 'get_standard_change_request_templates', 'get_change_request_models', 'get_standard_change_request_model', 'get_standard_change_request_template', 'get_change_request_worker', 'create_change_request', 'create_change_request_task', 'create_change_request_ci_association', 'calculate_standard_change_request_risk', 'check_change_request_conflict', 'refresh_change_request_impacted_services', 'approve_change_request', 'update_change_request', 'update_change_request_first_available', 'update_change_request_task', 'delete_change_request', 'delete_change_request_task', 'delete_change_request_conflict_scan'"
        ),
        params_json: str = Field(
            default="{}", description="JSON string of parameters to pass to the action."
        ),
        client=Depends(get_client),
        ctx: Context | None = Field(
            default=None, description="MCP context for progress reporting"
        ),
    ) -> dict:
        """Manage servicenow change management operations."""
        if ctx:
            ctx.info("Executing tool...")
        import json

        try:
            kwargs = json.loads(params_json)
        except Exception as e:
            return {"error": f"Invalid params_json: {e}"}

        kwargs = {k: v for k, v in kwargs.items() if v is not None}

        if action == "get_change_requests":
            return client.get_change_requests(**kwargs)
        if action == "get_change_request_nextstate":
            return client.get_change_request_nextstate(**kwargs)
        if action == "get_change_request_schedule":
            return client.get_change_request_schedule(**kwargs)
        if action == "get_change_request_tasks":
            return client.get_change_request_tasks(**kwargs)
        if action == "get_change_request":
            return client.get_change_request(**kwargs)
        if action == "get_change_request_ci":
            return client.get_change_request_ci(**kwargs)
        if action == "get_change_request_conflict":
            return client.get_change_request_conflict(**kwargs)
        if action == "get_standard_change_request_templates":
            return client.get_standard_change_request_templates(**kwargs)
        if action == "get_change_request_models":
            return client.get_change_request_models(**kwargs)
        if action == "get_standard_change_request_model":
            return client.get_standard_change_request_model(**kwargs)
        if action == "get_standard_change_request_template":
            return client.get_standard_change_request_template(**kwargs)
        if action == "get_change_request_worker":
            return client.get_change_request_worker(**kwargs)
        if action == "create_change_request":
            return client.create_change_request(**kwargs)
        if action == "create_change_request_task":
            return client.create_change_request_task(**kwargs)
        if action == "create_change_request_ci_association":
            return client.create_change_request_ci_association(**kwargs)
        if action == "calculate_standard_change_request_risk":
            return client.calculate_standard_change_request_risk(**kwargs)
        if action == "check_change_request_conflict":
            return client.check_change_request_conflict(**kwargs)
        if action == "refresh_change_request_impacted_services":
            return client.refresh_change_request_impacted_services(**kwargs)
        if action == "approve_change_request":
            return client.approve_change_request(**kwargs)
        if action == "update_change_request":
            return client.update_change_request(**kwargs)
        if action == "update_change_request_first_available":
            return client.update_change_request_first_available(**kwargs)
        if action == "update_change_request_task":
            return client.update_change_request_task(**kwargs)
        if action == "delete_change_request":
            return client.delete_change_request(**kwargs)
        if action == "delete_change_request_task":
            return client.delete_change_request_task(**kwargs)
        if action == "delete_change_request_conflict_scan":
            return client.delete_change_request_conflict_scan(**kwargs)
        raise ValueError(f"Unknown action: {action}")


def register_cilifecycle_tools(mcp: FastMCP):
    @mcp.tool(tags={"cilifecycle"})
    async def servicenow_cilifecycle(
        action: str = Field(
            description="Action to perform. Must be one of: 'check_ci_lifecycle_compat_actions', 'register_ci_lifecycle_operator', 'unregister_ci_lifecycle_operator', 'add_ci_lifecycle_action', 'check_ci_lifecycle_lease_expired', 'check_ci_lifecycle_not_allowed_action', 'check_ci_lifecycle_not_allowed_ops_transition', 'check_ci_lifecycle_requestor_valid', 'delete_ci_lifecycle_action', 'extend_ci_lifecycle_lease', 'get_ci_lifecycle_active_actions', 'get_ci_lifecycle_status', 'set_ci_lifecycle_status'"
        ),
        params_json: str = Field(
            default="{}", description="JSON string of parameters to pass to the action."
        ),
        client=Depends(get_client),
        ctx: Context | None = Field(
            default=None, description="MCP context for progress reporting"
        ),
    ) -> dict:
        """Manage servicenow cilifecycle operations."""
        if ctx:
            await ctx.info("Executing tool...")
        import json

        try:
            kwargs = json.loads(params_json)
        except Exception as e:
            return {"error": f"Invalid params_json: {e}"}

        kwargs = {k: v for k, v in kwargs.items() if v is not None}

        if action == "check_ci_lifecycle_compat_actions":
            return client.check_ci_lifecycle_compat_actions(**kwargs)
        if action == "register_ci_lifecycle_operator":
            return client.register_ci_lifecycle_operator(**kwargs)
        if action == "unregister_ci_lifecycle_operator":
            return client.unregister_ci_lifecycle_operator(**kwargs)
        if action == "add_ci_lifecycle_action":
            return client.add_ci_lifecycle_action(**kwargs)
        if action == "check_ci_lifecycle_lease_expired":
            return client.check_ci_lifecycle_lease_expired(**kwargs)
        if action == "check_ci_lifecycle_not_allowed_action":
            return client.check_ci_lifecycle_not_allowed_action(**kwargs)
        if action == "check_ci_lifecycle_not_allowed_ops_transition":
            return client.check_ci_lifecycle_not_allowed_ops_transition(**kwargs)
        if action == "check_ci_lifecycle_requestor_valid":
            return client.check_ci_lifecycle_requestor_valid(**kwargs)
        if action == "delete_ci_lifecycle_action":
            return client.delete_ci_lifecycle_action(**kwargs)
        if action == "extend_ci_lifecycle_lease":
            return client.extend_ci_lifecycle_lease(**kwargs)
        if action == "get_ci_lifecycle_active_actions":
            return client.get_ci_lifecycle_active_actions(**kwargs)
        if action == "get_ci_lifecycle_status":
            return client.get_ci_lifecycle_status(**kwargs)
        if action == "set_ci_lifecycle_status":
            return client.set_ci_lifecycle_status(**kwargs)
        raise ValueError(f"Unknown action: {action}")


def register_devops_tools(mcp: FastMCP):
    @mcp.tool(tags={"devops"})
    async def servicenow_devops(
        action: str = Field(
            description="Action to perform. Must be one of: 'check_devops_change_control', 'register_devops_artifact', 'check_devops_step_mapping', 'get_devops_change_info', 'get_devops_code_schema', 'get_devops_onboarding_status', 'get_devops_orchestration_schema', 'get_devops_plan_schema'"
        ),
        params_json: str = Field(
            default="{}", description="JSON string of parameters to pass to the action."
        ),
        client=Depends(get_client),
        ctx: Context | None = Field(
            default=None, description="MCP context for progress reporting"
        ),
    ) -> dict:
        """Manage servicenow devops operations."""
        if ctx:
            await ctx.info("Executing tool...")
        import json

        try:
            kwargs = json.loads(params_json)
        except Exception as e:
            return {"error": f"Invalid params_json: {e}"}

        kwargs = {k: v for k, v in kwargs.items() if v is not None}

        if action == "check_devops_change_control":
            return client.check_devops_change_control(**kwargs)
        if action == "register_devops_artifact":
            return client.register_devops_artifact(**kwargs)
        if action == "check_devops_step_mapping":
            return client.check_devops_step_mapping(**kwargs)
        if action == "get_devops_change_info":
            return client.get_devops_change_info(**kwargs)
        if action == "get_devops_code_schema":
            return client.get_devops_code_schema(**kwargs)
        if action == "get_devops_onboarding_status":
            return client.get_devops_onboarding_status(**kwargs)
        if action == "get_devops_orchestration_schema":
            return client.get_devops_orchestration_schema(**kwargs)
        if action == "get_devops_plan_schema":
            return client.get_devops_plan_schema(**kwargs)
        raise ValueError(f"Unknown action: {action}")


def register_import_sets_tools(mcp: FastMCP):
    @mcp.tool(tags={"import_sets"})
    async def servicenow_import_sets(
        action: str = Field(
            description="Action to perform. Must be one of: 'get_import_set', 'insert_import_set', 'insert_multiple_import_sets'"
        ),
        params_json: str = Field(
            default="{}", description="JSON string of parameters to pass to the action."
        ),
        client=Depends(get_client),
        ctx: Context | None = Field(
            default=None, description="MCP context for progress reporting"
        ),
    ) -> dict:
        """Manage servicenow import sets operations."""
        if ctx:
            ctx.info("Executing tool...")
        import json

        try:
            kwargs = json.loads(params_json)
        except Exception as e:
            return {"error": f"Invalid params_json: {e}"}

        kwargs = {k: v for k, v in kwargs.items() if v is not None}

        if action == "get_import_set":
            return client.get_import_set(**kwargs)
        if action == "insert_import_set":
            return client.insert_import_set(**kwargs)
        if action == "insert_multiple_import_sets":
            return client.insert_multiple_import_sets(**kwargs)
        raise ValueError(f"Unknown action: {action}")


def register_incidents_tools(mcp: FastMCP):
    @mcp.tool(tags={"incidents"})
    async def servicenow_incidents(
        action: str = Field(
            description="Action to perform. Must be one of: 'get_incidents', 'create_incident', 'get_incident'"
        ),
        params_json: str = Field(
            default="{}", description="JSON string of parameters to pass to the action."
        ),
        client=Depends(get_client),
        ctx: Context | None = Field(
            default=None, description="MCP context for progress reporting"
        ),
    ) -> dict:
        """Manage servicenow incidents operations."""
        if ctx:
            await ctx.info("Executing tool...")
        import json

        try:
            kwargs = json.loads(params_json)
        except Exception as e:
            return {"error": f"Invalid params_json: {e}"}

        kwargs = {k: v for k, v in kwargs.items() if v is not None}

        if action == "get_incidents":
            return client.get_incidents(**kwargs)
        if action == "create_incident":
            return client.create_incident(**kwargs)
        if action == "get_incident":
            return client.get_incident(**kwargs)
        raise ValueError(f"Unknown action: {action}")


def register_knowledge_management_tools(mcp: FastMCP):
    @mcp.tool(tags={"knowledge_management"})
    async def servicenow_knowledge_management(
        action: str = Field(
            description="Action to perform. Must be one of: 'get_knowledge_articles', 'get_knowledge_article', 'get_knowledge_article_attachment', 'get_featured_knowledge_article', 'get_most_viewed_knowledge_articles'"
        ),
        params_json: str = Field(
            default="{}", description="JSON string of parameters to pass to the action."
        ),
        client=Depends(get_client),
        ctx: Context | None = Field(
            default=None, description="MCP context for progress reporting"
        ),
    ) -> dict:
        """Manage servicenow knowledge management operations."""
        if ctx:
            ctx.info("Executing tool...")
        import json

        try:
            kwargs = json.loads(params_json)
        except Exception as e:
            return {"error": f"Invalid params_json: {e}"}

        kwargs = {k: v for k, v in kwargs.items() if v is not None}

        if action == "get_knowledge_articles":
            return client.get_knowledge_articles(**kwargs)
        if action == "get_knowledge_article":
            return client.get_knowledge_article(**kwargs)
        if action == "get_knowledge_article_attachment":
            return client.get_knowledge_article_attachment(**kwargs)
        if action == "get_featured_knowledge_article":
            return client.get_featured_knowledge_article(**kwargs)
        if action == "get_most_viewed_knowledge_articles":
            return client.get_most_viewed_knowledge_articles(**kwargs)
        raise ValueError(f"Unknown action: {action}")


def register_table_api_tools(mcp: FastMCP):
    @mcp.tool(tags={"table_api"})
    async def servicenow_table_api(
        action: str = Field(
            description="Action to perform. Must be one of: 'delete_table_record', 'get_table', 'get_table_record', 'patch_table_record', 'update_table_record', 'add_table_record'"
        ),
        params_json: str = Field(
            default="{}", description="JSON string of parameters to pass to the action."
        ),
        client=Depends(get_client),
        ctx: Context | None = Field(
            default=None, description="MCP context for progress reporting"
        ),
    ) -> dict:
        """Manage servicenow table api operations."""
        if ctx:
            ctx.info("Executing tool...")
        import json

        try:
            kwargs = json.loads(params_json)
        except Exception as e:
            return {"error": f"Invalid params_json: {e}"}

        kwargs = {k: v for k, v in kwargs.items() if v is not None}

        if action == "delete_table_record":
            return client.delete_table_record(**kwargs)
        if action == "get_table":
            return client.get_table(**kwargs)
        if action == "get_table_record":
            return client.get_table_record(**kwargs)
        if action == "patch_table_record":
            return client.patch_table_record(**kwargs)
        if action == "update_table_record":
            return client.update_table_record(**kwargs)
        if action == "add_table_record":
            return client.add_table_record(**kwargs)
        raise ValueError(f"Unknown action: {action}")


def register_auth_tools(mcp: FastMCP):
    @mcp.tool(tags={"auth"})
    async def servicenow_auth(
        action: str = Field(
            description="Action to perform. Must be one of: 'refresh_auth_token'"
        ),
        params_json: str = Field(
            default="{}", description="JSON string of parameters to pass to the action."
        ),
        client=Depends(get_client),
        ctx: Context | None = Field(
            default=None, description="MCP context for progress reporting"
        ),
    ) -> dict:
        """Manage servicenow auth operations."""
        if ctx:
            ctx.info("Executing tool...")
        import json

        try:
            kwargs = json.loads(params_json)
        except Exception as e:
            return {"error": f"Invalid params_json: {e}"}

        kwargs = {k: v for k, v in kwargs.items() if v is not None}

        if action == "refresh_auth_token":
            return client.refresh_auth_token(**kwargs)
        raise ValueError(f"Unknown action: {action}")


def register_custom_api_tools(mcp: FastMCP):
    @mcp.tool(tags={"custom_api"})
    async def servicenow_custom_api(
        action: str = Field(
            description="Action to perform. Must be one of: 'api_request'"
        ),
        params_json: str = Field(
            default="{}", description="JSON string of parameters to pass to the action."
        ),
        client=Depends(get_client),
        ctx: Context | None = Field(
            default=None, description="MCP context for progress reporting"
        ),
    ) -> dict:
        """Manage servicenow custom api operations."""
        if ctx:
            ctx.info("Executing tool...")
        import json

        try:
            kwargs = json.loads(params_json)
        except Exception as e:
            return {"error": f"Invalid params_json: {e}"}

        kwargs = {k: v for k, v in kwargs.items() if v is not None}

        if action == "api_request":
            return client.api_request(**kwargs)
        raise ValueError(f"Unknown action: {action}")


def register_email_tools(mcp: FastMCP):
    @mcp.tool(tags={"email"})
    async def servicenow_email(
        action: str = Field(
            description="Action to perform. Must be one of: 'send_email'"
        ),
        params_json: str = Field(
            default="{}", description="JSON string of parameters to pass to the action."
        ),
        client=Depends(get_client),
        ctx: Context | None = Field(
            default=None, description="MCP context for progress reporting"
        ),
    ) -> dict:
        """Manage servicenow email operations."""
        if ctx:
            ctx.info("Executing tool...")
        import json

        try:
            kwargs = json.loads(params_json)
        except Exception as e:
            return {"error": f"Invalid params_json: {e}"}

        kwargs = {k: v for k, v in kwargs.items() if v is not None}

        if action == "send_email":
            return client.send_email(**kwargs)
        raise ValueError(f"Unknown action: {action}")


def register_data_classification_tools(mcp: FastMCP):
    @mcp.tool(tags={"data_classification"})
    async def servicenow_data_classification(
        action: str = Field(
            description="Action to perform. Must be one of: 'get_data_classification'"
        ),
        params_json: str = Field(
            default="{}", description="JSON string of parameters to pass to the action."
        ),
        client=Depends(get_client),
        ctx: Context | None = Field(
            default=None, description="MCP context for progress reporting"
        ),
    ) -> dict:
        """Manage servicenow data classification operations."""
        if ctx:
            ctx.info("Executing tool...")
        import json

        try:
            kwargs = json.loads(params_json)
        except Exception as e:
            return {"error": f"Invalid params_json: {e}"}

        kwargs = {k: v for k, v in kwargs.items() if v is not None}

        if action == "get_data_classification":
            return client.get_data_classification(**kwargs)
        raise ValueError(f"Unknown action: {action}")


def register_aggregate_tools(mcp: FastMCP):
    @mcp.tool(tags={"aggregate"})
    async def servicenow_aggregate(
        action: str = Field(
            description="Action to perform. Must be one of: 'get_stats'"
        ),
        params_json: str = Field(
            default="{}", description="JSON string of parameters to pass to the action."
        ),
        client=Depends(get_client),
        ctx: Context | None = Field(
            default=None, description="MCP context for progress reporting"
        ),
    ) -> dict:
        """Manage servicenow aggregate operations."""
        if ctx:
            ctx.info("Executing tool...")
        import json

        try:
            kwargs = json.loads(params_json)
        except Exception as e:
            return {"error": f"Invalid params_json: {e}"}

        kwargs = {k: v for k, v in kwargs.items() if v is not None}

        if action == "get_stats":
            return client.get_stats(**kwargs)
        raise ValueError(f"Unknown action: {action}")


def register_activity_subscriptions_tools(mcp: FastMCP):
    @mcp.tool(tags={"activity_subscriptions"})
    async def servicenow_activity_subscriptions(
        action: str = Field(
            description="Action to perform. Must be one of: 'get_activity_subscriptions'"
        ),
        params_json: str = Field(
            default="{}", description="JSON string of parameters to pass to the action."
        ),
        client=Depends(get_client),
        ctx: Context | None = Field(
            default=None, description="MCP context for progress reporting"
        ),
    ) -> dict:
        """Manage servicenow activity subscriptions operations."""
        if ctx:
            ctx.info("Executing tool...")
        import json

        try:
            kwargs = json.loads(params_json)
        except Exception as e:
            return {"error": f"Invalid params_json: {e}"}

        kwargs = {k: v for k, v in kwargs.items() if v is not None}

        if action == "get_activity_subscriptions":
            return client.get_activity_subscriptions(**kwargs)
        raise ValueError(f"Unknown action: {action}")


def register_account_tools(mcp: FastMCP):
    @mcp.tool(tags={"account"})
    async def servicenow_account(
        action: str = Field(
            description="Action to perform. Must be one of: 'get_account'"
        ),
        params_json: str = Field(
            default="{}", description="JSON string of parameters to pass to the action."
        ),
        client=Depends(get_client),
        ctx: Context | None = Field(
            default=None, description="MCP context for progress reporting"
        ),
    ) -> dict:
        """Manage servicenow account operations."""
        if ctx:
            ctx.info("Executing tool...")
        import json

        try:
            kwargs = json.loads(params_json)
        except Exception as e:
            return {"error": f"Invalid params_json: {e}"}

        kwargs = {k: v for k, v in kwargs.items() if v is not None}

        if action == "get_account":
            return client.get_account(**kwargs)
        raise ValueError(f"Unknown action: {action}")


def register_hr_tools(mcp: FastMCP):
    @mcp.tool(tags={"hr"})
    async def servicenow_hr(
        action: str = Field(
            description="Action to perform. Must be one of: 'get_hr_profile'"
        ),
        params_json: str = Field(
            default="{}", description="JSON string of parameters to pass to the action."
        ),
        client=Depends(get_client),
        ctx: Context | None = Field(
            default=None, description="MCP context for progress reporting"
        ),
    ) -> dict:
        """Manage servicenow hr operations."""
        if ctx:
            ctx.info("Executing tool...")
        import json

        try:
            kwargs = json.loads(params_json)
        except Exception as e:
            return {"error": f"Invalid params_json: {e}"}

        kwargs = {k: v for k, v in kwargs.items() if v is not None}

        if action == "get_hr_profile":
            return client.get_hr_profile(**kwargs)
        raise ValueError(f"Unknown action: {action}")


def register_metricbase_tools(mcp: FastMCP):
    @mcp.tool(tags={"metricbase"})
    async def servicenow_metricbase(
        action: str = Field(
            description="Action to perform. Must be one of: 'metricbase_insert'"
        ),
        params_json: str = Field(
            default="{}", description="JSON string of parameters to pass to the action."
        ),
        client=Depends(get_client),
        ctx: Context | None = Field(
            default=None, description="MCP context for progress reporting"
        ),
    ) -> dict:
        """Manage servicenow metricbase operations."""
        if ctx:
            ctx.info("Executing tool...")
        import json

        try:
            kwargs = json.loads(params_json)
        except Exception as e:
            return {"error": f"Invalid params_json: {e}"}

        kwargs = {k: v for k, v in kwargs.items() if v is not None}

        if action == "metricbase_insert":
            return client.metricbase_insert(**kwargs)
        raise ValueError(f"Unknown action: {action}")


def register_attachment_tools(mcp: FastMCP):
    @mcp.tool(tags={"attachment"})
    async def servicenow_attachment(
        action: str = Field(
            description="Action to perform. Must be one of: 'get_attachment', 'upload_attachment', 'delete_attachment'"
        ),
        params_json: str = Field(
            default="{}", description="JSON string of parameters to pass to the action."
        ),
        client=Depends(get_client),
        ctx: Context | None = Field(
            default=None, description="MCP context for progress reporting"
        ),
    ) -> dict:
        """Manage servicenow attachment operations."""
        if ctx:
            ctx.info("Executing tool...")
        import json

        try:
            kwargs = json.loads(params_json)
        except Exception as e:
            return {"error": f"Invalid params_json: {e}"}

        kwargs = {k: v for k, v in kwargs.items() if v is not None}

        if action == "get_attachment":
            return client.get_attachment(**kwargs)
        if action == "upload_attachment":
            return client.upload_attachment(**kwargs)
        if action == "delete_attachment":
            return client.delete_attachment(**kwargs)
        raise ValueError(f"Unknown action: {action}")


def register_service_qualification_tools(mcp: FastMCP):
    @mcp.tool(tags={"service_qualification"})
    async def servicenow_service_qualification(
        action: str = Field(
            description="Action to perform. Must be one of: 'check_service_qualification', 'get_service_qualification', 'process_service_qualification_result'"
        ),
        params_json: str = Field(
            default="{}", description="JSON string of parameters to pass to the action."
        ),
        client=Depends(get_client),
        ctx: Context | None = Field(
            default=None, description="MCP context for progress reporting"
        ),
    ) -> dict:
        """Manage servicenow service qualification operations."""
        if ctx:
            ctx.info("Executing tool...")
        import json

        try:
            kwargs = json.loads(params_json)
        except Exception as e:
            return {"error": f"Invalid params_json: {e}"}

        kwargs = {k: v for k, v in kwargs.items() if v is not None}

        if action == "check_service_qualification":
            return client.check_service_qualification(**kwargs)
        if action == "get_service_qualification":
            return client.get_service_qualification(**kwargs)
        if action == "process_service_qualification_result":
            return client.process_service_qualification_result(**kwargs)
        raise ValueError(f"Unknown action: {action}")


def register_ppm_tools(mcp: FastMCP):
    @mcp.tool(tags={"ppm"})
    async def servicenow_ppm(
        action: str = Field(
            description="Action to perform. Must be one of: 'insert_cost_plans', 'insert_project_tasks'"
        ),
        params_json: str = Field(
            default="{}", description="JSON string of parameters to pass to the action."
        ),
        client=Depends(get_client),
        ctx: Context | None = Field(
            default=None, description="MCP context for progress reporting"
        ),
    ) -> dict:
        """Manage servicenow ppm operations."""
        if ctx:
            ctx.info("Executing tool...")
        import json

        try:
            kwargs = json.loads(params_json)
        except Exception as e:
            return {"error": f"Invalid params_json: {e}"}

        kwargs = {k: v for k, v in kwargs.items() if v is not None}

        if action == "insert_cost_plans":
            return client.insert_cost_plans(**kwargs)
        if action == "insert_project_tasks":
            return client.insert_project_tasks(**kwargs)
        raise ValueError(f"Unknown action: {action}")


def register_product_inventory_tools(mcp: FastMCP):
    @mcp.tool(tags={"product_inventory"})
    async def servicenow_product_inventory(
        action: str = Field(
            description="Action to perform. Must be one of: 'get_product_inventory', 'delete_product_inventory'"
        ),
        params_json: str = Field(
            default="{}", description="JSON string of parameters to pass to the action."
        ),
        client=Depends(get_client),
        ctx: Context | None = Field(
            default=None, description="MCP context for progress reporting"
        ),
    ) -> dict:
        """Manage servicenow product inventory operations."""
        if ctx:
            ctx.info("Executing tool...")
        import json

        try:
            kwargs = json.loads(params_json)
        except Exception as e:
            return {"error": f"Invalid params_json: {e}"}

        kwargs = {k: v for k, v in kwargs.items() if v is not None}

        if action == "get_product_inventory":
            return client.get_product_inventory(**kwargs)
        if action == "delete_product_inventory":
            return client.delete_product_inventory(**kwargs)
        raise ValueError(f"Unknown action: {action}")


def register_prompts(mcp: FastMCP):

    @mcp.prompt
    def create_incident_prompt(
        short_description: str, description: str, priority: int = 3
    ) -> str:
        """
        Generates a prompt for creating a ServiceNow incident.
        """
        return f"Create a new ServiceNow incident with short description: '{short_description}', full description: '{description}', and priority: {priority}. Use the add_table_record tool with table='incident'."

    @mcp.prompt
    def get_incident_with_fields_prompt(sysparm_fields: str) -> str:
        """
        Generates a prompt for getting ServiceNow Incidents with certain fields
        """
        return f"Get the incidents from ServiceNow and display them with the following fields: [{sysparm_fields}] in a table format"

    @mcp.prompt
    def get_incident_by_number_prompt(incident_number: str) -> str:
        """
        Generates a prompt for getting a ServiceNow Incident by number
        """
        return f"Get the incident with sysparm_query='number={incident_number}'"

    @mcp.prompt
    def get_change_by_number_prompt(change_number: str) -> str:
        """
        Generates a prompt for getting a ServiceNow Change by number
        """
        return f"Get the change request with sysparm_query='number={change_number}'"

    @mcp.prompt
    def query_table_prompt_prompt(
        table: str, sysparm_fields: str, sysparm_query: str
    ) -> str:
        """
        Generates a prompt for querying a ServiceNow table.
        """
        return f"Query the ServiceNow table '{table}' with sysparm_query: '{sysparm_query}' and sysparm_fields: '{sysparm_fields}'. Use the get_table tool with appropriate parameters."


def get_mcp_instance() -> tuple[Any, Any, Any, Any, Any]:
    """Initialize and return the MCP instance, args, and middlewares."""
    load_dotenv(find_dotenv())
    args, mcp, middlewares = create_mcp_server(
        name="ServiceNow",
        version=__version__,
        instructions="ServiceNow MCP Server — Manage incidents, CMDB, workflows, CICD, and more in your ServiceNow instance.",
    )
    imported_tools = []
    imported_resources = []
    if args.openapi_file:
        if config["enable_delegation"]:
            raise ValueError("OpenAPI import not supported with delegation enabled")
        try:
            with open(args.openapi_file) as f:
                spec = json.load(f)

            async def _load_openapi_tools():
                token = None
                username = None
                password = None
                client_id = None
                client_secret = None
                if args.openapi_use_token:
                    token = getattr(local, "user_token", None)
                    if not token:
                        raise ValueError(
                            "OpenAPI import requires --openapi-use-token and a valid Bearer token in the request"
                        )
                    print("Using incoming JWT for OpenAPI import", file=sys.stderr)
                else:
                    username = args.openapi_username or os.getenv("OPENAPI_USERNAME")
                    password = args.openapi_password or os.getenv("OPENAPI_PASSWORD")
                    client_id = args.openapi_client_id or os.getenv("OPENAPI_CLIENT_ID")
                    client_secret = args.openapi_client_secret or os.getenv(
                        "OPENAPI_CLIENT_SECRET"
                    )
                    if not (username and password) and (
                        not (client_id and client_secret)
                    ):
                        raise ValueError(
                            "OpenAPI import requires either --openapi-use-token or (username+password) or (client_id+client_secret)"
                        )
                api = get_client()
                base_url = args.openapi_base_url or api.url
                async with httpx.AsyncClient(
                    base_url=base_url, headers=api.headers, verify=api.verify
                ) as client:
                    openapi_mcp = FastMCP.from_openapi(
                        openapi_spec=spec, client=client, name="OpenAPI Tools"
                    )
                    tools = await openapi_mcp.get_tools()
                    resources = await openapi_mcp.get_resources()
                    return (tools, resources)

            print("Importing OpenAPI tools...", file=sys.stderr)
            imported_tools, imported_resources = asyncio.run(_load_openapi_tools())
            print(
                f"Imported {len(imported_tools)} tools, {len(imported_resources)} resources",
                file=sys.stderr,
            )
            for tool in imported_tools:
                mcp.add_tool(tool)
            for resource in imported_resources:
                mcp.add_resource(resource)
        except Exception as exc:
            print(f"OpenAPI import failed: {exc}", file=sys.stderr)
            logger.error("OpenAPI import failed", extra={"error": str(exc)})
            sys.exit(1)
    DEFAULT_MISCTOOL = to_boolean(os.getenv("MISCTOOL", "True"))
    if DEFAULT_MISCTOOL:
        register_misc_tools(mcp)
    DEFAULT_FLOWSTOOL = to_boolean(os.getenv("FLOWSTOOL", "True"))
    if DEFAULT_FLOWSTOOL:
        register_flows_tools(mcp)
    DEFAULT_APPLICATIONTOOL = to_boolean(os.getenv("APPLICATIONTOOL", "True"))
    if DEFAULT_APPLICATIONTOOL:
        register_application_tools(mcp)
    DEFAULT_CMDBTOOL = to_boolean(os.getenv("CMDBTOOL", "True"))
    if DEFAULT_CMDBTOOL:
        register_cmdb_tools(mcp)
    DEFAULT_CICDTOOL = to_boolean(os.getenv("CICDTOOL", "True"))
    if DEFAULT_CICDTOOL:
        register_cicd_tools(mcp)
    DEFAULT_PLUGINSTOOL = to_boolean(os.getenv("PLUGINSTOOL", "True"))
    if DEFAULT_PLUGINSTOOL:
        register_plugins_tools(mcp)
    DEFAULT_SOURCE_CONTROLTOOL = to_boolean(os.getenv("SOURCE_CONTROLTOOL", "True"))
    if DEFAULT_SOURCE_CONTROLTOOL:
        register_source_control_tools(mcp)
    DEFAULT_TESTINGTOOL = to_boolean(os.getenv("TESTINGTOOL", "True"))
    if DEFAULT_TESTINGTOOL:
        register_testing_tools(mcp)
    DEFAULT_UPDATE_SETSTOOL = to_boolean(os.getenv("UPDATE_SETSTOOL", "True"))
    if DEFAULT_UPDATE_SETSTOOL:
        register_update_sets_tools(mcp)
    DEFAULT_BATCHTOOL = to_boolean(os.getenv("BATCHTOOL", "True"))
    if DEFAULT_BATCHTOOL:
        register_batch_tools(mcp)
    DEFAULT_CHANGE_MANAGEMENTTOOL = to_boolean(
        os.getenv("CHANGE_MANAGEMENTTOOL", "True")
    )
    if DEFAULT_CHANGE_MANAGEMENTTOOL:
        register_change_management_tools(mcp)
    DEFAULT_CILIFECYCLETOOL = to_boolean(os.getenv("CILIFECYCLETOOL", "True"))
    if DEFAULT_CILIFECYCLETOOL:
        register_cilifecycle_tools(mcp)
    DEFAULT_DEVOPSTOOL = to_boolean(os.getenv("DEVOPSTOOL", "True"))
    if DEFAULT_DEVOPSTOOL:
        register_devops_tools(mcp)
    DEFAULT_IMPORT_SETSTOOL = to_boolean(os.getenv("IMPORT_SETSTOOL", "True"))
    if DEFAULT_IMPORT_SETSTOOL:
        register_import_sets_tools(mcp)
    DEFAULT_INCIDENTSTOOL = to_boolean(os.getenv("INCIDENTSTOOL", "True"))
    if DEFAULT_INCIDENTSTOOL:
        register_incidents_tools(mcp)
    DEFAULT_KNOWLEDGE_MANAGEMENTTOOL = to_boolean(
        os.getenv("KNOWLEDGE_MANAGEMENTTOOL", "True")
    )
    if DEFAULT_KNOWLEDGE_MANAGEMENTTOOL:
        register_knowledge_management_tools(mcp)
    DEFAULT_TABLE_APITOOL = to_boolean(os.getenv("TABLE_APITOOL", "True"))
    if DEFAULT_TABLE_APITOOL:
        register_table_api_tools(mcp)
    DEFAULT_AUTHTOOL = to_boolean(os.getenv("AUTHTOOL", "True"))
    if DEFAULT_AUTHTOOL:
        register_auth_tools(mcp)
    DEFAULT_CUSTOM_APITOOL = to_boolean(os.getenv("CUSTOM_APITOOL", "True"))
    if DEFAULT_CUSTOM_APITOOL:
        register_custom_api_tools(mcp)
    DEFAULT_EMAILTOOL = to_boolean(os.getenv("EMAILTOOL", "True"))
    if DEFAULT_EMAILTOOL:
        register_email_tools(mcp)
    DEFAULT_DATA_CLASSIFICATIONTOOL = to_boolean(
        os.getenv("DATA_CLASSIFICATIONTOOL", "True")
    )
    if DEFAULT_DATA_CLASSIFICATIONTOOL:
        register_data_classification_tools(mcp)
    DEFAULT_ATTACHMENTTOOL = to_boolean(os.getenv("ATTACHMENTTOOL", "True"))
    if DEFAULT_ATTACHMENTTOOL:
        register_attachment_tools(mcp)
    DEFAULT_AGGREGATETOOL = to_boolean(os.getenv("AGGREGATETOOL", "True"))
    if DEFAULT_AGGREGATETOOL:
        register_aggregate_tools(mcp)
    DEFAULT_ACTIVITY_SUBSCRIPTIONSTOOL = to_boolean(
        os.getenv("ACTIVITY_SUBSCRIPTIONSTOOL", "True")
    )
    if DEFAULT_ACTIVITY_SUBSCRIPTIONSTOOL:
        register_activity_subscriptions_tools(mcp)
    DEFAULT_ACCOUNTTOOL = to_boolean(os.getenv("ACCOUNTTOOL", "True"))
    if DEFAULT_ACCOUNTTOOL:
        register_account_tools(mcp)
    DEFAULT_HRTOOL = to_boolean(os.getenv("HRTOOL", "True"))
    if DEFAULT_HRTOOL:
        register_hr_tools(mcp)
    DEFAULT_METRICBASETOOL = to_boolean(os.getenv("METRICBASETOOL", "True"))
    if DEFAULT_METRICBASETOOL:
        register_metricbase_tools(mcp)
    DEFAULT_SERVICE_QUALIFICATIONTOOL = to_boolean(
        os.getenv("SERVICE_QUALIFICATIONTOOL", "True")
    )
    if DEFAULT_SERVICE_QUALIFICATIONTOOL:
        register_service_qualification_tools(mcp)
    DEFAULT_PPMTOOL = to_boolean(os.getenv("PPMTOOL", "True"))
    if DEFAULT_PPMTOOL:
        register_ppm_tools(mcp)
    DEFAULT_PRODUCT_INVENTORYTOOL = to_boolean(
        os.getenv("PRODUCT_INVENTORYTOOL", "True")
    )
    if DEFAULT_PRODUCT_INVENTORYTOOL:
        register_product_inventory_tools(mcp)
    register_prompts(mcp)
    for tool in imported_tools:
        mcp.add_tool(tool)
    for resource in imported_resources:
        mcp.add_resource(resource)
    for mw in middlewares:
        mcp.add_middleware(mw)
    registered_tags = []
    return (mcp, args, middlewares, registered_tags, imported_tools)


def mcp_server() -> None:
    mcp, args, middlewares, registered_tags, imported_tools = get_mcp_instance()
    print("\nStarting ServiceNow MCP Server", file=sys.stderr)
    print(f"  Transport: {args.transport.upper()}", file=sys.stderr)
    print(f"  Auth: {args.auth_type}", file=sys.stderr)
    print(
        f"  Delegation: {('ON' if config['enable_delegation'] else 'OFF')}",
        file=sys.stderr,
    )
    print(f"  Eunomia: {args.eunomia_type}", file=sys.stderr)
    print(f"  Imported OpenAPI Tools: {len(imported_tools)} total", file=sys.stderr)
    if args.transport == "stdio":
        mcp.run(transport="stdio")
    elif args.transport == "streamable-http":
        mcp.run(transport="streamable-http", host=args.host, port=args.port)
    elif args.transport == "sse":
        mcp.run(transport="sse", host=args.host, port=args.port)
    else:
        logger.error("Invalid transport", extra={"transport": args.transport})
        sys.exit(1)


if __name__ == "__main__":
    mcp_server()
