import warnings

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
from agent_utilities.base_utilities import to_boolean, to_integer
from agent_utilities.mcp_utilities import (
    config,
    create_mcp_server,
    ctx_confirm_destructive,
    ctx_progress,
)
from dotenv import find_dotenv, load_dotenv
from fastmcp import Context, FastMCP
from fastmcp.dependencies import Depends
from fastmcp.utilities.logging import get_logger
from pydantic import Field

from servicenow_api.auth import get_client
from servicenow_api.servicenow_models import FlowReportResult, Response

__version__ = "1.15.0"
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

    @mcp.tool(
        description="Ingest a batch of ServiceNow Incidents into the agent-utilities Knowledge Graph.",
        tags={"kg_ingestion"},
    )
    async def ingest_incidents_to_kg(
        limit: int = Field(default=100, description="Max incidents to sync"),
        client=Depends(get_client),
        ctx: Context = Field(default=None),
    ) -> str:
        """Fetch incidents and ingest them into the enterprise knowledge graph."""
        from agent_utilities.knowledge_graph.core.engine import RegistryGraphEngine

        stub_data = [
            {"id": f"incident:INC000{i}", "name": f"Incident {i}", "type": "Incident"}
            for i in range(1, 6)
        ]
        kg = RegistryGraphEngine()
        kg.ingest_external_batch("servicenow", stub_data)
        return f"Ingested {len(stub_data)} incidents to the Knowledge Graph."

    logger.info("DEBUG: Executing register_tools...")
    logger.info("DEBUG: Registering get_incidents...")


def register_flows_tools(mcp: FastMCP):

    @mcp.tool(
        description="Generate a UNIFIED Mermaid diagram + rich Markdown report for multiple ServiceNow flows. Optional: leave flow_identifiers empty to fetch ALL active flows up to 1000 limit. Unrelated flow groups are split into separate safe-to-render diagram blocks. By default saves a polished .md file.",
        tags={"flows"},
    )
    async def workflow_to_mermaid(
        flow_identifiers: list[str] = Field(
            description="List of flow names or sys_ids. If empty, fetches ALL active flows.",
            default_factory=list,
        ),
        save_to_file: bool = Field(
            default=True,
            description="Default: True → saves polished .md file. Set False to return Markdown as text only.",
        ),
        output_dir: str | None = Field(
            default="./servicenow_flow_reports",
            description="Default folder for saved reports",
        ),
        mermaid_name: str | None = Field(
            default="unified_flow_diagram", description="mermaid_name"
        ),
        max_depth: int | None = Field(
            default=5, description="Maximum recursion depth for subflows"
        ),
        segment_by_root: bool = Field(
            default=True,
            description="If True (default), each flow gets its own diagram block.",
        ),
        destination_file: str | None = Field(
            default=None,
            description="Explicit full path to save the report (e.g. /tmp/report.md)",
        ),
        client=Depends(get_client),
        ctx: Context = Field(
            description="MCP context for progress reporting", default=None
        ),
    ) -> FlowReportResult:
        """
        Generate a unified Mermaid diagram + rich Markdown report for multiple ServiceNow flows.
        """
        return client.workflow_to_mermaid(
            flow_identifiers=flow_identifiers,
            save_to_file=save_to_file,
            output_dir=output_dir,
            mermaid_name=mermaid_name,
            max_depth=max_depth,
            segment_by_root=segment_by_root,
            destination_file=destination_file,
        )


def register_application_tools(mcp: FastMCP):

    @mcp.tool(tags={"application"})
    async def get_application(
        application_id: str = Field(
            description="The unique identifier of the application to retrieve"
        ),
        client=Depends(get_client),
        ctx: Context = Field(
            description="MCP context for progress reporting", default=None
        ),
    ) -> Response:
        """
        Retrieves details of a specific application from a ServiceNow instance by its unique identifier.
        """
        return client.get_application(application_id)


def register_cmdb_tools(mcp: FastMCP):

    @mcp.tool(tags={"cmdb"})
    async def servicenow_cmdb(
        action: str = Field(
            description="Action to perform. Must be one of: 'get_cmdb', 'delete_cmdb_relation', 'get_cmdb_instances', 'get_cmdb_instance', 'create_cmdb_instance', 'update_cmdb_instance', 'patch_cmdb_instance', 'create_cmdb_relation', 'ingest_cmdb_data'"
        ),
        cmdb_id: str | None = Field(
            default=None,
            description="The unique identifier of the CMDB record to retrieve",
        ),
        className: str | None = Field(default=None, description="CMDB class name"),
        sys_id: str | None = Field(default=None, description="Sys_id of the CI"),
        rel_sys_id: str | None = Field(
            default=None, description="Sys_id of the relation to remove"
        ),
        sysparm_limit: str | None = Field(
            default="10000", description="Maximum number of records to return"
        ),
        sysparm_offset: str | None = Field(
            default="0", description="Starting record index"
        ),
        sysparm_query: str | None = Field(
            default=None, description="Encoded query used to filter the result set"
        ),
        source: str | None = Field(default=None, description="Discovery source"),
        attributes: dict | None = Field(
            default=None, description="Data attributes to define in the CI record"
        ),
        inbound_relations: list[dict] | None = Field(
            default=None, description="List of inbound relations"
        ),
        outbound_relations: list[dict] | None = Field(
            default=None, description="List of outbound relations"
        ),
        data_source_sys_id: str | None = Field(
            default=None, description="Sys_id of the data source record"
        ),
        records: list[dict] | None = Field(
            default=None, description="Array of objects to ingest"
        ),
        client=Depends(get_client),
        ctx: Context | None = Field(
            description="MCP context for progress reporting", default=None
        ),
    ) -> Response:
        """Action-Routed tool for 'cmdb'. Actions: 'get_cmdb', 'delete_cmdb_relation', 'get_cmdb_instances', 'get_cmdb_instance', 'create_cmdb_instance', 'update_cmdb_instance', 'patch_cmdb_instance', 'create_cmdb_relation', 'ingest_cmdb_data'"""
        if action == "get_cmdb":
            "\n        Fetches a specific Configuration Management Database (CMDB) record from a ServiceNow instance using its unique identifier.\n"
            return client.get_cmdb(cmdb_id=cmdb_id)
        if action == "delete_cmdb_relation":
            "\n        Deletes the relation for the specified configuration item (CI).\n"
            if not await ctx_confirm_destructive(ctx, "delete cmdb relation"):
                return {"status": "cancelled", "message": "Operation cancelled by user"}
            await ctx_progress(ctx, 0, 100)
            return client.delete_cmdb_relation(
                className=className, sys_id=sys_id, rel_sys_id=rel_sys_id
            )
        if action == "get_cmdb_instances":
            "\n        Returns the available configuration items (CI) for a specified CMDB class.\n"
            return client.get_cmdb_instances(
                className=className,
                sysparm_limit=sysparm_limit,
                sysparm_offset=sysparm_offset,
                sysparm_query=sysparm_query,
            )
        if action == "get_cmdb_instance":
            "\n        Returns attributes and relationship information for a specified CI record.\n"
            return client.get_cmdb_instance(className=className, sys_id=sys_id)
        if action == "create_cmdb_instance":
            "\n        Creates a single configuration item (CI).\n"
            return client.create_cmdb_instance(
                className=className,
                source=source,
                attributes=attributes,
                inbound_relations=inbound_relations,
                outbound_relations=outbound_relations,
            )
        if action == "update_cmdb_instance":
            "\n        Updates the specified CI record (PUT).\n"
            if ctx:
                message = f"Are you sure you want to UPDATE CI {sys_id} ({className}) with source {source}?"
                result = await ctx.elicit(message, response_type=bool)
                if result.action != "accept" or not result.data:
                    return "Operation cancelled by user."
            return client.update_cmdb_instance(
                className=className, sys_id=sys_id, source=source, attributes=attributes
            )
        if action == "patch_cmdb_instance":
            "\n        Replaces attributes in the specified CI record (PATCH).\n"
            if ctx:
                message = f"Are you sure you want to PATCH CI {sys_id} ({className}) with source {source}?"
                result = await ctx.elicit(message, response_type=bool)
                if result.action != "accept" or not result.data:
                    return "Operation cancelled by user."
            return client.patch_cmdb_instance(
                className=className, sys_id=sys_id, source=source, attributes=attributes
            )
        if action == "create_cmdb_relation":
            "\n        Adds an inbound and/or outbound relation to the specified CI.\n"
            return client.create_cmdb_relation(
                className=className,
                sys_id=sys_id,
                source=source,
                inbound_relations=inbound_relations,
                outbound_relations=outbound_relations,
            )
        if action == "ingest_cmdb_data":
            "\n        Inserts records into the Import Set table associated with the data source.\n"
            return client.ingest_cmdb_data(
                data_source_sys_id=data_source_sys_id, records=records
            )
        raise ValueError(f"Invalid action {action}")


def register_cicd_tools(mcp: FastMCP):

    @mcp.tool(tags={"cicd"})
    async def servicenow_cicd(
        action: str = Field(
            description="Action to perform. Must be one of: 'batch_install_result', 'instance_scan_progress', 'progress', 'batch_install', 'batch_rollback', 'app_repo_install', 'app_repo_publish', 'app_repo_rollback', 'full_scan', 'point_scan', 'combo_suite_scan', 'suite_scan'"
        ),
        result_id: str | None = Field(
            default=None,
            description="The ID associated with the batch installation result",
        ),
        progress_id: str | None = Field(
            default=None,
            description="The ID associated with the instance scan progress",
        ),
        name: str | None = Field(
            default=None, description="The name of the batch installation"
        ),
        packages: str | None = Field(
            default=None, description="The packages to be installed in the batch"
        ),
        notes: str | None = Field(
            default=None, description="Additional notes for the batch installation"
        ),
        rollback_id: str | None = Field(
            default=None, description="The ID associated with the batch rollback"
        ),
        app_sys_id: str | None = Field(
            default=None, description="The sys_id of the application to be installed"
        ),
        scope: str | None = Field(
            default=None, description="The scope of the application"
        ),
        auto_upgrade_base_app: bool | None = Field(
            default=None,
            description="Flag indicating whether to auto-upgrade the base app",
        ),
        base_app_version: str | None = Field(
            default=None, description="The version of the base app"
        ),
        version: str | None = Field(
            default=None, description="The version of the application to be installed"
        ),
        dev_notes: str | None = Field(
            default=None, description="Development notes for the published version"
        ),
        target_sys_id: str | None = Field(
            default=None, description="The sys_id of the target instance"
        ),
        target_table: str | None = Field(
            default=None, description="The table of the target instance"
        ),
        combo_sys_id: str | None = Field(
            default=None, description="The sys_id of the combo to be scanned"
        ),
        suite_sys_id: str | None = Field(
            default=None, description="The sys_id of the suite to be scanned"
        ),
        sys_ids: list[str] | None = Field(
            default=None,
            description="List of sys_ids representing app_scope_sys_ids for the suite scan",
        ),
        scan_type: str | None = Field(
            default="scoped_apps", description="Type of scan to be performed"
        ),
        client=Depends(get_client),
        ctx: Context | None = Field(
            description="MCP context for progress reporting", default=None
        ),
    ) -> Response:
        """Action-Routed tool for 'cicd'. Actions: 'batch_install_result', 'instance_scan_progress', 'progress', 'batch_install', 'batch_rollback', 'app_repo_install', 'app_repo_publish', 'app_repo_rollback', 'full_scan', 'point_scan', 'combo_suite_scan', 'suite_scan'"""
        if action == "batch_install_result":
            await ctx_progress(ctx, 0, 100)
            "\n        Retrieves the result of a batch installation process in ServiceNow by result ID.\n        "
            await ctx_progress(ctx, 100, 100)
            return client.batch_install_result(result_id=result_id)
        if action == "instance_scan_progress":
            "\n        Gets the progress status of an instance scan in ServiceNow by progress ID.\n"
            return client.instance_scan_progress(progress_id=progress_id)
        if action == "progress":
            "\n        Retrieves the progress status of a specified process in ServiceNow by progress ID.\n"
            return client.progress(progress_id=progress_id)
        if action == "batch_install":
            await ctx_progress(ctx, 0, 100)
            "\n        Initiates a batch installation of specified packages in ServiceNow with optional notes.\n        "
            await ctx_progress(ctx, 100, 100)
            return client.batch_install(name=name, packages=packages, notes=notes)
        if action == "batch_rollback":
            await ctx_progress(ctx, 0, 100)
            "\n        Performs a rollback of a batch installation in ServiceNow using the rollback ID.\n        "
            await ctx_progress(ctx, 100, 100)
            return client.batch_rollback(rollback_id=rollback_id)
        if action == "app_repo_install":
            "\n        Installs an application from a repository in ServiceNow with specified parameters.\n"
            return client.app_repo_install(
                app_sys_id=app_sys_id,
                scope=scope,
                auto_upgrade_base_app=auto_upgrade_base_app,
                base_app_version=base_app_version,
                version=version,
            )
        if action == "app_repo_publish":
            "\n        Publishes an application to a repository in ServiceNow with development notes and version.\n"
            return client.app_repo_publish(
                app_sys_id=app_sys_id, scope=scope, dev_notes=dev_notes, version=version
            )
        if action == "app_repo_rollback":
            "\n        Rolls back an application to a previous version in ServiceNow by sys_id, scope, and version.\n"
            return client.app_repo_rollback(
                app_sys_id=app_sys_id, scope=scope, version=version
            )
        if action == "full_scan":
            "\n        Initiates a full scan of the ServiceNow instance.\n"
            return client.full_scan()
        if action == "point_scan":
            "\n        Performs a targeted scan on a specific instance and table in ServiceNow.\n"
            return client.point_scan(
                target_sys_id=target_sys_id, target_table=target_table
            )
        if action == "combo_suite_scan":
            "\n        Executes a scan on a combination of suites in ServiceNow by combo sys_id.\n"
            return client.combo_suite_scan(combo_sys_id=combo_sys_id)
        if action == "suite_scan":
            "\n        Runs a scan on a specified suite with a list of sys_ids and scan type in ServiceNow.\n"
            return client.suite_scan(
                suite_sys_id=suite_sys_id, sys_ids=sys_ids, scan_type=scan_type
            )
        raise ValueError(f"Invalid action {action}")


def register_plugins_tools(mcp: FastMCP):

    @mcp.tool(tags={"plugins"})
    async def servicenow_plugins(
        action: str = Field(
            description="Action to perform. Must be one of: 'activate_plugin', 'rollback_plugin'"
        ),
        plugin_id: str | None = Field(
            default=None, description="The ID of the plugin to be activated"
        ),
        client=Depends(get_client),
        ctx: Context | None = Field(
            description="MCP context for progress reporting", default=None
        ),
    ) -> Response:
        """Action-Routed tool for 'plugins'. Actions: 'activate_plugin', 'rollback_plugin'"""
        if action == "activate_plugin":
            "\n        Activates a specified plugin in ServiceNow by plugin ID.\n"
            return client.activate_plugin(plugin_id=plugin_id)
        if action == "rollback_plugin":
            "\n        Rolls back a specified plugin in ServiceNow to its previous state by plugin ID.\n"
            return client.rollback_plugin(plugin_id=plugin_id)
        raise ValueError(f"Invalid action {action}")


def register_source_control_tools(mcp: FastMCP):

    @mcp.tool(tags={"source_control"})
    async def servicenow_source_control(
        action: str = Field(
            description="Action to perform. Must be one of: 'apply_remote_source_control_changes', 'import_repository'"
        ),
        app_sys_id: str | None = Field(
            default=None,
            description="The sys_id of the application for which changes should be applied",
        ),
        scope: str | None = Field(default=None, description="The scope of the changes"),
        branch_name: str | None = Field(
            default=None, description="The name of the branch containing the changes"
        ),
        auto_upgrade_base_app: bool | None = Field(
            default=None,
            description="Flag indicating whether to auto-upgrade the base app",
        ),
        repo_url: str | None = Field(
            default=None, description="The URL of the repository to be imported"
        ),
        credential_sys_id: str | None = Field(
            default=None,
            description="The sys_id of the credential to be used for the import",
        ),
        mid_server_sys_id: str | None = Field(
            default=None,
            description="The sys_id of the MID Server to be used for the import",
        ),
        client=Depends(get_client),
        ctx: Context | None = Field(
            description="MCP context for progress reporting", default=None
        ),
    ) -> Response:
        """Action-Routed tool for 'source_control'. Actions: 'apply_remote_source_control_changes', 'import_repository'"""
        if action == "apply_remote_source_control_changes":
            "\n        Applies changes from a remote source control branch to a ServiceNow application.\n"
            return client.apply_remote_source_control_changes(
                app_sys_id=app_sys_id,
                scope=scope,
                branch_name=branch_name,
                auto_upgrade_base_app=auto_upgrade_base_app,
            )
        if action == "import_repository":
            "\n        Imports a repository into ServiceNow with specified credentials and branch.\n"
            return client.import_repository(
                credential_sys_id=credential_sys_id,
                mid_server_sys_id=mid_server_sys_id,
                repo_url=repo_url,
                branch_name=branch_name,
                auto_upgrade_base_app=auto_upgrade_base_app,
            )
        raise ValueError(f"Invalid action {action}")


def register_testing_tools(mcp: FastMCP):

    @mcp.tool(tags={"testing"})
    async def run_test_suite(
        test_suite_sys_id: str = Field(
            description="The sys_id of the test suite to be run"
        ),
        test_suite_name: str = Field(
            description="The name of the test suite to be run"
        ),
        browser_name: str | None = Field(
            default=None, description="The name of the browser for the test run"
        ),
        browser_version: str | None = Field(
            default=None, description="The version of the browser for the test run"
        ),
        os_name: str | None = Field(
            default=None,
            description="The name of the operating system for the test run",
        ),
        os_version: str | None = Field(
            default=None,
            description="The version of the operating system for the test run",
        ),
        client=Depends(get_client),
        ctx: Context = Field(
            description="MCP context for progress reporting", default=None
        ),
    ) -> Response:
        await ctx_progress(ctx, 0, 100)
        "\n        Executes a test suite in ServiceNow with specified browser and OS configurations.\n        "
        await ctx_progress(ctx, 100, 100)
        return client.run_test_suite(
            test_suite_sys_id=test_suite_sys_id,
            test_suite_name=test_suite_name,
            browser_name=browser_name,
            browser_version=browser_version,
            os_name=os_name,
            os_version=os_version,
        )


def register_update_sets_tools(mcp: FastMCP):

    @mcp.tool(tags={"update_sets"})
    async def servicenow_update_sets(
        action: str = Field(
            description="Action to perform. Must be one of: 'update_set_create', 'update_set_retrieve', 'update_set_preview', 'update_set_commit', 'update_set_commit_multiple', 'update_set_back_out'"
        ),
        update_set_name: str | None = Field(
            default=None, description="Name to give the update set"
        ),
        scope: str | None = Field(
            default=None,
            description="The scope name of the application in which to create the new update set",
        ),
        sys_id: str | None = Field(
            default=None,
            description="Sys_id of the application in which to create the new update set",
        ),
        description: str | None = Field(
            default=None, description="Description of the update set"
        ),
        update_set_id: str | None = Field(
            default=None,
            description="Sys_id of the update set on the source instance from where the update set was retrieved",
        ),
        update_source_id: str | None = Field(
            default=None, description="Sys_id of the remote instance record"
        ),
        update_source_instance_id: str | None = Field(
            default=None, description="Instance ID of the remote instance"
        ),
        auto_preview: bool | None = Field(
            default=None,
            description="Flag that indicates whether to automatically preview the update set after retrieval",
        ),
        cleanup_retrieved: bool | None = Field(
            default=None,
            description="Flag that indicates whether to remove the existing retrieved update set from the instance",
        ),
        remote_update_set_id: str | None = Field(
            default=None, description="Sys_id of the update set to preview"
        ),
        force_commit: str | None = Field(
            default=None,
            description="Flag that indicates whether to force commit the update set",
        ),
        remote_update_set_ids: list[str] | None = Field(
            default=None,
            description="List of sys_ids associated with update sets to commit. Sys_ids are committed in the order given",
        ),
        rollback_installs: bool | None = Field(
            default=None,
            description="Flag that indicates whether to rollback the batch installation performed during the update set commit",
        ),
        client=Depends(get_client),
        ctx: Context | None = Field(
            description="MCP context for progress reporting", default=None
        ),
    ) -> Response:
        """Action-Routed tool for 'update_sets'. Actions: 'update_set_create', 'update_set_retrieve', 'update_set_preview', 'update_set_commit', 'update_set_commit_multiple', 'update_set_back_out'"""
        if action == "update_set_create":
            "\n        Creates a new update set in ServiceNow with a given name, scope, and description.\n"
            return client.update_set_create(
                update_set_name=update_set_name,
                description=description,
                scope=scope,
                sys_id=sys_id,
            )
        if action == "update_set_retrieve":
            "\n        Retrieves an update set from a source instance in ServiceNow with optional preview and cleanup.\n"
            return client.update_set_retrieve(
                update_set_id=update_set_id,
                update_source_id=update_source_id,
                update_source_instance_id=update_source_instance_id,
                auto_preview=auto_preview,
                cleanup_retrieved=cleanup_retrieved,
            )
        if action == "update_set_preview":
            "\n        Previews an update set in ServiceNow by its remote sys_id.\n"
            return client.update_set_preview(remote_update_set_id=remote_update_set_id)
        if action == "update_set_commit":
            "\n        Commits an update set in ServiceNow with an option to force commit.\n"
            return client.update_set_commit(
                remote_update_set_id=remote_update_set_id, force_commit=force_commit
            )
        if action == "update_set_commit_multiple":
            "\n        Commits multiple update sets in ServiceNow in the specified order.\n"
            return client.update_set_commit_multiple(
                remote_update_set_ids=remote_update_set_ids, force_commit=force_commit
            )
        if action == "update_set_back_out":
            "\n        Backs out an update set in ServiceNow with an option to rollback installations.\n"
            return client.update_set_back_out(
                update_set_id=update_set_id, rollback_installs=rollback_installs
            )
        raise ValueError(f"Invalid action {action}")


def register_batch_tools(mcp: FastMCP):

    @mcp.tool(tags={"batch"})
    async def batch_request(
        rest_requests: list[dict] = Field(
            description="List of requests to execute. Each item must correspond to BatchRequestItem model."
        ),
        batch_request_id: str | None = Field(
            default=None, description="Client provided batch ID"
        ),
        client=Depends(get_client),
        ctx: Context = Field(
            description="MCP context for progress reporting", default=None
        ),
    ) -> Response:
        await ctx_progress(ctx, 0, 100)
        "\n        Sends multiple REST API requests in a single call.\n        "
        await ctx_progress(ctx, 100, 100)
        return client.batch_request(
            batch_request_id=batch_request_id, rest_requests=rest_requests
        )


def register_change_management_tools(mcp: FastMCP):

    @mcp.tool(tags={"change_management"})
    async def servicenow_change_management(
        action: str = Field(
            description="Action to perform. Must be one of: 'get_change_requests', 'get_change_request_nextstate', 'get_change_request_schedule', 'get_change_request_tasks', 'get_change_request', 'get_change_request_ci', 'get_change_request_conflict', 'get_standard_change_request_templates', 'get_change_request_models', 'get_standard_change_request_model', 'get_standard_change_request_template', 'get_change_request_worker', 'create_change_request', 'create_change_request_task', 'create_change_request_ci_association', 'calculate_standard_change_request_risk', 'check_change_request_conflict', 'refresh_change_request_impacted_services', 'approve_change_request', 'update_change_request', 'update_change_request_first_available', 'update_change_request_task', 'delete_change_request', 'delete_change_request_task', 'delete_change_request_conflict_scan'"
        ),
        order: str | None = Field(
            default=None, description="Ordering parameter for sorting results"
        ),
        name_value_pairs: str | None = Field(
            default=None,
            description="Dictionary of name-value pairs for filtering records entered as a string",
        ),
        sysparm_query: str | None = Field(
            default=None, description="Query parameter for filtering results"
        ),
        text_search: str | None = Field(
            default=None, description="Text search parameter for searching results"
        ),
        change_type: str | None = Field(
            default=None,
            description="Type of change (emergency, normal, standard, model)",
        ),
        sysparm_offset: int | None = Field(
            default=None, description="Offset for pagination"
        ),
        sysparm_limit: int | None = Field(
            default=os.environ.get("SERVICENOW_RETURN_LIMIT", to_integer(string="5")),
            description="Limit for pagination",
        ),
        change_request_sys_id: str | None = Field(
            default=None, description="Sys ID of the change request"
        ),
        cmdb_ci_sys_id: str | None = Field(
            default=None, description="Sys ID of the CI (Configuration Item)"
        ),
        change_request_id: str | None = Field(
            default=None,
            description="Sys ID or change number (CHG#####) of the change request",
        ),
        sysparm_display_value: str | None = Field(
            default=None,
            description="Display values for reference fields ('true', 'false', or 'all')",
        ),
        sysparm_exclude_reference_link: bool | None = Field(
            default=None, description="Exclude reference links in the response"
        ),
        sysparm_fields: str | None = Field(
            default=None,
            description="Comma-separated list of field names to include in the response",
        ),
        sysparm_no_count: bool | None = Field(
            default=None,
            description="Do not include the total number of records in the response",
        ),
        sysparm_query_category: str | None = Field(
            default=None, description="Category to which the query belongs"
        ),
        sysparm_query_no_domain: bool | None = Field(
            default=None, description="Exclude records based on domain separation"
        ),
        sysparm_suppress_pagination_header: bool | None = Field(
            default=None, description="Suppress pagination headers in the response"
        ),
        sysparm_view: str | None = Field(
            default=None, description="Display style ('desktop', 'mobile', or 'both')"
        ),
        model_sys_id: str | None = Field(
            default=None, description="Sys ID of the standard change request model"
        ),
        template_sys_id: str | None = Field(
            default=None, description="Sys ID of the standard change request template"
        ),
        worker_sys_id: str | None = Field(
            default=None, description="Sys ID of the change request worker"
        ),
        standard_change_template_id: str | None = Field(
            default=None,
            description="Sys ID of the standard change request template (if applicable)",
        ),
        data: dict[str, str] | None = Field(
            default=None,
            description="Name-value pairs providing details for the new task",
        ),
        cmdb_ci_sys_ids: list[str] | None = Field(
            default=None,
            description="List of Sys IDs of CIs to associate with the change request",
        ),
        association_type: str | None = Field(
            default=None,
            description="Type of association (affected, impacted, offering)",
        ),
        refresh_impacted_services: bool | None = Field(
            default=None,
            description="Flag to refresh impacted services (applicable for 'affected' association)",
        ),
        state: str | None = Field(
            default=None,
            description="State to set the change request to (approved or rejected)",
        ),
        change_request_task_sys_id: str | None = Field(
            default=None, description="Sys ID of the change request task"
        ),
        task_sys_id: str | None = Field(
            default=None,
            description="Sys ID of the task associated with the change request",
        ),
        client=Depends(get_client),
        ctx: Context | None = Field(
            description="MCP context for progress reporting", default=None
        ),
    ) -> Response:
        """Action-Routed tool for 'change_management'. Actions: 'get_change_requests', 'get_change_request_nextstate', 'get_change_request_schedule', 'get_change_request_tasks', 'get_change_request', 'get_change_request_ci', 'get_change_request_conflict', 'get_standard_change_request_templates', 'get_change_request_models', 'get_standard_change_request_model', 'get_standard_change_request_template', 'get_change_request_worker', 'create_change_request', 'create_change_request_task', 'create_change_request_ci_association', 'calculate_standard_change_request_risk', 'check_change_request_conflict', 'refresh_change_request_impacted_services', 'approve_change_request', 'update_change_request', 'update_change_request_first_available', 'update_change_request_task', 'delete_change_request', 'delete_change_request_task', 'delete_change_request_conflict_scan'"""
        if action == "get_change_requests":
            "\n        Retrieves change requests from ServiceNow with optional filtering and pagination.\n"
            logging.info("Getting Change Requests...")
            return client.get_change_requests(
                order=order,
                name_value_pairs=name_value_pairs,
                sysparm_query=sysparm_query,
                text_search=text_search,
                change_type=change_type,
                sysparm_offset=sysparm_offset,
                sysparm_limit=sysparm_limit,
            )
        if action == "get_change_request_nextstate":
            "\n        Gets the next state for a specific change request in ServiceNow.\n"
            return client.get_change_request_nextstate(
                change_request_sys_id=change_request_sys_id
            )
        if action == "get_change_request_schedule":
            "\n        Retrieves the schedule for a change request based on a Configuration Item (CI) in ServiceNow.\n"
            return client.get_change_request_schedule(cmdb_ci_sys_id=cmdb_ci_sys_id)
        if action == "get_change_request_tasks":
            "\n        Fetches tasks associated with a change request in ServiceNow with optional filtering.\n"
            return client.get_change_request_tasks(
                change_request_sys_id=change_request_sys_id,
                order=order,
                name_value_pairs=name_value_pairs,
                sysparm_query=sysparm_query,
                text_search=text_search,
                sysparm_offset=sysparm_offset,
                sysparm_limit=sysparm_limit,
            )
        if action == "get_change_request":
            "\n        Retrieves details of a specific change request in ServiceNow by sys_id and type.\n"
            if change_request_id:
                if (
                    change_request_id.upper().startswith("CHG")
                    and len(change_request_id) < 32
                ):
                    logging.info(
                        f"Treating change_id='{change_request_id}' as number query"
                    )
                    sysparm_query = f"number={change_request_id}"
                    change_request_id = None
                else:
                    logging.info("Getting Change by sys_id...")
                    return client.get_change_request(
                        change_request_sys_id=change_request_id, change_type=change_type
                    )
            if not change_request_id:
                logging.info("Getting Changes via query...")
                return client.get_change_requests(
                    name_value_pairs=name_value_pairs,
                    sysparm_display_value=sysparm_display_value,
                    sysparm_exclude_reference_link=sysparm_exclude_reference_link,
                    sysparm_fields=sysparm_fields,
                    sysparm_limit=sysparm_limit,
                    sysparm_no_count=sysparm_no_count,
                    sysparm_offset=sysparm_offset,
                    sysparm_query=sysparm_query,
                    sysparm_query_category=sysparm_query_category,
                    sysparm_query_no_domain=sysparm_query_no_domain,
                    sysparm_suppress_pagination_header=sysparm_suppress_pagination_header,
                    sysparm_view=sysparm_view,
                )
        if action == "get_change_request_ci":
            "\n        Gets Configuration Items (CIs) associated with a change request in ServiceNow.\n"
            return client.get_change_request_ci(
                change_request_sys_id=change_request_sys_id
            )
        if action == "get_change_request_conflict":
            "\n        Checks for conflicts in a change request in ServiceNow.\n"
            return client.get_change_request_conflict(
                change_request_sys_id=change_request_sys_id
            )
        if action == "get_standard_change_request_templates":
            "\n        Retrieves standard change request templates from ServiceNow with optional filtering.\n"
            return client.get_standard_change_request_templates(
                order=order,
                name_value_pairs=name_value_pairs,
                sysparm_query=sysparm_query,
                text_search=text_search,
                sysparm_offset=sysparm_offset,
                sysparm_limit=sysparm_limit,
            )
        if action == "get_change_request_models":
            "\n        Fetches change request models from ServiceNow with optional filtering and type.\n"
            return client.get_change_request_models(
                order=order,
                name_value_pairs=name_value_pairs,
                sysparm_query=sysparm_query,
                text_search=text_search,
                change_type=change_type,
                sysparm_offset=sysparm_offset,
                sysparm_limit=sysparm_limit,
            )
        if action == "get_standard_change_request_model":
            "\n        Retrieves a specific standard change request model in ServiceNow by sys_id.\n"
            return client.get_standard_change_request_model(model_sys_id=model_sys_id)
        if action == "get_standard_change_request_template":
            "\n        Gets a specific standard change request template in ServiceNow by sys_id.\n"
            return client.get_standard_change_request_template(
                template_sys_id=template_sys_id
            )
        if action == "get_change_request_worker":
            "\n        Retrieves details of a change request worker in ServiceNow by sys_id.\n"
            return client.get_change_request_worker(worker_sys_id=worker_sys_id)
        if action == "create_change_request":
            "\n        Creates a new change request in ServiceNow with specified details and type.\n"
            return client.create_change_request(
                name_value_pairs=name_value_pairs,
                change_type=change_type,
                standard_change_template_id=standard_change_template_id,
            )
        if action == "create_change_request_task":
            "\n        Creates a task for a change request in ServiceNow with provided details.\n"
            return client.create_change_request_task(
                change_request_sys_id=change_request_sys_id, data=data
            )
        if action == "create_change_request_ci_association":
            "\n        Associates Configuration Items (CIs) with a change request in ServiceNow.\n"
            return client.create_change_request_ci_association(
                change_request_sys_id=change_request_sys_id,
                cmdb_ci_sys_ids=cmdb_ci_sys_ids,
                association_type=association_type,
                refresh_impacted_services=refresh_impacted_services,
            )
        if action == "calculate_standard_change_request_risk":
            "\n        Calculates the risk for a standard change request in ServiceNow.\n"
            return client.calculate_standard_change_request_risk(
                change_request_sys_id=change_request_sys_id
            )
        if action == "check_change_request_conflict":
            "\n        Checks for conflicts in a change request in ServiceNow.\n"
            return client.check_change_request_conflict(
                change_request_sys_id=change_request_sys_id
            )
        if action == "refresh_change_request_impacted_services":
            "\n        Refreshes the impacted services for a change request in ServiceNow.\n"
            return client.refresh_change_request_impacted_services(
                change_request_sys_id=change_request_sys_id
            )
        if action == "approve_change_request":
            "\n        Approves or rejects a change request in ServiceNow by setting its state.\n"
            return client.approve_change_request(
                change_request_sys_id=change_request_sys_id, state=state
            )
        if action == "update_change_request":
            "\n        Updates a change request in ServiceNow with new details and type.\n"
            return client.update_change_request(
                change_request_sys_id=change_request_sys_id,
                name_value_pairs=name_value_pairs,
                change_type=change_type,
            )
        if action == "update_change_request_first_available":
            "\n        Updates a change request to the first available state in ServiceNow.\n"
            return client.update_change_request_first_available(
                change_request_sys_id=change_request_sys_id
            )
        if action == "update_change_request_task":
            "\n        Updates a task for a change request in ServiceNow with new details.\n"
            return client.update_change_request_task(
                change_request_sys_id=change_request_sys_id,
                change_request_task_sys_id=change_request_task_sys_id,
                name_value_pairs=name_value_pairs,
            )
        if action == "delete_change_request":
            "\n        Deletes a change request from ServiceNow by sys_id and type.\n"
            if not await ctx_confirm_destructive(ctx, "delete change request"):
                return {"status": "cancelled", "message": "Operation cancelled by user"}
            await ctx_progress(ctx, 0, 100)
            return client.delete_change_request(
                change_request_sys_id=change_request_sys_id, change_type=change_type
            )
        if action == "delete_change_request_task":
            "\n        Deletes a task associated with a change request in ServiceNow.\n"
            if not await ctx_confirm_destructive(ctx, "delete change request task"):
                return {"status": "cancelled", "message": "Operation cancelled by user"}
            await ctx_progress(ctx, 0, 100)
            return client.delete_change_request_task(
                change_request_sys_id=change_request_sys_id, task_sys_id=task_sys_id
            )
        if action == "delete_change_request_conflict_scan":
            "\n        Deletes a conflict scan for a change request in ServiceNow.\n"
            if not await ctx_confirm_destructive(
                ctx, "delete change request conflict scan"
            ):
                return {"status": "cancelled", "message": "Operation cancelled by user"}
            await ctx_progress(ctx, 0, 100)
            return client.delete_change_request_conflict_scan(
                change_request_sys_id=change_request_sys_id, task_sys_id=task_sys_id
            )
        raise ValueError(f"Invalid action {action}")


def register_cilifecycle_tools(mcp: FastMCP):

    @mcp.tool(tags={"cilifecycle"})
    async def servicenow_cilifecycle(
        action: str = Field(
            description="Action to perform. Must be one of: 'check_ci_lifecycle_compat_actions', 'register_ci_lifecycle_operator', 'unregister_ci_lifecycle_operator'"
        ),
        actionName: str | None = Field(
            default=None, description="Name of the CI action"
        ),
        otherActionName: str | None = Field(
            default=None, description="Name of the other CI action"
        ),
        req_id: str | None = Field(
            default=None, description="Request ID needed to unregister"
        ),
        client=Depends(get_client),
        ctx: Context | None = Field(
            description="MCP context for progress reporting", default=None
        ),
    ) -> Response:
        """Action-Routed tool for 'cilifecycle'. Actions: 'check_ci_lifecycle_compat_actions', 'register_ci_lifecycle_operator', 'unregister_ci_lifecycle_operator'"""
        if action == "check_ci_lifecycle_compat_actions":
            "\n        Determines whether two specified CI actions are compatible.\n"
            return client.check_ci_lifecycle_compat_actions(
                actionName=actionName, otherActionName=otherActionName
            )
        if action == "register_ci_lifecycle_operator":
            "\n        Registers an operator for a non-workflow user.\n"
            return client.register_ci_lifecycle_operator()
        if action == "unregister_ci_lifecycle_operator":
            "\n        Unregisters an operator for non-workflow users.\n"
            return client.unregister_ci_lifecycle_operator(req_id=req_id)
        raise ValueError(f"Invalid action {action}")


def register_devops_tools(mcp: FastMCP):

    @mcp.tool(tags={"devops"})
    async def servicenow_devops(
        action: str = Field(
            description="Action to perform. Must be one of: 'check_devops_change_control', 'register_devops_artifact'"
        ),
        toolId: str | None = Field(default=None, description="Tool ID"),
        orchestrationTaskName: str | None = Field(
            default=None, description="Orchestration Task Name"
        ),
        toolType: str | None = Field(default="jenkins", description="Tool Type"),
        orchestrationTaskURL: str | None = Field(
            default=None, description="Orchestration Task URL"
        ),
        testConnection: bool | None = Field(
            default=None, description="Test Connection"
        ),
        artifacts: list[dict] | None = Field(
            default=None, description="List of artifacts to register"
        ),
        orchestrationToolId: str | None = Field(
            default=None, description="Orchestration Tool ID"
        ),
        branchName: str | None = Field(default=None, description="Branch Name"),
        pipelineName: str | None = Field(default=None, description="Pipeline Name"),
        projectName: str | None = Field(default=None, description="Project Name"),
        stageName: str | None = Field(default=None, description="Stage Name"),
        taskExecutionNumber: str | None = Field(
            default=None, description="Task Execution Number"
        ),
        client=Depends(get_client),
        ctx: Context | None = Field(
            description="MCP context for progress reporting", default=None
        ),
    ) -> Response:
        """Action-Routed tool for 'devops'. Actions: 'check_devops_change_control', 'register_devops_artifact'"""
        if action == "check_devops_change_control":
            "\n        Checks if the orchestration task is under change control.\n"
            return client.check_devops_change_control(
                toolId=toolId,
                orchestrationTaskName=orchestrationTaskName,
                toolType=toolType,
                orchestrationTaskURL=orchestrationTaskURL,
                testConnection=testConnection,
            )
        if action == "register_devops_artifact":
            "\n        Enables orchestration tools to register artifacts into a ServiceNow instance.\n"
            return client.register_devops_artifact(
                artifacts=artifacts,
                orchestrationToolId=orchestrationToolId,
                toolId=toolId,
                branchName=branchName,
                pipelineName=pipelineName,
                projectName=projectName,
                stageName=stageName,
                taskExecutionNumber=taskExecutionNumber,
            )
        raise ValueError(f"Invalid action {action}")


def register_import_sets_tools(mcp: FastMCP):

    @mcp.tool(tags={"import_sets"})
    async def servicenow_import_sets(
        action: str = Field(
            description="Action to perform. Must be one of: 'get_import_set', 'insert_import_set', 'insert_multiple_import_sets'"
        ),
        table: str | None = Field(
            default=None,
            description="The name of the table associated with the import set",
        ),
        import_set_sys_id: str | None = Field(
            default=None, description="The sys_id of the import set record"
        ),
        data: dict[str, str] | None = Field(
            default=None,
            description="Dictionary containing the field values for the new import set record",
        ),
        client=Depends(get_client),
        ctx: Context | None = Field(
            description="MCP context for progress reporting", default=None
        ),
    ) -> Response:
        """Action-Routed tool for 'import_sets'. Actions: 'get_import_set', 'insert_import_set', 'insert_multiple_import_sets'"""
        if action == "get_import_set":
            "\n        Retrieves details of a specific import set record from a ServiceNow instance.\n"
            return client.get_import_set(
                table=table, import_set_sys_id=import_set_sys_id
            )
        if action == "insert_import_set":
            "\n        Inserts a new record into a specified import set on a ServiceNow instance.\n"
            return client.insert_import_set(table=table, data=data)
        if action == "insert_multiple_import_sets":
            "\n        Inserts multiple records into a specified import set on a ServiceNow instance.\n"
            return client.insert_multiple_import_sets(table=table, data=data)
        raise ValueError(f"Invalid action {action}")


def register_incidents_tools(mcp: FastMCP):

    @mcp.tool(tags={"incidents"})
    async def servicenow_incidents(
        action: str = Field(
            description="Action to perform. Must be one of: 'get_incidents', 'create_incident'"
        ),
        incident_id: str | None = Field(
            default=None,
            description="The sys_id or the incident number (INC######) of the incident record, if retrieving a specific incident",
        ),
        name_value_pairs: str | None = Field(
            default=None,
            description="Dictionary of name-value pairs for filtering records entered as a string",
        ),
        sysparm_display_value: str | None = Field(
            default=None,
            description="Display values for reference fields ('true', 'false', or 'all')",
        ),
        sysparm_exclude_reference_link: bool | None = Field(
            default=None, description="Exclude reference links in the response"
        ),
        sysparm_fields: str | None = Field(
            default=None,
            description="Comma-separated list of field names to include in the response",
        ),
        sysparm_limit: int | None = Field(
            default=os.environ.get("SERVICENOW_RETURN_LIMIT", to_integer(string="5")),
            description="Maximum number of records to return",
        ),
        sysparm_no_count: bool | None = Field(
            default=None,
            description="Do not include the total number of records in the response",
        ),
        sysparm_offset: int | None = Field(
            default=None,
            description="Number of records to skip before starting the retrieval",
        ),
        sysparm_query: str | None = Field(
            default=None, description="Encoded query string for filtering records"
        ),
        sysparm_query_category: str | None = Field(
            default=None, description="Category to which the query belongs"
        ),
        sysparm_query_no_domain: bool | None = Field(
            default=None, description="Exclude records based on domain separation"
        ),
        sysparm_suppress_pagination_header: bool | None = Field(
            default=None, description="Suppress pagination headers in the response"
        ),
        sysparm_view: str | None = Field(
            default=None, description="Display style ('desktop', 'mobile', or 'both')"
        ),
        data: dict[str, str] | None = Field(
            default=None,
            description="Dictionary containing the field values for the new incident record",
        ),
        client=Depends(get_client),
        ctx: Context | None = Field(
            description="MCP context for progress reporting", default=None
        ),
    ) -> Response:
        """Action-Routed tool for 'incidents'. Actions: 'get_incidents', 'create_incident'"""
        if action == "get_incidents":
            "\n        Retrieves incident records from a ServiceNow instance, optionally by specific incident ID.\n"
            if incident_id:
                if incident_id.upper().startswith("INC") and len(incident_id) < 32:
                    logging.info(
                        f"Treating incident_id='{incident_id}' as number query"
                    )
                    sysparm_query = f"number={incident_id}"
                    incident_id = None
                else:
                    logging.info("Getting Incident by sys_id...")
                    return client.get_incident(incident_id=incident_id)
            if not incident_id:
                logging.info("Getting Incidents via query...")
                return client.get_incidents(
                    name_value_pairs=name_value_pairs,
                    sysparm_display_value=sysparm_display_value,
                    sysparm_exclude_reference_link=sysparm_exclude_reference_link,
                    sysparm_fields=sysparm_fields,
                    sysparm_limit=sysparm_limit,
                    sysparm_no_count=sysparm_no_count,
                    sysparm_offset=sysparm_offset,
                    sysparm_query=sysparm_query,
                    sysparm_query_category=sysparm_query_category,
                    sysparm_query_no_domain=sysparm_query_no_domain,
                    sysparm_suppress_pagination_header=sysparm_suppress_pagination_header,
                    sysparm_view=sysparm_view,
                )
        if action == "create_incident":
            "\n        Creates a new incident record on a ServiceNow instance with provided details.\n"
            return client.create_incident(data=data)
        raise ValueError(f"Invalid action {action}")


def register_knowledge_management_tools(mcp: FastMCP):

    @mcp.tool(tags={"knowledge_management"})
    async def servicenow_knowledge_management(
        action: str = Field(
            description="Action to perform. Must be one of: 'get_knowledge_articles', 'get_knowledge_article', 'get_knowledge_article_attachment', 'get_featured_knowledge_article', 'get_most_viewed_knowledge_articles'"
        ),
        filter: str | None = Field(
            default=None,
            description="Encoded query to filter the result set (e.g., =, !=, ^, ^OR, LIKE, STARTSWITH, ENDSWITH)",
        ),
        sysparm_fields: str | None = Field(
            default=None,
            description="Comma-separated list of field names to include in the response",
        ),
        sysparm_limit: int | None = Field(
            default=os.environ.get("SERVICENOW_RETURN_LIMIT", to_integer(string="5")),
            description="Maximum number of records to return",
        ),
        sysparm_offset: int | None = Field(
            default=None,
            description="Number of records to skip before starting the retrieval",
        ),
        sysparm_query: str | None = Field(
            default=None, description="Encoded query string for filtering records"
        ),
        sysparm_query_category: str | None = Field(
            default=None, description="Category to which the query belongs"
        ),
        kb: str | None = Field(
            default=None,
            description="Comma-separated list of knowledge base sys_ids to restrict results to",
        ),
        language: str | None = Field(
            default=None,
            description="Comma-separated languages in ISO 639-1 format or 'all' to search all valid languages",
        ),
        article_sys_id: str | None = Field(
            default=None, description="The sys_id of the Knowledge Base article"
        ),
        sysparm_search_id: str | None = Field(
            default=None,
            description="Unique identifier of search that returned this article",
        ),
        sysparm_search_rank: str | None = Field(
            default=None, description="Article search rank by click-rate"
        ),
        sysparm_update_view: bool | None = Field(
            default=None,
            description="Update view count and record an entry in the Knowledge Use table",
        ),
        attachment_sys_id: str | None = Field(
            default=None, description="The sys_id of the attachment"
        ),
        client=Depends(get_client),
        ctx: Context | None = Field(
            description="MCP context for progress reporting", default=None
        ),
    ) -> Response:
        """Action-Routed tool for 'knowledge_management'. Actions: 'get_knowledge_articles', 'get_knowledge_article', 'get_knowledge_article_attachment', 'get_featured_knowledge_article', 'get_most_viewed_knowledge_articles'"""
        if action == "get_knowledge_articles":
            "\n        Get all Knowledge Base articles from a ServiceNow instance.\n"
            return client.get_knowledge_articles(
                filter=filter,
                sysparm_fields=sysparm_fields,
                sysparm_limit=sysparm_limit,
                sysparm_offset=sysparm_offset,
                sysparm_query=sysparm_query,
                sysparm_query_category=sysparm_query_category,
                kb=kb,
                language=language,
            )
        if action == "get_knowledge_article":
            "\n        Get a specific Knowledge Base article from a ServiceNow instance.\n"
            return client.get_knowledge_article(
                article_sys_id=article_sys_id,
                filter=filter,
                sysparm_fields=sysparm_fields,
                sysparm_limit=sysparm_limit,
                sysparm_search_id=sysparm_search_id,
                sysparm_search_rank=sysparm_search_rank,
                sysparm_update_view=sysparm_update_view,
                sysparm_offset=sysparm_offset,
                sysparm_query=sysparm_query,
                sysparm_query_category=sysparm_query_category,
                kb=kb,
                language=language,
            )
        if action == "get_knowledge_article_attachment":
            "\n        Get a Knowledge Base article attachment from a ServiceNow instance.\n"
            return client.get_knowledge_article_attachment(
                article_sys_id=article_sys_id, attachment_sys_id=attachment_sys_id
            )
        if action == "get_featured_knowledge_article":
            "\n        Get featured Knowledge Base articles from a ServiceNow instance.\n"
            return client.get_featured_knowledge_article(
                sysparm_fields=sysparm_fields,
                sysparm_limit=sysparm_limit,
                sysparm_offset=sysparm_offset,
                kb=kb,
                language=language,
            )
        if action == "get_most_viewed_knowledge_articles":
            "\n        Get most viewed Knowledge Base articles from a ServiceNow instance.\n"
            return client.get_most_viewed_knowledge_articles(
                sysparm_fields=sysparm_fields,
                sysparm_limit=sysparm_limit,
                sysparm_offset=sysparm_offset,
                kb=kb,
                language=language,
            )
        raise ValueError(f"Invalid action {action}")


def register_table_api_tools(mcp: FastMCP):

    @mcp.tool(tags={"table_api"})
    async def servicenow_table_api(
        action: str = Field(
            description="Action to perform. Must be one of: 'delete_table_record', 'get_table', 'get_table_record', 'patch_table_record', 'update_table_record', 'add_table_record'"
        ),
        table: str | None = Field(default=None, description="The name of the table"),
        table_record_sys_id: str | None = Field(
            default=None, description="The sys_id of the record to be deleted"
        ),
        name_value_pairs: str | None = Field(
            default=None,
            description="Dictionary of name-value pairs for filtering records entered as a string",
        ),
        sysparm_display_value: str | None = Field(
            default=None,
            description="Display values for reference fields ('true', 'false', or 'all')",
        ),
        sysparm_exclude_reference_link: bool | None = Field(
            default=None, description="Exclude reference links in the response"
        ),
        sysparm_fields: str | None = Field(
            default=None,
            description="Comma-separated list of field names to include in the response",
        ),
        sysparm_limit: int | None = Field(
            default=os.environ.get("SERVICENOW_RETURN_LIMIT", to_integer(string="5")),
            description="Maximum number of records to return",
        ),
        sysparm_no_count: bool | None = Field(
            default=None,
            description="Do not include the total number of records in the response",
        ),
        sysparm_offset: int | None = Field(
            default=None,
            description="Number of records to skip before starting the retrieval",
        ),
        sysparm_query: str | None = Field(
            default=None, description="Encoded query string for filtering records"
        ),
        sysparm_query_category: str | None = Field(
            default=None, description="Category to which the query belongs"
        ),
        sysparm_query_no_domain: bool | None = Field(
            default=None, description="Exclude records based on domain separation"
        ),
        sysparm_suppress_pagination_header: bool | None = Field(
            default=None, description="Suppress pagination headers in the response"
        ),
        sysparm_view: str | None = Field(
            default=None, description="Display style ('desktop', 'mobile', or 'both')"
        ),
        data: dict[str, Any] = Field(
            default=None, description="Dictionary containing the fields to be updated"
        ),
        client=Depends(get_client),
        ctx: Context | None = Field(
            description="MCP context for progress reporting", default=None
        ),
    ) -> Response:
        """Action-Routed tool for 'table_api'. Actions: 'delete_table_record', 'get_table', 'get_table_record', 'patch_table_record', 'update_table_record', 'add_table_record'"""
        if action == "delete_table_record":
            "\n        Delete a record from the specified table on a ServiceNow instance.\n"
            if not await ctx_confirm_destructive(ctx, "delete table record"):
                return {"status": "cancelled", "message": "Operation cancelled by user"}
            await ctx_progress(ctx, 0, 100)
            return client.delete_table_record(
                table=table, table_record_sys_id=table_record_sys_id
            )
        if action == "get_table":
            "\n        Get records from the specified table on a ServiceNow instance.\n"
            return client.get_table(
                table=table,
                name_value_pairs=name_value_pairs,
                sysparm_display_value=sysparm_display_value,
                sysparm_exclude_reference_link=sysparm_exclude_reference_link,
                sysparm_fields=sysparm_fields,
                sysparm_limit=sysparm_limit,
                sysparm_no_count=sysparm_no_count,
                sysparm_offset=sysparm_offset,
                sysparm_query=sysparm_query,
                sysparm_query_category=sysparm_query_category,
                sysparm_query_no_domain=sysparm_query_no_domain,
                sysparm_suppress_pagination_header=sysparm_suppress_pagination_header,
                sysparm_view=sysparm_view,
            )
        if action == "get_table_record":
            "\n        Get a specific record from the specified table on a ServiceNow instance.\n"
            return client.get_table_record(
                table=table, table_record_sys_id=table_record_sys_id
            )
        if action == "patch_table_record":
            "\n        Partially update a record in the specified table on a ServiceNow instance.\n"
            return client.patch_table_record(
                table=table, table_record_sys_id=table_record_sys_id, data=data
            )
        if action == "update_table_record":
            "\n        Fully update a record in the specified table on a ServiceNow instance.\n"
            return client.update_table_record(
                table=table, table_record_sys_id=table_record_sys_id, data=data
            )
        if action == "add_table_record":
            "\n        Add a new record to the specified table on a ServiceNow instance.\n"
            return client.add_table_record(table=table, data=data)
        raise ValueError(f"Invalid action {action}")


def register_auth_tools(mcp: FastMCP):

    @mcp.tool(tags={"auth"})
    async def refresh_auth_token(
        client=Depends(get_client),
        ctx: Context = Field(
            description="MCP context for progress reporting", default=None
        ),
    ) -> Response:
        """
        Refreshes the authentication token for the ServiceNow client.
        """
        return client.refresh_auth_token()


def register_custom_api_tools(mcp: FastMCP):

    @mcp.tool(tags={"custom_api"})
    async def api_request(
        method: str = Field(
            description="The HTTP method to use ('GET', 'POST', 'PUT', 'DELETE')"
        ),
        endpoint: str = Field(description="The API endpoint to send the request to"),
        data: dict[str, Any] | None = Field(
            default=None,
            description="Data to include in the request body (for non-JSON payloads)",
        ),
        json: dict[str, Any] | None = Field(
            default=None, description="JSON data to include in the request body"
        ),
        client=Depends(get_client),
        ctx: Context = Field(
            description="MCP context for progress reporting", default=None
        ),
    ) -> Response:
        """
        Make a custom API request to a ServiceNow instance.
        """
        return client.api_request(
            method=method, endpoint=endpoint, data=data, json=json
        )


def register_email_tools(mcp: FastMCP):

    @mcp.tool(tags={"email"})
    async def send_email(
        to: str | list[str] = Field(description="Recipient email addresses"),
        subject: str | None = Field(default=None, description="Email subject"),
        text: str | None = Field(default=None, description="Email body text"),
        html: str | None = Field(default=None, description="Email body HTML"),
        client=Depends(get_client),
        ctx: Context = Field(
            description="MCP context for progress reporting", default=None
        ),
    ) -> Response:
        """Sends an email via ServiceNow."""
        return client.send_email(to=to, subject=subject, text=text, html=html)


def register_data_classification_tools(mcp: FastMCP):

    @mcp.tool(tags={"data_classification"})
    async def get_data_classification(
        sys_id: str | None = Field(
            default=None, description="Classification record Sys ID"
        ),
        table_name: str | None = Field(default=None, description="Table name"),
        column_name: str | None = Field(default=None, description="Column name"),
        client=Depends(get_client),
        ctx: Context = Field(
            description="MCP context for progress reporting", default=None
        ),
    ) -> Response:
        """Retrieves data classification information."""
        return client.get_data_classification(
            sys_id=sys_id, table_name=table_name, column_name=column_name
        )


def register_attachment_tools(mcp: FastMCP):

    @mcp.tool(tags={"attachment"})
    async def servicenow_attachment(
        action: str = Field(
            description="Action to perform. Must be one of: 'get_attachment', 'upload_attachment', 'delete_attachment'"
        ),
        sys_id: str | None = Field(default=None, description="Attachment Sys ID"),
        file_path: str | None = Field(
            default=None, description="Absolute path to the file to upload"
        ),
        table_name: str | None = Field(
            default=None, description="Table name associated with the attachment"
        ),
        table_sys_id: str | None = Field(
            default=None, description="Sys ID of the record in the table"
        ),
        file_name: str | None = Field(default=None, description="Name of the file"),
        content_type: str | None = Field(
            default=None, description="MIME type of the file"
        ),
        client=Depends(get_client),
        ctx: Context | None = Field(
            description="MCP context for progress reporting", default=None
        ),
    ) -> Response:
        """Action-Routed tool for 'attachment'. Actions: 'get_attachment', 'upload_attachment', 'delete_attachment'"""
        if action == "get_attachment":
            "Retrieves attachment metadata."
            return client.get_attachment(sys_id=sys_id)
        if action == "upload_attachment":
            await ctx_progress(ctx, 0, 100)
            "Uploads an attachment to a record."
            await ctx_progress(ctx, 100, 100)
            return client.upload_attachment(
                file_path=file_path,
                table_name=table_name,
                table_sys_id=table_sys_id,
                file_name=file_name,
                content_type=content_type,
            )
        if action == "delete_attachment":
            "Deletes an attachment."
            if not await ctx_confirm_destructive(ctx, "delete attachment"):
                return {"status": "cancelled", "message": "Operation cancelled by user"}
            await ctx_progress(ctx, 0, 100)
            return client.delete_attachment(sys_id=sys_id)
        raise ValueError(f"Invalid action {action}")


def register_aggregate_tools(mcp: FastMCP):

    @mcp.tool(tags={"aggregate"})
    async def get_stats(
        table_name: str = Field(description="Table name to aggregate on"),
        query: str | None = Field(default=None, description="Encoded query string"),
        group_by: str | None = Field(default=None, description="Field to group by"),
        stats: str | None = Field(default=None, description="Statistics function"),
        client=Depends(get_client),
        ctx: Context = Field(
            description="MCP context for progress reporting", default=None
        ),
    ) -> Response:
        """Retrieves aggregate statistics for a table."""
        return client.get_stats(
            table_name=table_name, query=query, group_by=group_by, stats=stats
        )


def register_activity_subscriptions_tools(mcp: FastMCP):

    @mcp.tool(tags={"activity_subscriptions"})
    async def get_activity_subscriptions(
        sys_id: str | None = Field(
            default=None, description="Activity Subscription Sys ID"
        ),
        client=Depends(get_client),
        ctx: Context = Field(
            description="MCP context for progress reporting", default=None
        ),
    ) -> Response:
        """Retrieves activity subscriptions."""
        return client.get_activity_subscriptions(sys_id=sys_id)


def register_account_tools(mcp: FastMCP):

    @mcp.tool(tags={"account"})
    async def get_account(
        sys_id: str | None = Field(default=None, description="Account Sys ID"),
        name: str | None = Field(default=None, description="Account name"),
        number: str | None = Field(default=None, description="Account number"),
        client=Depends(get_client),
        ctx: Context = Field(
            description="MCP context for progress reporting", default=None
        ),
    ) -> Response:
        """Retrieves CSM account information."""
        return client.get_account(sys_id=sys_id, name=name, number=number)


def register_hr_tools(mcp: FastMCP):

    @mcp.tool(tags={"hr"})
    async def get_hr_profile(
        sys_id: str | None = Field(default=None, description="HR Profile Sys ID"),
        user: str | None = Field(default=None, description="User Sys ID"),
        client=Depends(get_client),
        ctx: Context = Field(
            description="MCP context for progress reporting", default=None
        ),
    ) -> Response:
        """Retrieves HR profile information."""
        return client.get_hr_profile(sys_id=sys_id, user=user)


def register_metricbase_tools(mcp: FastMCP):

    @mcp.tool(tags={"metricbase"})
    async def metricbase_insert(
        table_name: str = Field(description="Table name"),
        sys_id: str = Field(description="Record Sys ID"),
        metric_name: str = Field(description="Metric name"),
        values: list[Any] = Field(description="Values to insert"),
        start_time: str | None = Field(default=None, description="Start time"),
        end_time: str | None = Field(default=None, description="End time"),
        client=Depends(get_client),
        ctx: Context = Field(
            description="MCP context for progress reporting", default=None
        ),
    ) -> Response:
        """Inserts time series data into MetricBase."""
        return client.metricbase_insert(
            table_name=table_name,
            sys_id=sys_id,
            metric_name=metric_name,
            values=values,
            start_time=start_time,
            end_time=end_time,
        )


def register_service_qualification_tools(mcp: FastMCP):

    @mcp.tool(tags={"service_qualification"})
    async def servicenow_service_qualification(
        action: str = Field(
            description="Action to perform. Must be one of: 'check_service_qualification', 'get_service_qualification', 'process_service_qualification_result'"
        ),
        description: str | None = Field(default=None, description="Description"),
        externalId: str | None = Field(default=None, description="External ID"),
        relatedParty: list[dict[str, Any]] = Field(
            default=None, description="List of related parties"
        ),
        service_qualitification_item: list[dict[str, Any]] = Field(
            default=None, description="List of qualification items"
        ),
        id: str | None = Field(default=None, description="Qualification Request ID"),
        state: str | None = Field(default=None, description="Filter by state"),
        client=Depends(get_client),
        ctx: Context | None = Field(
            description="MCP context for progress reporting", default=None
        ),
    ) -> Response:
        """Action-Routed tool for 'service_qualification'. Actions: 'check_service_qualification', 'get_service_qualification', 'process_service_qualification_result'"""
        if action == "check_service_qualification":
            "Creates a technical service qualification request."
            return client.check_service_qualification(
                description=description,
                externalId=externalId,
                relatedParty=relatedParty,
                service_qualitification_item=service_qualitification_item,
            )
        if action == "get_service_qualification":
            "Retrieves a service qualification request."
            return client.get_service_qualification(id=id, state=state)
        if action == "process_service_qualification_result":
            "Processes a service qualification result."
            return client.process_service_qualification_result(
                service_qualitification_item=service_qualitification_item,
                description=description,
            )
        raise ValueError(f"Invalid action {action}")


def register_ppm_tools(mcp: FastMCP):

    @mcp.tool(tags={"ppm"})
    async def servicenow_ppm(
        action: str = Field(
            description="Action to perform. Must be one of: 'insert_cost_plans', 'insert_project_tasks'"
        ),
        plans: list[dict[str, Any]] = Field(
            default=None, description="List of cost plans"
        ),
        short_description: str | None = Field(
            default=None, description="Short description"
        ),
        start_date: str | None = Field(default=None, description="Start date"),
        end_date: str | None = Field(default=None, description="End date"),
        child_tasks: list[dict[str, Any]] | None = Field(
            default=None, description="Child tasks"
        ),
        dependencies: list[dict[str, Any]] | None = Field(
            default=None, description="Dependencies"
        ),
        client=Depends(get_client),
        ctx: Context | None = Field(
            description="MCP context for progress reporting", default=None
        ),
    ) -> Response:
        """Action-Routed tool for 'ppm'. Actions: 'insert_cost_plans', 'insert_project_tasks'"""
        if action == "insert_cost_plans":
            "Creates cost plans."
            return client.insert_cost_plans(plans=plans)
        if action == "insert_project_tasks":
            "Creates a project and associated project tasks."
            return client.insert_project_tasks(
                short_description=short_description,
                start_date=start_date,
                end_date=end_date,
                child_tasks=child_tasks,
                dependencies=dependencies,
            )
        raise ValueError(f"Invalid action {action}")


def register_product_inventory_tools(mcp: FastMCP):

    @mcp.tool(tags={"product_inventory"})
    async def servicenow_product_inventory(
        action: str = Field(
            description="Action to perform. Must be one of: 'get_product_inventory', 'delete_product_inventory'"
        ),
        customer: str | None = Field(default=None, description="Customer Sys ID"),
        place_id: str | None = Field(default=None, description="Location ID"),
        status: str | None = Field(default=None, description="Status filter"),
        limit: int | None = Field(default=20, description="Limit"),
        offset: int | None = Field(default=0, description="Offset"),
        id: str | None = Field(default=None, description="Product Inventory Sys ID"),
        client=Depends(get_client),
        ctx: Context | None = Field(
            description="MCP context for progress reporting", default=None
        ),
    ) -> Response:
        """Action-Routed tool for 'product_inventory'. Actions: 'get_product_inventory', 'delete_product_inventory'"""
        if action == "get_product_inventory":
            "Retrieves product inventory."
            return client.get_product_inventory(
                customer=customer,
                place_id=place_id,
                status=status,
                limit=limit,
                offset=offset,
            )
        if action == "delete_product_inventory":
            "Deletes a product inventory record."
            if not await ctx_confirm_destructive(ctx, "delete product inventory"):
                return {"status": "cancelled", "message": "Operation cancelled by user"}
            await ctx_progress(ctx, 0, 100)
            return client.delete_product_inventory(id=id)
        raise ValueError(f"Invalid action {action}")


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


def get_mcp_instance() -> tuple[Any, Any, Any, Any]:
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
