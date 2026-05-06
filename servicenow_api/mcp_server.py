#!/usr/bin/python
import warnings

# Filter RequestsDependencyWarning early to prevent log spam
with warnings.catch_warnings():
    warnings.simplefilter("ignore")
    try:
        from requests.exceptions import RequestsDependencyWarning

        warnings.filterwarnings("ignore", category=RequestsDependencyWarning)
    except ImportError:
        pass

# General urllib3/chardet mismatch warnings
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
from servicenow_api.servicenow_models import (
    FlowReportResult,
    Response,
)

__version__ = "1.12.1"

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
    pass
    pass
    logger.info("DEBUG: Executing register_tools...")

    logger.info("DEBUG: Registering get_incidents...")


def register_flows_tools(mcp: FastMCP):
    @mcp.tool(
        description="Generate a UNIFIED Mermaid diagram + rich Markdown report for multiple ServiceNow flows. Optional: leave flow_identifiers empty to fetch ALL active flows up to 1000 limit. Unrelated flow groups are split into separate safe-to-render diagram blocks. By default saves a polished .md file.",
        tags={"flows"},
    )
    async def workflow_to_mermaid(
        flow_identifiers: list[str] = Field(
            default_factory=list,
            description="List of flow names or sys_ids. If empty, fetches ALL active flows.",
        ),
        save_to_file: bool = Field(
            True,
            description="Default: True → saves polished .md file. Set False to return Markdown as text only.",
        ),
        output_dir: str | None = Field(
            "./servicenow_flow_reports", description="Default folder for saved reports"
        ),
        mermaid_name: str | None = Field("unified_flow_diagram"),
        max_depth: int | None = Field(
            5, description="Maximum recursion depth for subflows"
        ),
        segment_by_root: bool = Field(
            True, description="If True (default), each flow gets its own diagram block."
        ),
        destination_file: str | None = Field(
            None,
            description="Explicit full path to save the report (e.g. /tmp/report.md)",
        ),
        _client=Depends(get_client),
        ctx: Context = Field(
            description="MCP context for progress reporting", default=None
        ),
    ) -> FlowReportResult:
        """
        Generate a unified Mermaid diagram + rich Markdown report for multiple ServiceNow flows.
        """
        return _client.workflow_to_mermaid(
            flow_identifiers=flow_identifiers,
            save_to_file=save_to_file,
            output_dir=output_dir,
            mermaid_name=mermaid_name,
            max_depth=max_depth,
            segment_by_root=segment_by_root,
            destination_file=destination_file,
        )


def register_application_tools(mcp: FastMCP):
    @mcp.tool(
        tags={"application"},
    )
    async def get_application(
        application_id: str = Field(
            description="The unique identifier of the application to retrieve"
        ),
        _client=Depends(get_client),
        ctx: Context = Field(
            description="MCP context for progress reporting", default=None
        ),
    ) -> Response:
        """
        Retrieves details of a specific application from a ServiceNow instance by its unique identifier.
        """
        return _client.get_application(application_id)


def register_cmdb_tools(mcp: FastMCP):
    @mcp.tool(
        tags={"cmdb"},
    )
    async def get_cmdb(
        cmdb_id: str = Field(
            description="The unique identifier of the CMDB record to retrieve"
        ),
        _client=Depends(get_client),
        ctx: Context = Field(
            description="MCP context for progress reporting", default=None
        ),
    ) -> Response:
        """
        Fetches a specific Configuration Management Database (CMDB) record from a ServiceNow instance using its unique identifier.
        """

        return _client.get_cmdb(cmdb_id=cmdb_id)

    @mcp.tool(
        tags={"cmdb"},
    )
    async def delete_cmdb_relation(
        className: str = Field(description="CMDB class name"),
        sys_id: str = Field(description="Sys_id of the CI"),
        rel_sys_id: str = Field(description="Sys_id of the relation to remove"),
        _client=Depends(get_client),
        ctx: Context = Field(
            description="MCP context for progress reporting", default=None
        ),
    ) -> Response:
        """
        Deletes the relation for the specified configuration item (CI).
        """
        if not await ctx_confirm_destructive(ctx, "delete cmdb relation"):
            return {"status": "cancelled", "message": "Operation cancelled by user"}
        await ctx_progress(ctx, 0, 100)
        return _client.delete_cmdb_relation(
            className=className, sys_id=sys_id, rel_sys_id=rel_sys_id
        )

    @mcp.tool(
        tags={"cmdb"},
    )
    async def get_cmdb_instances(
        className: str = Field(description="CMDB class name"),
        sysparm_limit: str | None = Field(
            default="10000", description="Maximum number of records to return"
        ),
        sysparm_offset: str | None = Field(
            default="0", description="Starting record index"
        ),
        sysparm_query: str | None = Field(
            default=None, description="Encoded query used to filter the result set"
        ),
        _client=Depends(get_client),
        ctx: Context = Field(
            description="MCP context for progress reporting", default=None
        ),
    ) -> Response:
        """
        Returns the available configuration items (CI) for a specified CMDB class.
        """
        return _client.get_cmdb_instances(
            className=className,
            sysparm_limit=sysparm_limit,
            sysparm_offset=sysparm_offset,
            sysparm_query=sysparm_query,
        )

    @mcp.tool(
        tags={"cmdb"},
    )
    async def get_cmdb_instance(
        className: str = Field(description="CMDB class name"),
        sys_id: str = Field(description="Sys_id of the CI record to retrieve"),
        _client=Depends(get_client),
        ctx: Context = Field(
            description="MCP context for progress reporting", default=None
        ),
    ) -> Response:
        """
        Returns attributes and relationship information for a specified CI record.
        """
        return _client.get_cmdb_instance(className=className, sys_id=sys_id)

    @mcp.tool(
        tags={"cmdb"},
    )
    async def create_cmdb_instance(
        className: str = Field(description="CMDB class name"),
        source: str = Field(description="Discovery source"),
        attributes: dict | None = Field(
            default=None, description="Data attributes to define in the CI record"
        ),
        inbound_relations: list[dict] | None = Field(
            default=None, description="List of inbound relations"
        ),
        outbound_relations: list[dict] | None = Field(
            default=None, description="List of outbound relations"
        ),
        _client=Depends(get_client),
        ctx: Context = Field(
            description="MCP context for progress reporting", default=None
        ),
    ) -> Response:
        """
        Creates a single configuration item (CI).
        """
        return _client.create_cmdb_instance(
            className=className,
            source=source,
            attributes=attributes,
            inbound_relations=inbound_relations,
            outbound_relations=outbound_relations,
        )

    @mcp.tool(
        tags={"cmdb"},
    )
    async def update_cmdb_instance(
        className: str = Field(description="CMDB class name"),
        sys_id: str = Field(description="Sys_id of the CI"),
        source: str = Field(description="Discovery source"),
        attributes: dict | None = Field(
            default=None, description="Data attributes to replace"
        ),
        ctx: Context | None = None,
        _client=Depends(get_client),
    ) -> Response | str:
        """
        Updates the specified CI record (PUT).
        """
        if ctx:
            message = f"Are you sure you want to UPDATE CI {sys_id} ({className}) with source {source}?"
            result = await ctx.elicit(message, response_type=bool)
            if result.action != "accept" or not result.data:
                return "Operation cancelled by user."

        return _client.update_cmdb_instance(
            className=className,
            sys_id=sys_id,
            source=source,
            attributes=attributes,
        )

    @mcp.tool(
        tags={"cmdb"},
    )
    async def patch_cmdb_instance(
        className: str = Field(description="CMDB class name"),
        sys_id: str = Field(description="Sys_id of the CI"),
        source: str = Field(description="Discovery source"),
        attributes: dict | None = Field(
            default=None, description="Data attributes to replace"
        ),
        ctx: Context | None = None,
        _client=Depends(get_client),
    ) -> Response | str:
        """
        Replaces attributes in the specified CI record (PATCH).
        """
        if ctx:
            message = f"Are you sure you want to PATCH CI {sys_id} ({className}) with source {source}?"
            result = await ctx.elicit(message, response_type=bool)
            if result.action != "accept" or not result.data:
                return "Operation cancelled by user."

        return _client.patch_cmdb_instance(
            className=className,
            sys_id=sys_id,
            source=source,
            attributes=attributes,
        )

    @mcp.tool(
        tags={"cmdb"},
    )
    async def create_cmdb_relation(
        className: str = Field(description="CMDB class name"),
        sys_id: str = Field(description="Sys_id of the CI"),
        source: str = Field(description="Discovery source"),
        inbound_relations: list[dict] | None = Field(
            default=None, description="List of inbound relations"
        ),
        outbound_relations: list[dict] | None = Field(
            default=None, description="List of outbound relations"
        ),
        _client=Depends(get_client),
        ctx: Context = Field(
            description="MCP context for progress reporting", default=None
        ),
    ) -> Response:
        """
        Adds an inbound and/or outbound relation to the specified CI.
        """
        return _client.create_cmdb_relation(
            className=className,
            sys_id=sys_id,
            source=source,
            inbound_relations=inbound_relations,
            outbound_relations=outbound_relations,
        )

    @mcp.tool(
        tags={"cmdb"},
    )
    async def ingest_cmdb_data(
        data_source_sys_id: str = Field(description="Sys_id of the data source record"),
        records: list[dict] = Field(description="Array of objects to ingest"),
        _client=Depends(get_client),
        ctx: Context = Field(
            description="MCP context for progress reporting", default=None
        ),
    ) -> Response:
        """
        Inserts records into the Import Set table associated with the data source.
        """
        return _client.ingest_cmdb_data(
            data_source_sys_id=data_source_sys_id, records=records
        )


def register_cicd_tools(mcp: FastMCP):
    @mcp.tool(
        tags={"cicd"},
    )
    async def batch_install_result(
        result_id: str = Field(
            description="The ID associated with the batch installation result"
        ),
        _client=Depends(get_client),
        ctx: Context = Field(
            description="MCP context for progress reporting", default=None
        ),
    ) -> Response:
        await ctx_progress(ctx, 0, 100)
        """
        Retrieves the result of a batch installation process in ServiceNow by result ID.
        """

        await ctx_progress(ctx, 100, 100)
        return _client.batch_install_result(result_id=result_id)

    @mcp.tool(
        tags={"cicd"},
    )
    async def instance_scan_progress(
        progress_id: str = Field(
            description="The ID associated with the instance scan progress"
        ),
        _client=Depends(get_client),
        ctx: Context = Field(
            description="MCP context for progress reporting", default=None
        ),
    ) -> Response:
        """
        Gets the progress status of an instance scan in ServiceNow by progress ID.
        """

        return _client.instance_scan_progress(progress_id=progress_id)

    @mcp.tool(
        tags={"cicd"},
    )
    async def progress(
        progress_id: str = Field(description="The ID associated with the progress"),
        _client=Depends(get_client),
        ctx: Context = Field(
            description="MCP context for progress reporting", default=None
        ),
    ) -> Response:
        """
        Retrieves the progress status of a specified process in ServiceNow by progress ID.
        """

        return _client.progress(progress_id=progress_id)

    @mcp.tool(
        tags={"cicd"},
    )
    async def batch_install(
        name: str = Field(description="The name of the batch installation"),
        packages: str = Field(description="The packages to be installed in the batch"),
        notes: str | None = Field(
            default=None, description="Additional notes for the batch installation"
        ),
        _client=Depends(get_client),
        ctx: Context = Field(
            description="MCP context for progress reporting", default=None
        ),
    ) -> Response:
        await ctx_progress(ctx, 0, 100)
        """
        Initiates a batch installation of specified packages in ServiceNow with optional notes.
        """

        await ctx_progress(ctx, 100, 100)
        return _client.batch_install(name=name, packages=packages, notes=notes)

    @mcp.tool(
        tags={"cicd"},
    )
    async def batch_rollback(
        rollback_id: str = Field(
            description="The ID associated with the batch rollback"
        ),
        _client=Depends(get_client),
        ctx: Context = Field(
            description="MCP context for progress reporting", default=None
        ),
    ) -> Response:
        await ctx_progress(ctx, 0, 100)
        """
        Performs a rollback of a batch installation in ServiceNow using the rollback ID.
        """

        await ctx_progress(ctx, 100, 100)
        return _client.batch_rollback(rollback_id=rollback_id)

    @mcp.tool(
        tags={"cicd"},
    )
    async def app_repo_install(
        app_sys_id: str = Field(
            description="The sys_id of the application to be installed"
        ),
        scope: str = Field(description="The scope of the application"),
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
        _client=Depends(get_client),
        ctx: Context = Field(
            description="MCP context for progress reporting", default=None
        ),
    ) -> Response:
        """
        Installs an application from a repository in ServiceNow with specified parameters.
        """

        return _client.app_repo_install(
            app_sys_id=app_sys_id,
            scope=scope,
            auto_upgrade_base_app=auto_upgrade_base_app,
            base_app_version=base_app_version,
            version=version,
        )

    @mcp.tool(
        tags={"cicd"},
    )
    async def app_repo_publish(
        app_sys_id: str = Field(
            description="The sys_id of the application to be published"
        ),
        scope: str = Field(description="The scope of the application"),
        dev_notes: str | None = Field(
            default=None, description="Development notes for the published version"
        ),
        version: str | None = Field(
            default=None, description="The version of the application to be published"
        ),
        _client=Depends(get_client),
        ctx: Context = Field(
            description="MCP context for progress reporting", default=None
        ),
    ) -> Response:
        """
        Publishes an application to a repository in ServiceNow with development notes and version.
        """

        return _client.app_repo_publish(
            app_sys_id=app_sys_id, scope=scope, dev_notes=dev_notes, version=version
        )

    @mcp.tool(
        tags={"cicd"},
    )
    async def app_repo_rollback(
        app_sys_id: str = Field(
            description="The sys_id of the application to be rolled back"
        ),
        scope: str = Field(description="The scope of the application"),
        version: str = Field(
            description="The version of the application to be rolled back"
        ),
        _client=Depends(get_client),
        ctx: Context = Field(
            description="MCP context for progress reporting", default=None
        ),
    ) -> Response:
        """
        Rolls back an application to a previous version in ServiceNow by sys_id, scope, and version.
        """

        return _client.app_repo_rollback(
            app_sys_id=app_sys_id, scope=scope, version=version
        )

    @mcp.tool(
        tags={"cicd"},
    )
    async def full_scan(
        _client=Depends(get_client),
        ctx: Context = Field(
            description="MCP context for progress reporting", default=None
        ),
    ) -> Response:
        """
        Initiates a full scan of the ServiceNow instance.
        """

        return _client.full_scan()

    @mcp.tool(
        tags={"cicd"},
    )
    async def point_scan(
        target_sys_id: str = Field(description="The sys_id of the target instance"),
        target_table: str = Field(description="The table of the target instance"),
        _client=Depends(get_client),
        ctx: Context = Field(
            description="MCP context for progress reporting", default=None
        ),
    ) -> Response:
        """
        Performs a targeted scan on a specific instance and table in ServiceNow.
        """

        return _client.point_scan(
            target_sys_id=target_sys_id, target_table=target_table
        )

    @mcp.tool(
        tags={"cicd"},
    )
    async def combo_suite_scan(
        combo_sys_id: str = Field(description="The sys_id of the combo to be scanned"),
        _client=Depends(get_client),
        ctx: Context = Field(
            description="MCP context for progress reporting", default=None
        ),
    ) -> Response:
        """
        Executes a scan on a combination of suites in ServiceNow by combo sys_id.
        """

        return _client.combo_suite_scan(combo_sys_id=combo_sys_id)

    @mcp.tool(
        tags={"cicd"},
    )
    async def suite_scan(
        suite_sys_id: str = Field(description="The sys_id of the suite to be scanned"),
        sys_ids: list[str] = Field(
            description="List of sys_ids representing app_scope_sys_ids for the suite scan"
        ),
        scan_type: str = Field(
            default="scoped_apps", description="Type of scan to be performed"
        ),
        _client=Depends(get_client),
        ctx: Context = Field(
            description="MCP context for progress reporting", default=None
        ),
    ) -> Response:
        """
        Runs a scan on a specified suite with a list of sys_ids and scan type in ServiceNow.
        """

        return _client.suite_scan(
            suite_sys_id=suite_sys_id, sys_ids=sys_ids, scan_type=scan_type
        )


def register_plugins_tools(mcp: FastMCP):
    @mcp.tool(
        tags={"plugins"},
    )
    async def activate_plugin(
        plugin_id: str = Field(description="The ID of the plugin to be activated"),
        _client=Depends(get_client),
        ctx: Context = Field(
            description="MCP context for progress reporting", default=None
        ),
    ) -> Response:
        """
        Activates a specified plugin in ServiceNow by plugin ID.
        """

        return _client.activate_plugin(plugin_id=plugin_id)

    @mcp.tool(
        tags={"plugins"},
    )
    async def rollback_plugin(
        plugin_id: str = Field(description="The ID of the plugin to be rolled back"),
        _client=Depends(get_client),
        ctx: Context = Field(
            description="MCP context for progress reporting", default=None
        ),
    ) -> Response:
        """
        Rolls back a specified plugin in ServiceNow to its previous state by plugin ID.
        """

        return _client.rollback_plugin(plugin_id=plugin_id)


def register_source_control_tools(mcp: FastMCP):
    @mcp.tool(
        tags={"source_control"},
    )
    async def apply_remote_source_control_changes(
        app_sys_id: str = Field(
            description="The sys_id of the application for which changes should be applied"
        ),
        scope: str = Field(description="The scope of the changes"),
        branch_name: str = Field(
            description="The name of the branch containing the changes"
        ),
        auto_upgrade_base_app: bool | None = Field(
            default=None,
            description="Flag indicating whether to auto-upgrade the base app",
        ),
        _client=Depends(get_client),
        ctx: Context = Field(
            description="MCP context for progress reporting", default=None
        ),
    ) -> Response:
        """
        Applies changes from a remote source control branch to a ServiceNow application.
        """

        return _client.apply_remote_source_control_changes(
            app_sys_id=app_sys_id,
            scope=scope,
            branch_name=branch_name,
            auto_upgrade_base_app=auto_upgrade_base_app,
        )

    @mcp.tool(
        tags={"source_control"},
    )
    async def import_repository(
        repo_url: str = Field(description="The URL of the repository to be imported"),
        credential_sys_id: str | None = Field(
            default=None,
            description="The sys_id of the credential to be used for the import",
        ),
        mid_server_sys_id: str | None = Field(
            default=None,
            description="The sys_id of the MID Server to be used for the import",
        ),
        branch_name: str | None = Field(
            default=None, description="The name of the branch to be imported"
        ),
        auto_upgrade_base_app: bool | None = Field(
            default=None,
            description="Flag indicating whether to auto-upgrade the base app",
        ),
        _client=Depends(get_client),
        ctx: Context = Field(
            description="MCP context for progress reporting", default=None
        ),
    ) -> Response:
        """
        Imports a repository into ServiceNow with specified credentials and branch.
        """

        return _client.import_repository(
            credential_sys_id=credential_sys_id,
            mid_server_sys_id=mid_server_sys_id,
            repo_url=repo_url,
            branch_name=branch_name,
            auto_upgrade_base_app=auto_upgrade_base_app,
        )


def register_testing_tools(mcp: FastMCP):
    @mcp.tool(
        tags={"testing"},
    )
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
        _client=Depends(get_client),
        ctx: Context = Field(
            description="MCP context for progress reporting", default=None
        ),
    ) -> Response:
        await ctx_progress(ctx, 0, 100)
        """
        Executes a test suite in ServiceNow with specified browser and OS configurations.
        """

        await ctx_progress(ctx, 100, 100)
        return _client.run_test_suite(
            test_suite_sys_id=test_suite_sys_id,
            test_suite_name=test_suite_name,
            browser_name=browser_name,
            browser_version=browser_version,
            os_name=os_name,
            os_version=os_version,
        )


def register_update_sets_tools(mcp: FastMCP):
    @mcp.tool(
        tags={"update_sets"},
    )
    async def update_set_create(
        update_set_name: str = Field(description="Name to give the update set"),
        scope: str = Field(
            description="The scope name of the application in which to create the new update set"
        ),
        sys_id: str = Field(
            description="Sys_id of the application in which to create the new update set"
        ),
        description: str | None = Field(
            default=None, description="Description of the update set"
        ),
        _client=Depends(get_client),
        ctx: Context = Field(
            description="MCP context for progress reporting", default=None
        ),
    ) -> Response:
        """
        Creates a new update set in ServiceNow with a given name, scope, and description.
        """

        return _client.update_set_create(
            update_set_name=update_set_name,
            description=description,
            scope=scope,
            sys_id=sys_id,
        )

    @mcp.tool(
        tags={"update_sets"},
    )
    async def update_set_retrieve(
        update_set_id: str = Field(
            description="Sys_id of the update set on the source instance from where the update set was retrieved"
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
        _client=Depends(get_client),
        ctx: Context = Field(
            description="MCP context for progress reporting", default=None
        ),
    ) -> Response:
        """
        Retrieves an update set from a source instance in ServiceNow with optional preview and cleanup.
        """

        return _client.update_set_retrieve(
            update_set_id=update_set_id,
            update_source_id=update_source_id,
            update_source_instance_id=update_source_instance_id,
            auto_preview=auto_preview,
            cleanup_retrieved=cleanup_retrieved,
        )

    @mcp.tool(
        tags={"update_sets"},
    )
    async def update_set_preview(
        remote_update_set_id: str = Field(
            description="Sys_id of the update set to preview"
        ),
        _client=Depends(get_client),
        ctx: Context = Field(
            description="MCP context for progress reporting", default=None
        ),
    ) -> Response:
        """
        Previews an update set in ServiceNow by its remote sys_id.
        """

        return _client.update_set_preview(remote_update_set_id=remote_update_set_id)

    @mcp.tool(
        tags={"update_sets"},
    )
    async def update_set_commit(
        remote_update_set_id: str = Field(
            description="Sys_id of the update set to commit"
        ),
        force_commit: str | None = Field(
            default=None,
            description="Flag that indicates whether to force commit the update set",
        ),
        _client=Depends(get_client),
        ctx: Context = Field(
            description="MCP context for progress reporting", default=None
        ),
    ) -> Response:
        """
        Commits an update set in ServiceNow with an option to force commit.
        """

        return _client.update_set_commit(
            remote_update_set_id=remote_update_set_id, force_commit=force_commit
        )

    @mcp.tool(
        tags={"update_sets"},
    )
    async def update_set_commit_multiple(
        remote_update_set_ids: list[str] = Field(
            description="List of sys_ids associated with update sets to commit. Sys_ids are committed in the order given"
        ),
        force_commit: str | None = Field(
            default=None,
            description="Flag that indicates whether to force commit the update sets",
        ),
        _client=Depends(get_client),
        ctx: Context = Field(
            description="MCP context for progress reporting", default=None
        ),
    ) -> Response:
        """
        Commits multiple update sets in ServiceNow in the specified order.
        """

        return _client.update_set_commit_multiple(
            remote_update_set_ids=remote_update_set_ids, force_commit=force_commit
        )

    @mcp.tool(
        tags={"update_sets"},
    )
    async def update_set_back_out(
        update_set_id: str = Field(description="Sys_id of the update set"),
        rollback_installs: bool | None = Field(
            default=None,
            description="Flag that indicates whether to rollback the batch installation performed during the update set commit",
        ),
        _client=Depends(get_client),
        ctx: Context = Field(
            description="MCP context for progress reporting", default=None
        ),
    ) -> Response:
        """
        Backs out an update set in ServiceNow with an option to rollback installations.
        """

        return _client.update_set_back_out(
            update_set_id=update_set_id, rollback_installs=rollback_installs
        )


def register_batch_tools(mcp: FastMCP):
    @mcp.tool(
        tags={"batch"},
    )
    async def batch_request(
        rest_requests: list[dict] = Field(
            description="List of requests to execute. Each item must correspond to BatchRequestItem model."
        ),
        batch_request_id: str | None = Field(
            default=None, description="Client provided batch ID"
        ),
        _client=Depends(get_client),
        ctx: Context = Field(
            description="MCP context for progress reporting", default=None
        ),
    ) -> Response:
        await ctx_progress(ctx, 0, 100)
        """
        Sends multiple REST API requests in a single call.
        """
        await ctx_progress(ctx, 100, 100)
        return _client.batch_request(
            batch_request_id=batch_request_id, rest_requests=rest_requests
        )


def register_change_management_tools(mcp: FastMCP):
    @mcp.tool(
        tags={"change_management"},
    )
    async def get_change_requests(
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
        _client=Depends(get_client),
        ctx: Context = Field(
            description="MCP context for progress reporting", default=None
        ),
    ) -> Response:
        """
        Retrieves change requests from ServiceNow with optional filtering and pagination.
        """

        logging.info("Getting Change Requests...")
        return _client.get_change_requests(
            order=order,
            name_value_pairs=name_value_pairs,
            sysparm_query=sysparm_query,
            text_search=text_search,
            change_type=change_type,
            sysparm_offset=sysparm_offset,
            sysparm_limit=sysparm_limit,
        )

    @mcp.tool(
        tags={"change_management"},
    )
    async def get_change_request_nextstate(
        change_request_sys_id: str = Field(description="Sys ID of the change request"),
        _client=Depends(get_client),
        ctx: Context = Field(
            description="MCP context for progress reporting", default=None
        ),
    ) -> Response:
        """
        Gets the next state for a specific change request in ServiceNow.
        """

        return _client.get_change_request_nextstate(
            change_request_sys_id=change_request_sys_id
        )

    @mcp.tool(
        tags={"change_management"},
    )
    async def get_change_request_schedule(
        cmdb_ci_sys_id: str = Field(
            description="Sys ID of the CI (Configuration Item)"
        ),
        _client=Depends(get_client),
        ctx: Context = Field(
            description="MCP context for progress reporting", default=None
        ),
    ) -> Response:
        """
        Retrieves the schedule for a change request based on a Configuration Item (CI) in ServiceNow.
        """

        return _client.get_change_request_schedule(cmdb_ci_sys_id=cmdb_ci_sys_id)

    @mcp.tool(
        tags={"change_management"},
    )
    async def get_change_request_tasks(
        change_request_sys_id: str = Field(description="Sys ID of the change request"),
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
        sysparm_offset: int | None = Field(
            default=None, description="Offset for pagination"
        ),
        sysparm_limit: int | None = Field(
            default=os.environ.get("SERVICENOW_RETURN_LIMIT", to_integer(string="5")),
            description="Limit for pagination",
        ),
        _client=Depends(get_client),
        ctx: Context = Field(
            description="MCP context for progress reporting", default=None
        ),
    ) -> Response:
        """
        Fetches tasks associated with a change request in ServiceNow with optional filtering.
        """

        return _client.get_change_request_tasks(
            change_request_sys_id=change_request_sys_id,
            order=order,
            name_value_pairs=name_value_pairs,
            sysparm_query=sysparm_query,
            text_search=text_search,
            sysparm_offset=sysparm_offset,
            sysparm_limit=sysparm_limit,
        )

    @mcp.tool(
        tags={"change_management"},
    )
    async def get_change_request(
        change_request_id: str = Field(
            description="Sys ID or change number (CHG#####) of the change request",
            default=None,
        ),
        change_type: str | None = Field(
            default=None, description="Type of change (emergency, normal, standard)"
        ),
        _client=Depends(get_client),
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
        ctx: Context = Field(
            description="MCP context for progress reporting", default=None
        ),
    ) -> Response | None:
        """
        Retrieves details of a specific change request in ServiceNow by sys_id and type.
        """

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
                return _client.get_change_request(
                    change_request_sys_id=change_request_id,
                    change_type=change_type,
                )

        if not change_request_id:
            logging.info("Getting Changes via query...")
            return _client.get_change_requests(
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

    @mcp.tool(
        tags={"change_management"},
    )
    async def get_change_request_ci(
        change_request_sys_id: str = Field(description="Sys ID of the change request"),
        _client=Depends(get_client),
        ctx: Context = Field(
            description="MCP context for progress reporting", default=None
        ),
    ) -> Response:
        """
        Gets Configuration Items (CIs) associated with a change request in ServiceNow.
        """

        return _client.get_change_request_ci(
            change_request_sys_id=change_request_sys_id
        )

    @mcp.tool(
        tags={"change_management"},
    )
    async def get_change_request_conflict(
        change_request_sys_id: str = Field(description="Sys ID of the change request"),
        _client=Depends(get_client),
        ctx: Context = Field(
            description="MCP context for progress reporting", default=None
        ),
    ) -> Response:
        """
        Checks for conflicts in a change request in ServiceNow.
        """

        return _client.get_change_request_conflict(
            change_request_sys_id=change_request_sys_id
        )

    @mcp.tool(
        tags={"change_management"},
    )
    async def get_standard_change_request_templates(
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
        sysparm_offset: int | None = Field(
            default=None, description="Offset for pagination"
        ),
        sysparm_limit: int | None = Field(
            default=os.environ.get("SERVICENOW_RETURN_LIMIT", to_integer(string="5")),
            description="Limit for pagination",
        ),
        _client=Depends(get_client),
        ctx: Context = Field(
            description="MCP context for progress reporting", default=None
        ),
    ) -> Response:
        """
        Retrieves standard change request templates from ServiceNow with optional filtering.
        """

        return _client.get_standard_change_request_templates(
            order=order,
            name_value_pairs=name_value_pairs,
            sysparm_query=sysparm_query,
            text_search=text_search,
            sysparm_offset=sysparm_offset,
            sysparm_limit=sysparm_limit,
        )

    @mcp.tool(
        tags={"change_management"},
    )
    async def get_change_request_models(
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
        _client=Depends(get_client),
        ctx: Context = Field(
            description="MCP context for progress reporting", default=None
        ),
    ) -> Response:
        """
        Fetches change request models from ServiceNow with optional filtering and type.
        """

        return _client.get_change_request_models(
            order=order,
            name_value_pairs=name_value_pairs,
            sysparm_query=sysparm_query,
            text_search=text_search,
            change_type=change_type,
            sysparm_offset=sysparm_offset,
            sysparm_limit=sysparm_limit,
        )

    @mcp.tool(
        tags={"change_management"},
    )
    async def get_standard_change_request_model(
        model_sys_id: str = Field(
            description="Sys ID of the standard change request model"
        ),
        _client=Depends(get_client),
        ctx: Context = Field(
            description="MCP context for progress reporting", default=None
        ),
    ) -> Response:
        """
        Retrieves a specific standard change request model in ServiceNow by sys_id.
        """

        return _client.get_standard_change_request_model(model_sys_id=model_sys_id)

    @mcp.tool(
        tags={"change_management"},
    )
    async def get_standard_change_request_template(
        template_sys_id: str = Field(
            description="Sys ID of the standard change request template"
        ),
        _client=Depends(get_client),
        ctx: Context = Field(
            description="MCP context for progress reporting", default=None
        ),
    ) -> Response:
        """
        Gets a specific standard change request template in ServiceNow by sys_id.
        """

        return _client.get_standard_change_request_template(
            template_sys_id=template_sys_id
        )

    @mcp.tool(
        tags={"change_management"},
    )
    async def get_change_request_worker(
        worker_sys_id: str = Field(description="Sys ID of the change request worker"),
        _client=Depends(get_client),
        ctx: Context = Field(
            description="MCP context for progress reporting", default=None
        ),
    ) -> Response:
        """
        Retrieves details of a change request worker in ServiceNow by sys_id.
        """

        return _client.get_change_request_worker(worker_sys_id=worker_sys_id)

    @mcp.tool(
        tags={"change_management"},
    )
    async def create_change_request(
        name_value_pairs: str | None = Field(
            default=None,
            description="Dictionary of name-value pairs for filtering records entered as a string",
        ),
        change_type: str | None = Field(
            default="normal", description="Type of change (emergency, normal, standard)"
        ),
        standard_change_template_id: str | None = Field(
            default=None,
            description="Sys ID of the standard change request template (if applicable)",
        ),
        _client=Depends(get_client),
        ctx: Context = Field(
            description="MCP context for progress reporting", default=None
        ),
    ) -> Response:
        """
        Creates a new change request in ServiceNow with specified details and type.
        """

        return _client.create_change_request(
            name_value_pairs=name_value_pairs,
            change_type=change_type,
            standard_change_template_id=standard_change_template_id,
        )

    @mcp.tool(
        tags={"change_management"},
    )
    async def create_change_request_task(
        change_request_sys_id: str = Field(description="Sys ID of the change request"),
        data: dict[str, str] = Field(
            description="Name-value pairs providing details for the new task"
        ),
        _client=Depends(get_client),
        ctx: Context = Field(
            description="MCP context for progress reporting", default=None
        ),
    ) -> Response:
        """
        Creates a task for a change request in ServiceNow with provided details.
        """

        return _client.create_change_request_task(
            change_request_sys_id=change_request_sys_id, data=data
        )

    @mcp.tool(
        tags={"change_management"},
    )
    async def create_change_request_ci_association(
        change_request_sys_id: str = Field(description="Sys ID of the change request"),
        cmdb_ci_sys_ids: list[str] = Field(
            description="List of Sys IDs of CIs to associate with the change request"
        ),
        association_type: str = Field(
            description="Type of association (affected, impacted, offering)"
        ),
        refresh_impacted_services: bool | None = Field(
            default=None,
            description="Flag to refresh impacted services (applicable for 'affected' association)",
        ),
        _client=Depends(get_client),
        ctx: Context = Field(
            description="MCP context for progress reporting", default=None
        ),
    ) -> Response:
        """
        Associates Configuration Items (CIs) with a change request in ServiceNow.
        """

        return _client.create_change_request_ci_association(
            change_request_sys_id=change_request_sys_id,
            cmdb_ci_sys_ids=cmdb_ci_sys_ids,
            association_type=association_type,
            refresh_impacted_services=refresh_impacted_services,
        )

    @mcp.tool(
        tags={"change_management"},
    )
    async def calculate_standard_change_request_risk(
        change_request_sys_id: str = Field(
            description="Sys ID of the standard change request"
        ),
        _client=Depends(get_client),
        ctx: Context = Field(
            description="MCP context for progress reporting", default=None
        ),
    ) -> Response:
        """
        Calculates the risk for a standard change request in ServiceNow.
        """

        return _client.calculate_standard_change_request_risk(
            change_request_sys_id=change_request_sys_id
        )

    @mcp.tool(
        tags={"change_management"},
    )
    async def check_change_request_conflict(
        change_request_sys_id: str = Field(description="Sys ID of the change request"),
        _client=Depends(get_client),
        ctx: Context = Field(
            description="MCP context for progress reporting", default=None
        ),
    ) -> Response:
        """
        Checks for conflicts in a change request in ServiceNow.
        """

        return _client.check_change_request_conflict(
            change_request_sys_id=change_request_sys_id
        )

    @mcp.tool(
        tags={"change_management"},
    )
    async def refresh_change_request_impacted_services(
        change_request_sys_id: str = Field(description="Sys ID of the change request"),
        _client=Depends(get_client),
        ctx: Context = Field(
            description="MCP context for progress reporting", default=None
        ),
    ) -> Response:
        """
        Refreshes the impacted services for a change request in ServiceNow.
        """

        return _client.refresh_change_request_impacted_services(
            change_request_sys_id=change_request_sys_id
        )

    @mcp.tool(
        tags={"change_management"},
    )
    async def approve_change_request(
        change_request_sys_id: str = Field(description="Sys ID of the change request"),
        state: str = Field(
            description="State to set the change request to (approved or rejected)"
        ),
        _client=Depends(get_client),
        ctx: Context = Field(
            description="MCP context for progress reporting", default=None
        ),
    ) -> Response:
        """
        Approves or rejects a change request in ServiceNow by setting its state.
        """

        return _client.approve_change_request(
            change_request_sys_id=change_request_sys_id, state=state
        )

    @mcp.tool(
        tags={"change_management"},
    )
    async def update_change_request(
        change_request_sys_id: str = Field(description="Sys ID of the change request"),
        name_value_pairs: str | None = Field(
            default=None,
            description="Dictionary of name-value pairs for filtering records entered as a string",
        ),
        change_type: str | None = Field(
            default=None,
            description="Type of change (emergency, normal, standard, model)",
        ),
        _client=Depends(get_client),
        ctx: Context = Field(
            description="MCP context for progress reporting", default=None
        ),
    ) -> Response:
        """
        Updates a change request in ServiceNow with new details and type.
        """

        return _client.update_change_request(
            change_request_sys_id=change_request_sys_id,
            name_value_pairs=name_value_pairs,
            change_type=change_type,
        )

    @mcp.tool(
        tags={"change_management"},
    )
    async def update_change_request_first_available(
        change_request_sys_id: str = Field(description="Sys ID of the change request"),
        _client=Depends(get_client),
        ctx: Context = Field(
            description="MCP context for progress reporting", default=None
        ),
    ) -> Response:
        """
        Updates a change request to the first available state in ServiceNow.
        """

        return _client.update_change_request_first_available(
            change_request_sys_id=change_request_sys_id
        )

    @mcp.tool(
        tags={"change_management"},
    )
    async def update_change_request_task(
        change_request_sys_id: str = Field(description="Sys ID of the change request"),
        change_request_task_sys_id: str = Field(
            description="Sys ID of the change request task"
        ),
        name_value_pairs: str | None = Field(
            default=None,
            description="Dictionary of name-value pairs for filtering records entered as a string",
        ),
        _client=Depends(get_client),
        ctx: Context = Field(
            description="MCP context for progress reporting", default=None
        ),
    ) -> Response:
        """
        Updates a task for a change request in ServiceNow with new details.
        """

        return _client.update_change_request_task(
            change_request_sys_id=change_request_sys_id,
            change_request_task_sys_id=change_request_task_sys_id,
            name_value_pairs=name_value_pairs,
        )

    @mcp.tool(
        tags={"change_management"},
    )
    async def delete_change_request(
        change_request_sys_id: str = Field(description="Sys ID of the change request"),
        change_type: str | None = Field(
            default=None, description="Type of change (emergency, normal, standard)"
        ),
        _client=Depends(get_client),
        ctx: Context = Field(
            description="MCP context for progress reporting", default=None
        ),
    ) -> Response:
        """
        Deletes a change request from ServiceNow by sys_id and type.
        """

        if not await ctx_confirm_destructive(ctx, "delete change request"):
            return {"status": "cancelled", "message": "Operation cancelled by user"}
        await ctx_progress(ctx, 0, 100)
        return _client.delete_change_request(
            change_request_sys_id=change_request_sys_id, change_type=change_type
        )

    @mcp.tool(
        tags={"change_management"},
    )
    async def delete_change_request_task(
        change_request_sys_id: str = Field(description="Sys ID of the change request"),
        task_sys_id: str = Field(
            description="Sys ID of the task associated with the change request"
        ),
        _client=Depends(get_client),
        ctx: Context = Field(
            description="MCP context for progress reporting", default=None
        ),
    ) -> Response:
        """
        Deletes a task associated with a change request in ServiceNow.
        """

        if not await ctx_confirm_destructive(ctx, "delete change request task"):
            return {"status": "cancelled", "message": "Operation cancelled by user"}
        await ctx_progress(ctx, 0, 100)
        return _client.delete_change_request_task(
            change_request_sys_id=change_request_sys_id, task_sys_id=task_sys_id
        )

    @mcp.tool(
        tags={"change_management"},
    )
    async def delete_change_request_conflict_scan(
        change_request_sys_id: str = Field(description="Sys ID of the change request"),
        task_sys_id: str = Field(
            description="Sys ID of the task associated with the change request"
        ),
        _client=Depends(get_client),
        ctx: Context = Field(
            description="MCP context for progress reporting", default=None
        ),
    ) -> Response:
        """
        Deletes a conflict scan for a change request in ServiceNow.
        """

        if not await ctx_confirm_destructive(
            ctx, "delete change request conflict scan"
        ):
            return {"status": "cancelled", "message": "Operation cancelled by user"}
        await ctx_progress(ctx, 0, 100)
        return _client.delete_change_request_conflict_scan(
            change_request_sys_id=change_request_sys_id, task_sys_id=task_sys_id
        )


def register_cilifecycle_tools(mcp: FastMCP):
    @mcp.tool(
        tags={"cilifecycle"},
    )
    async def check_ci_lifecycle_compat_actions(
        actionName: str = Field(description="Name of the CI action"),
        otherActionName: str = Field(description="Name of the other CI action"),
        _client=Depends(get_client),
        ctx: Context = Field(
            description="MCP context for progress reporting", default=None
        ),
    ) -> Response:
        """
        Determines whether two specified CI actions are compatible.
        """
        return _client.check_ci_lifecycle_compat_actions(
            actionName=actionName, otherActionName=otherActionName
        )

    @mcp.tool(
        tags={"cilifecycle"},
    )
    async def register_ci_lifecycle_operator(
        _client=Depends(get_client),
        ctx: Context = Field(
            description="MCP context for progress reporting", default=None
        ),
    ) -> Response:
        """
        Registers an operator for a non-workflow user.
        """
        return _client.register_ci_lifecycle_operator()

    @mcp.tool(
        tags={"cilifecycle"},
    )
    async def unregister_ci_lifecycle_operator(
        req_id: str = Field(description="Request ID needed to unregister"),
        _client=Depends(get_client),
        ctx: Context = Field(
            description="MCP context for progress reporting", default=None
        ),
    ) -> Response:
        """
        Unregisters an operator for non-workflow users.
        """
        return _client.unregister_ci_lifecycle_operator(req_id=req_id)


def register_devops_tools(mcp: FastMCP):
    @mcp.tool(
        tags={"devops"},
    )
    async def check_devops_change_control(
        toolId: str = Field(description="Tool ID"),
        orchestrationTaskName: str | None = Field(
            default=None, description="Orchestration Task Name"
        ),
        toolType: str = Field(default="jenkins", description="Tool Type"),
        orchestrationTaskURL: str | None = Field(
            default=None, description="Orchestration Task URL"
        ),
        testConnection: bool | None = Field(
            default=None, description="Test Connection"
        ),
        _client=Depends(get_client),
        ctx: Context = Field(
            description="MCP context for progress reporting", default=None
        ),
    ) -> Response:
        """
        Checks if the orchestration task is under change control.
        """
        return _client.check_devops_change_control(
            toolId=toolId,
            orchestrationTaskName=orchestrationTaskName,
            toolType=toolType,
            orchestrationTaskURL=orchestrationTaskURL,
            testConnection=testConnection,
        )

    @mcp.tool(
        tags={"devops"},
    )
    async def register_devops_artifact(
        artifacts: list[dict] = Field(description="List of artifacts to register"),
        orchestrationToolId: str | None = Field(
            default=None, description="Orchestration Tool ID"
        ),
        toolId: str | None = Field(default=None, description="Artifact Tool ID"),
        branchName: str | None = Field(default=None, description="Branch Name"),
        pipelineName: str | None = Field(default=None, description="Pipeline Name"),
        projectName: str | None = Field(default=None, description="Project Name"),
        stageName: str | None = Field(default=None, description="Stage Name"),
        taskExecutionNumber: str | None = Field(
            default=None, description="Task Execution Number"
        ),
        _client=Depends(get_client),
        ctx: Context = Field(
            description="MCP context for progress reporting", default=None
        ),
    ) -> Response:
        """
        Enables orchestration tools to register artifacts into a ServiceNow instance.
        """
        return _client.register_devops_artifact(
            artifacts=artifacts,
            orchestrationToolId=orchestrationToolId,
            toolId=toolId,
            branchName=branchName,
            pipelineName=pipelineName,
            projectName=projectName,
            stageName=stageName,
            taskExecutionNumber=taskExecutionNumber,
        )


def register_import_sets_tools(mcp: FastMCP):
    @mcp.tool(
        tags={"import_sets"},
    )
    async def get_import_set(
        table: str = Field(
            description="The name of the table associated with the import set"
        ),
        import_set_sys_id: str = Field(
            description="The sys_id of the import set record"
        ),
        _client=Depends(get_client),
        ctx: Context = Field(
            description="MCP context for progress reporting", default=None
        ),
    ) -> Response:
        """
        Retrieves details of a specific import set record from a ServiceNow instance.
        """

        return _client.get_import_set(table=table, import_set_sys_id=import_set_sys_id)

    @mcp.tool(
        tags={"import_sets"},
    )
    async def insert_import_set(
        table: str = Field(
            description="The name of the table associated with the import set"
        ),
        data: dict[str, str] = Field(
            description="Dictionary containing the field values for the new import set record"
        ),
        _client=Depends(get_client),
        ctx: Context = Field(
            description="MCP context for progress reporting", default=None
        ),
    ) -> Response:
        """
        Inserts a new record into a specified import set on a ServiceNow instance.
        """

        return _client.insert_import_set(table=table, data=data)

    @mcp.tool(
        tags={"import_sets"},
    )
    async def insert_multiple_import_sets(
        table: str = Field(
            description="The name of the table associated with the import set"
        ),
        data: list[dict[str, str]] = Field(
            description="List of dictionaries containing field values for multiple new import set records"
        ),
        _client=Depends(get_client),
        ctx: Context = Field(
            description="MCP context for progress reporting", default=None
        ),
    ) -> Response:
        """
        Inserts multiple records into a specified import set on a ServiceNow instance.
        """

        return _client.insert_multiple_import_sets(table=table, data=data)


def register_incidents_tools(mcp: FastMCP):
    @mcp.tool(
        tags={"incidents"},
    )
    async def get_incidents(
        incident_id: str | None = Field(
            default=None,
            description="The sys_id or the incident number (INC######) of the incident record, if retrieving a specific incident",
        ),
        _client=Depends(get_client),
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
        ctx: Context = Field(
            description="MCP context for progress reporting", default=None
        ),
    ) -> Response | None:
        """
        Retrieves incident records from a ServiceNow instance, optionally by specific incident ID.
        """

        if incident_id:
            if incident_id.upper().startswith("INC") and len(incident_id) < 32:
                logging.info(f"Treating incident_id='{incident_id}' as number query")
                sysparm_query = f"number={incident_id}"
                incident_id = None
            else:
                logging.info("Getting Incident by sys_id...")
                return _client.get_incident(incident_id=incident_id)

        if not incident_id:
            logging.info("Getting Incidents via query...")
            return _client.get_incidents(
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

    @mcp.tool(
        tags={"incidents"},
    )
    async def create_incident(
        data: dict[str, str] = Field(
            description="Dictionary containing the field values for the new incident record"
        ),
        _client=Depends(get_client),
        ctx: Context = Field(
            description="MCP context for progress reporting", default=None
        ),
    ) -> Response:
        """
        Creates a new incident record on a ServiceNow instance with provided details.
        """
        return _client.create_incident(data=data)


def register_knowledge_management_tools(mcp: FastMCP):
    @mcp.tool(
        tags={"knowledge_management"},
    )
    async def get_knowledge_articles(
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
        _client=Depends(get_client),
        ctx: Context = Field(
            description="MCP context for progress reporting", default=None
        ),
    ) -> Response:
        """
        Get all Knowledge Base articles from a ServiceNow instance.
        """

        return _client.get_knowledge_articles(
            filter=filter,
            sysparm_fields=sysparm_fields,
            sysparm_limit=sysparm_limit,
            sysparm_offset=sysparm_offset,
            sysparm_query=sysparm_query,
            sysparm_query_category=sysparm_query_category,
            kb=kb,
            language=language,
        )

    @mcp.tool(
        tags={"knowledge_management"},
    )
    async def get_knowledge_article(
        article_sys_id: str = Field(
            description="The sys_id of the Knowledge Base article"
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
        _client=Depends(get_client),
        ctx: Context = Field(
            description="MCP context for progress reporting", default=None
        ),
    ) -> Response:
        """
        Get a specific Knowledge Base article from a ServiceNow instance.
        """

        return _client.get_knowledge_article(
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

    @mcp.tool(
        tags={"knowledge_management"},
    )
    async def get_knowledge_article_attachment(
        article_sys_id: str = Field(
            description="The sys_id of the Knowledge Base article"
        ),
        attachment_sys_id: str = Field(description="The sys_id of the attachment"),
        _client=Depends(get_client),
        ctx: Context = Field(
            description="MCP context for progress reporting", default=None
        ),
    ) -> Response:
        """
        Get a Knowledge Base article attachment from a ServiceNow instance.
        """

        return _client.get_knowledge_article_attachment(
            article_sys_id=article_sys_id, attachment_sys_id=attachment_sys_id
        )

    @mcp.tool(
        tags={"knowledge_management"},
    )
    async def get_featured_knowledge_article(
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
        kb: str | None = Field(
            default=None,
            description="Comma-separated list of knowledge base sys_ids to restrict results to",
        ),
        language: str | None = Field(
            default=None,
            description="Comma-separated languages in ISO 639-1 format or 'all' to search all valid languages",
        ),
        _client=Depends(get_client),
        ctx: Context = Field(
            description="MCP context for progress reporting", default=None
        ),
    ) -> Response:
        """
        Get featured Knowledge Base articles from a ServiceNow instance.
        """

        return _client.get_featured_knowledge_article(
            sysparm_fields=sysparm_fields,
            sysparm_limit=sysparm_limit,
            sysparm_offset=sysparm_offset,
            kb=kb,
            language=language,
        )

    @mcp.tool(
        tags={"knowledge_management"},
    )
    async def get_most_viewed_knowledge_articles(
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
        kb: str | None = Field(
            default=None,
            description="Comma-separated list of knowledge base sys_ids to restrict results to",
        ),
        language: str | None = Field(
            default=None,
            description="Comma-separated languages in ISO 639-1 format or 'all' to search all valid languages",
        ),
        _client=Depends(get_client),
        ctx: Context = Field(
            description="MCP context for progress reporting", default=None
        ),
    ) -> Response:
        """
        Get most viewed Knowledge Base articles from a ServiceNow instance.
        """

        return _client.get_most_viewed_knowledge_articles(
            sysparm_fields=sysparm_fields,
            sysparm_limit=sysparm_limit,
            sysparm_offset=sysparm_offset,
            kb=kb,
            language=language,
        )


def register_table_api_tools(mcp: FastMCP):
    @mcp.tool(
        tags={"table_api"},
    )
    async def delete_table_record(
        table: str = Field(description="The name of the table"),
        table_record_sys_id: str = Field(
            description="The sys_id of the record to be deleted"
        ),
        _client=Depends(get_client),
        ctx: Context = Field(
            description="MCP context for progress reporting", default=None
        ),
    ) -> Response:
        """
        Delete a record from the specified table on a ServiceNow instance.
        """

        if not await ctx_confirm_destructive(ctx, "delete table record"):
            return {"status": "cancelled", "message": "Operation cancelled by user"}
        await ctx_progress(ctx, 0, 100)
        return _client.delete_table_record(
            table=table, table_record_sys_id=table_record_sys_id
        )

    @mcp.tool(
        tags={"table_api"},
    )
    async def get_table(
        table: str = Field(description="The name of the table"),
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
        _client=Depends(get_client),
        ctx: Context = Field(
            description="MCP context for progress reporting", default=None
        ),
    ) -> Response:
        """
        Get records from the specified table on a ServiceNow instance.
        """

        return _client.get_table(
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

    @mcp.tool(
        tags={"table_api"},
    )
    async def get_table_record(
        table: str = Field(description="The name of the table"),
        table_record_sys_id: str = Field(
            description="The sys_id of the record to be retrieved"
        ),
        _client=Depends(get_client),
        ctx: Context = Field(
            description="MCP context for progress reporting", default=None
        ),
    ) -> Response:
        """
        Get a specific record from the specified table on a ServiceNow instance.
        """

        return _client.get_table_record(
            table=table, table_record_sys_id=table_record_sys_id
        )

    @mcp.tool(
        tags={"table_api"},
    )
    async def patch_table_record(
        table: str = Field(description="The name of the table"),
        table_record_sys_id: str = Field(
            description="The sys_id of the record to be updated"
        ),
        data: dict[str, Any] = Field(
            description="Dictionary containing the fields to be updated"
        ),
        _client=Depends(get_client),
        ctx: Context = Field(
            description="MCP context for progress reporting", default=None
        ),
    ) -> Response:
        """
        Partially update a record in the specified table on a ServiceNow instance.
        """

        return _client.patch_table_record(
            table=table, table_record_sys_id=table_record_sys_id, data=data
        )

    @mcp.tool(
        tags={"table_api"},
    )
    async def update_table_record(
        table: str = Field(description="The name of the table"),
        table_record_sys_id: str = Field(
            description="The sys_id of the record to be updated"
        ),
        data: dict[str, Any] = Field(
            description="Dictionary containing the fields to be updated"
        ),
        _client=Depends(get_client),
        ctx: Context = Field(
            description="MCP context for progress reporting", default=None
        ),
    ) -> Response:
        """
        Fully update a record in the specified table on a ServiceNow instance.
        """

        return _client.update_table_record(
            table=table, table_record_sys_id=table_record_sys_id, data=data
        )

    @mcp.tool(
        tags={"table_api"},
    )
    async def add_table_record(
        table: str = Field(description="The name of the table"),
        data: dict[str, Any] = Field(
            description="Dictionary containing the field values for the new record"
        ),
        _client=Depends(get_client),
        ctx: Context = Field(
            description="MCP context for progress reporting", default=None
        ),
    ) -> Response:
        """
        Add a new record to the specified table on a ServiceNow instance.
        """

        return _client.add_table_record(table=table, data=data)


def register_auth_tools(mcp: FastMCP):
    @mcp.tool(
        tags={"auth"},
    )
    async def refresh_auth_token(
        _client=Depends(get_client),
        ctx: Context = Field(
            description="MCP context for progress reporting", default=None
        ),
    ) -> Response:
        """
        Refreshes the authentication token for the ServiceNow client.
        """

        return _client.refresh_auth_token()


def register_custom_api_tools(mcp: FastMCP):
    @mcp.tool(
        tags={"custom_api"},
    )
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
        _client=Depends(get_client),
        ctx: Context = Field(
            description="MCP context for progress reporting", default=None
        ),
    ) -> Response:
        """
        Make a custom API request to a ServiceNow instance.
        """

        return _client.api_request(
            method=method, endpoint=endpoint, data=data, json=json
        )


def register_email_tools(mcp: FastMCP):
    @mcp.tool(tags={"email"})
    async def send_email(
        to: str | list[str] = Field(description="Recipient email addresses"),
        subject: str | None = Field(default=None, description="Email subject"),
        text: str | None = Field(default=None, description="Email body text"),
        html: str | None = Field(default=None, description="Email body HTML"),
        _client=Depends(get_client),
        ctx: Context = Field(
            description="MCP context for progress reporting", default=None
        ),
    ) -> Response:
        """Sends an email via ServiceNow."""
        return _client.send_email(to=to, subject=subject, text=text, html=html)


def register_data_classification_tools(mcp: FastMCP):
    @mcp.tool(tags={"data_classification"})
    async def get_data_classification(
        sys_id: str | None = Field(
            default=None, description="Classification record Sys ID"
        ),
        table_name: str | None = Field(default=None, description="Table name"),
        column_name: str | None = Field(default=None, description="Column name"),
        _client=Depends(get_client),
        ctx: Context = Field(
            description="MCP context for progress reporting", default=None
        ),
    ) -> Response:
        """Retrieves data classification information."""
        return _client.get_data_classification(
            sys_id=sys_id, table_name=table_name, column_name=column_name
        )


def register_attachment_tools(mcp: FastMCP):
    @mcp.tool(tags={"attachment"})
    async def get_attachment(
        sys_id: str = Field(description="Attachment Sys ID"),
        _client=Depends(get_client),
        ctx: Context = Field(
            description="MCP context for progress reporting", default=None
        ),
    ) -> Response:
        """Retrieves attachment metadata."""
        return _client.get_attachment(sys_id=sys_id)

    @mcp.tool(tags={"attachment"})
    async def upload_attachment(
        file_path: str = Field(description="Absolute path to the file to upload"),
        table_name: str = Field(
            description="Table name associated with the attachment"
        ),
        table_sys_id: str = Field(description="Sys ID of the record in the table"),
        file_name: str = Field(description="Name of the file"),
        content_type: str | None = Field(
            default=None, description="MIME type of the file"
        ),
        _client=Depends(get_client),
        ctx: Context = Field(
            description="MCP context for progress reporting", default=None
        ),
    ) -> Response:
        await ctx_progress(ctx, 0, 100)
        """Uploads an attachment to a record."""
        await ctx_progress(ctx, 100, 100)
        return _client.upload_attachment(
            file_path=file_path,
            table_name=table_name,
            table_sys_id=table_sys_id,
            file_name=file_name,
            content_type=content_type,
        )

    @mcp.tool(tags={"attachment"})
    async def delete_attachment(
        sys_id: str = Field(description="Attachment Sys ID"),
        _client=Depends(get_client),
        ctx: Context = Field(
            description="MCP context for progress reporting", default=None
        ),
    ) -> Response:
        """Deletes an attachment."""
        if not await ctx_confirm_destructive(ctx, "delete attachment"):
            return {"status": "cancelled", "message": "Operation cancelled by user"}
        await ctx_progress(ctx, 0, 100)
        return _client.delete_attachment(sys_id=sys_id)


def register_aggregate_tools(mcp: FastMCP):
    @mcp.tool(tags={"aggregate"})
    async def get_stats(
        table_name: str = Field(description="Table name to aggregate on"),
        query: str | None = Field(default=None, description="Encoded query string"),
        group_by: str | None = Field(default=None, description="Field to group by"),
        stats: str | None = Field(default=None, description="Statistics function"),
        _client=Depends(get_client),
        ctx: Context = Field(
            description="MCP context for progress reporting", default=None
        ),
    ) -> Response:
        """Retrieves aggregate statistics for a table."""
        return _client.get_stats(
            table_name=table_name, query=query, group_by=group_by, stats=stats
        )


def register_activity_subscriptions_tools(mcp: FastMCP):
    @mcp.tool(tags={"activity_subscriptions"})
    async def get_activity_subscriptions(
        sys_id: str | None = Field(
            default=None, description="Activity Subscription Sys ID"
        ),
        _client=Depends(get_client),
        ctx: Context = Field(
            description="MCP context for progress reporting", default=None
        ),
    ) -> Response:
        """Retrieves activity subscriptions."""
        return _client.get_activity_subscriptions(sys_id=sys_id)


def register_account_tools(mcp: FastMCP):
    @mcp.tool(tags={"account"})
    async def get_account(
        sys_id: str | None = Field(default=None, description="Account Sys ID"),
        name: str | None = Field(default=None, description="Account name"),
        number: str | None = Field(default=None, description="Account number"),
        _client=Depends(get_client),
        ctx: Context = Field(
            description="MCP context for progress reporting", default=None
        ),
    ) -> Response:
        """Retrieves CSM account information."""
        return _client.get_account(sys_id=sys_id, name=name, number=number)


def register_hr_tools(mcp: FastMCP):
    @mcp.tool(tags={"hr"})
    async def get_hr_profile(
        sys_id: str | None = Field(default=None, description="HR Profile Sys ID"),
        user: str | None = Field(default=None, description="User Sys ID"),
        _client=Depends(get_client),
        ctx: Context = Field(
            description="MCP context for progress reporting", default=None
        ),
    ) -> Response:
        """Retrieves HR profile information."""
        return _client.get_hr_profile(sys_id=sys_id, user=user)


def register_metricbase_tools(mcp: FastMCP):
    @mcp.tool(tags={"metricbase"})
    async def metricbase_insert(
        table_name: str = Field(description="Table name"),
        sys_id: str = Field(description="Record Sys ID"),
        metric_name: str = Field(description="Metric name"),
        values: list[Any] = Field(description="Values to insert"),
        start_time: str | None = Field(default=None, description="Start time"),
        end_time: str | None = Field(default=None, description="End time"),
        _client=Depends(get_client),
        ctx: Context = Field(
            description="MCP context for progress reporting", default=None
        ),
    ) -> Response:
        """Inserts time series data into MetricBase."""
        return _client.metricbase_insert(
            table_name=table_name,
            sys_id=sys_id,
            metric_name=metric_name,
            values=values,
            start_time=start_time,
            end_time=end_time,
        )


def register_service_qualification_tools(mcp: FastMCP):
    @mcp.tool(tags={"service_qualification"})
    async def check_service_qualification(
        description: str | None = Field(default=None, description="Description"),
        externalId: str | None = Field(default=None, description="External ID"),
        relatedParty: list[dict[str, Any]] = Field(
            default=None, description="List of related parties"
        ),
        service_qualitification_item: list[dict[str, Any]] = Field(
            default=None, description="List of qualification items"
        ),
        _client=Depends(get_client),
        ctx: Context = Field(
            description="MCP context for progress reporting", default=None
        ),
    ) -> Response:
        """Creates a technical service qualification request."""
        return _client.check_service_qualification(
            description=description,
            externalId=externalId,
            relatedParty=relatedParty,
            service_qualitification_item=service_qualitification_item,
        )

    @mcp.tool(tags={"service_qualification"})
    async def get_service_qualification(
        id: str | None = Field(default=None, description="Qualification Request ID"),
        state: str | None = Field(default=None, description="Filter by state"),
        _client=Depends(get_client),
        ctx: Context = Field(
            description="MCP context for progress reporting", default=None
        ),
    ) -> Response:
        """Retrieves a service qualification request."""
        return _client.get_service_qualification(id=id, state=state)

    @mcp.tool(tags={"service_qualification"})
    async def process_service_qualification_result(
        service_qualitification_item: list[dict[str, Any]] = Field(
            description="Items to process"
        ),
        description: str | None = Field(default=None, description="Description"),
        _client=Depends(get_client),
        ctx: Context = Field(
            description="MCP context for progress reporting", default=None
        ),
    ) -> Response:
        """Processes a service qualification result."""
        return _client.process_service_qualification_result(
            service_qualitification_item=service_qualitification_item,
            description=description,
        )


def register_ppm_tools(mcp: FastMCP):
    @mcp.tool(tags={"ppm"})
    async def insert_cost_plans(
        plans: list[dict[str, Any]] = Field(description="List of cost plans"),
        _client=Depends(get_client),
        ctx: Context = Field(
            description="MCP context for progress reporting", default=None
        ),
    ) -> Response:
        """Creates cost plans."""
        return _client.insert_cost_plans(plans=plans)

    @mcp.tool(tags={"ppm"})
    async def insert_project_tasks(
        short_description: str = Field(description="Short description"),
        start_date: str | None = Field(default=None, description="Start date"),
        end_date: str | None = Field(default=None, description="End date"),
        child_tasks: list[dict[str, Any]] | None = Field(
            default=None, description="Child tasks"
        ),
        dependencies: list[dict[str, Any]] | None = Field(
            default=None, description="Dependencies"
        ),
        _client=Depends(get_client),
        ctx: Context = Field(
            description="MCP context for progress reporting", default=None
        ),
    ) -> Response:
        """Creates a project and associated project tasks."""
        return _client.insert_project_tasks(
            short_description=short_description,
            start_date=start_date,
            end_date=end_date,
            child_tasks=child_tasks,
            dependencies=dependencies,
        )


def register_product_inventory_tools(mcp: FastMCP):
    @mcp.tool(tags={"product_inventory"})
    async def get_product_inventory(
        customer: str | None = Field(default=None, description="Customer Sys ID"),
        place_id: str | None = Field(default=None, description="Location ID"),
        status: str | None = Field(default=None, description="Status filter"),
        limit: int | None = Field(default=20, description="Limit"),
        offset: int | None = Field(default=0, description="Offset"),
        _client=Depends(get_client),
        ctx: Context = Field(
            description="MCP context for progress reporting", default=None
        ),
    ) -> Response:
        """Retrieves product inventory."""
        return _client.get_product_inventory(
            customer=customer,
            place_id=place_id,
            status=status,
            limit=limit,
            offset=offset,
        )

    @mcp.tool(tags={"product_inventory"})
    async def delete_product_inventory(
        id: str = Field(description="Product Inventory Sys ID"),
        _client=Depends(get_client),
        ctx: Context = Field(
            description="MCP context for progress reporting", default=None
        ),
    ) -> Response:
        """Deletes a product inventory record."""
        if not await ctx_confirm_destructive(ctx, "delete product inventory"):
            return {"status": "cancelled", "message": "Operation cancelled by user"}
        await ctx_progress(ctx, 0, 100)
        return _client.delete_product_inventory(id=id)


def register_prompts(mcp: FastMCP):
    @mcp.prompt
    def create_incident_prompt(
        short_description: str,
        description: str,
        priority: int = 3,
    ) -> str:
        """
        Generates a prompt for creating a ServiceNow incident.
        """
        return (
            f"Create a new ServiceNow incident with short description: '{short_description}', "
            f"full description: '{description}', and priority: {priority}. "
            f"Use the add_table_record tool with table='incident'."
        )

    @mcp.prompt
    def get_incident_with_fields_prompt(sysparm_fields: str) -> str:
        """
        Generates a prompt for getting ServiceNow Incidents with certain fields
        """
        return (
            f"Get the incidents from ServiceNow and display them with the following fields: "
            f"[{sysparm_fields}] in a table format"
        )

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
        return (
            f"Query the ServiceNow table '{table}' "
            f"with sysparm_query: '{sysparm_query}' and sysparm_fields: '{sysparm_fields}'. "
            f"Use the get_table tool with appropriate parameters."
        )


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
                    print("Using incoming JWT for OpenAPI import")

                else:
                    username = args.openapi_username or os.getenv("OPENAPI_USERNAME")
                    password = args.openapi_password or os.getenv("OPENAPI_PASSWORD")
                    client_id = args.openapi_client_id or os.getenv("OPENAPI_CLIENT_ID")
                    client_secret = args.openapi_client_secret or os.getenv(
                        "OPENAPI_CLIENT_SECRET"
                    )

                    if not (username and password) and not (
                        client_id and client_secret
                    ):
                        raise ValueError(
                            "OpenAPI import requires either --openapi-use-token "
                            "or (username+password) or (client_id+client_secret)"
                        )

                api = get_client()
                base_url = args.openapi_base_url or api.url

                async with httpx.AsyncClient(
                    base_url=base_url,
                    headers=api.headers,
                    verify=api.verify,
                ) as client:
                    openapi_mcp = FastMCP.from_openapi(
                        openapi_spec=spec, client=client, name="OpenAPI Tools"
                    )
                    tools = await openapi_mcp.get_tools()
                    resources = await openapi_mcp.get_resources()
                    return tools, resources

            print("Importing OpenAPI tools...")
            imported_tools, imported_resources = asyncio.run(_load_openapi_tools())
            print(
                f"Imported {len(imported_tools)} tools, {len(imported_resources)} resources"
            )

            for tool in imported_tools:
                mcp.add_tool(tool)
            for resource in imported_resources:
                mcp.add_resource(resource)

        except Exception as exc:
            print(f"OpenAPI import failed: {exc}")
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
    return mcp, args, middlewares, registered_tags, imported_tools


def mcp_server() -> None:
    mcp, args, middlewares, registered_tags, imported_tools = get_mcp_instance()

    print("\nStarting ServiceNow MCP Server")
    print(f"  Transport: {args.transport.upper()}", file=sys.stderr)
    print(f"  Auth: {args.auth_type}", file=sys.stderr)
    print(
        f"  Delegation: {'ON' if config['enable_delegation'] else 'OFF'}",
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
