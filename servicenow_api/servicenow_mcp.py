#!/usr/bin/python
# coding: utf-8
import asyncio
import json
import os
import argparse
import sys
import logging
from threading import local
from typing import Optional, List, Dict, Any, Union

import httpx
import requests
from eunomia_mcp.middleware import EunomiaMcpMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse
from fastmcp.dependencies import Depends
from pydantic import Field
from fastmcp import FastMCP, Context
from fastmcp.server.auth.oidc_proxy import OIDCProxy
from fastmcp.server.auth import OAuthProxy, RemoteAuthProvider
from fastmcp.server.auth.providers.jwt import JWTVerifier, StaticTokenVerifier
from fastmcp.server.middleware.logging import LoggingMiddleware
from fastmcp.server.middleware.timing import TimingMiddleware
from fastmcp.server.middleware.rate_limiting import RateLimitingMiddleware
from fastmcp.server.middleware.error_handling import ErrorHandlingMiddleware
from fastmcp.utilities.logging import get_logger
from servicenow_api.servicenow_api import Api
from servicenow_api.servicenow_models import Response
from servicenow_api.utils import to_integer, to_boolean
from servicenow_api.middlewares import UserTokenMiddleware, JWTClaimsLoggingMiddleware

__version__ = "1.5.9"

logger = get_logger(name="TokenMiddleware")
logger.setLevel(logging.DEBUG)

config = {
    "enable_delegation": to_boolean(os.environ.get("ENABLE_DELEGATION", "False")),
    "audience": os.environ.get("SERVICENOW_AUDIENCE", None),
    "delegated_scopes": os.environ.get("DELEGATED_SCOPES", "api"),
    "token_endpoint": None,  # Will be fetched dynamically from OIDC config
    "oidc_client_id": os.environ.get("OIDC_CLIENT_ID", None),
    "oidc_client_secret": os.environ.get("OIDC_CLIENT_SECRET", None),
    "oidc_config_url": os.environ.get("OIDC_CONFIG_URL", None),
    "jwt_jwks_uri": os.getenv("FASTMCP_SERVER_AUTH_JWT_JWKS_URI", None),
    "jwt_issuer": os.getenv("FASTMCP_SERVER_AUTH_JWT_ISSUER", None),
    "jwt_audience": os.getenv("FASTMCP_SERVER_AUTH_JWT_AUDIENCE", None),
    "jwt_algorithm": os.getenv("FASTMCP_SERVER_AUTH_JWT_ALGORITHM", None),
    "jwt_secret": os.getenv("FASTMCP_SERVER_AUTH_JWT_PUBLIC_KEY", None),
    "jwt_required_scopes": os.getenv("FASTMCP_SERVER_AUTH_JWT_REQUIRED_SCOPES", None),
}

DEFAULT_TRANSPORT = os.getenv("TRANSPORT", "stdio")
DEFAULT_HOST = os.getenv("HOST", "0.0.0.0")
DEFAULT_PORT = to_integer(string=os.getenv("PORT", "8000"))


def get_client() -> Api:
    """
    Single entry point for ServiceNow clients.

    Auto-detects auth method:
    1. Delegation → Exchanges MCP token
    2. Basic auth → username/password (env fallback)
    """
    instance = os.getenv("SERVICENOW_INSTANCE")
    if not instance:
        raise RuntimeError("SERVICENOW_INSTANCE not set")

    verify = True

    # === Auto-extract MCP token ===
    mcp_token = getattr(local, "user_token", None)

    # === Delegation ===
    if config.get("enable_delegation", False) and mcp_token:
        logger.info("Delegating MCP token to ServiceNow")
        exchange_data = {
            "grant_type": "urn:ietf:params:oauth:grant-type:token-exchange",
            "subject_token": mcp_token,
            "subject_token_type": "urn:ietf:params:oauth:token-type:access_token",
            "requested_token_type": "urn:ietf:params:oauth:token-type:access_token",
            "audience": config["audience"],
            "scope": config["delegated_scopes"],
        }
        try:
            resp = requests.post(
                config["token_endpoint"],
                data=exchange_data,
                auth=(config["oidc_client_id"], config["oidc_client_secret"]),
                verify=verify,
            )
            resp.raise_for_status()
            sn_token = resp.json()["access_token"]
            return Api(url=instance, token=sn_token, verify=verify)
        except Exception as e:
            print(f"Delegation failed: {e}")
            logger.error("Delegation failed", extra={"error": str(e)})
            raise

    # === Basic auth (env) ===
    username = os.getenv("SERVICENOW_USERNAME")
    password = os.getenv("SERVICENOW_PASSWORD")
    client_id = os.getenv("SERVICENOW_CLIENT_ID")
    client_secret = os.getenv("SERVICENOW_CLIENT_SECRET")

    if username or password:
        return Api(
            url=instance,
            username=username,
            password=password,
            client_id=client_id,
            client_secret=client_secret,
            verify=verify,
        )

    # === Error ===
    raise ValueError(
        "No auth method: Provide token, enable delegation, or set SERVICENOW_USERNAME/PASSWORD"
    )


def register_tools(mcp: FastMCP):
    logger.info("DEBUG: Executing register_tools...")

    @mcp.custom_route("/health", methods=["GET"])
    async def health_check(request: Request) -> JSONResponse:
        return JSONResponse({"status": "OK"})

    # Application Service Tools
    @mcp.tool(
        tags={"application"},
    )
    async def get_application(
        application_id: str = Field(
            description="The unique identifier of the application to retrieve"
        ),
        _client=Depends(get_client),
    ) -> Response:
        """
        Retrieves details of a specific application from a ServiceNow instance by its unique identifier.
        """
        return _client.get_application(application_id)

    # CMDB Tools
    @mcp.tool(
        tags={"cmdb"},
    )
    async def get_cmdb(
        cmdb_id: str = Field(
            description="The unique identifier of the CMDB record to retrieve"
        ),
        _client=Depends(get_client),
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
    ) -> Response:
        """
        Deletes the relation for the specified configuration item (CI).
        """
        return _client.delete_cmdb_relation(
            className=className, sys_id=sys_id, rel_sys_id=rel_sys_id
        )

    @mcp.tool(
        tags={"cmdb"},
    )
    async def get_cmdb_instances(
        className: str = Field(description="CMDB class name"),
        sysparm_limit: Optional[str] = Field(
            default="10000", description="Maximum number of records to return"
        ),
        sysparm_offset: Optional[str] = Field(
            default="0", description="Starting record index"
        ),
        sysparm_query: Optional[str] = Field(
            default=None, description="Encoded query used to filter the result set"
        ),
        _client=Depends(get_client),
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
        attributes: Optional[Dict] = Field(
            default=None, description="Data attributes to define in the CI record"
        ),
        inbound_relations: Optional[List[Dict]] = Field(
            default=None, description="List of inbound relations"
        ),
        outbound_relations: Optional[List[Dict]] = Field(
            default=None, description="List of outbound relations"
        ),
        _client=Depends(get_client),
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
        attributes: Optional[Dict] = Field(
            default=None, description="Data attributes to replace"
        ),
        ctx: Context = None,
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
        attributes: Optional[Dict] = Field(
            default=None, description="Data attributes to replace"
        ),
        ctx: Context = None,
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
        inbound_relations: Optional[List[Dict]] = Field(
            default=None, description="List of inbound relations"
        ),
        outbound_relations: Optional[List[Dict]] = Field(
            default=None, description="List of outbound relations"
        ),
        _client=Depends(get_client),
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
        records: List[Dict] = Field(description="Array of objects to ingest"),
        _client=Depends(get_client),
    ) -> Response:
        """
        Inserts records into the Import Set table associated with the data source.
        """
        return _client.ingest_cmdb_data(
            data_source_sys_id=data_source_sys_id, records=records
        )

    # CI/CD Tools
    @mcp.tool(
        tags={"cicd"},
    )
    async def batch_install_result(
        result_id: str = Field(
            description="The ID associated with the batch installation result"
        ),
        _client=Depends(get_client),
    ) -> Response:
        """
        Retrieves the result of a batch installation process in ServiceNow by result ID.
        """

        return _client.batch_install_result(result_id=result_id)

    @mcp.tool(
        tags={"cicd"},
    )
    async def instance_scan_progress(
        progress_id: str = Field(
            description="The ID associated with the instance scan progress"
        ),
        _client=Depends(get_client),
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
        notes: Optional[str] = Field(
            default=None, description="Additional notes for the batch installation"
        ),
        _client=Depends(get_client),
    ) -> Response:
        """
        Initiates a batch installation of specified packages in ServiceNow with optional notes.
        """

        return _client.batch_install(name=name, packages=packages, notes=notes)

    @mcp.tool(
        tags={"cicd"},
    )
    async def batch_rollback(
        rollback_id: str = Field(
            description="The ID associated with the batch rollback"
        ),
        _client=Depends(get_client),
    ) -> Response:
        """
        Performs a rollback of a batch installation in ServiceNow using the rollback ID.
        """

        return _client.batch_rollback(rollback_id=rollback_id)

    @mcp.tool(
        tags={"cicd"},
    )
    async def app_repo_install(
        app_sys_id: str = Field(
            description="The sys_id of the application to be installed"
        ),
        scope: str = Field(description="The scope of the application"),
        auto_upgrade_base_app: Optional[bool] = Field(
            default=None,
            description="Flag indicating whether to auto-upgrade the base app",
        ),
        base_app_version: Optional[str] = Field(
            default=None, description="The version of the base app"
        ),
        version: Optional[str] = Field(
            default=None, description="The version of the application to be installed"
        ),
        _client=Depends(get_client),
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
        dev_notes: Optional[str] = Field(
            default=None, description="Development notes for the published version"
        ),
        version: Optional[str] = Field(
            default=None, description="The version of the application to be published"
        ),
        _client=Depends(get_client),
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
        sys_ids: List[str] = Field(
            description="List of sys_ids representing app_scope_sys_ids for the suite scan"
        ),
        scan_type: str = Field(
            default="scoped_apps", description="Type of scan to be performed"
        ),
        _client=Depends(get_client),
    ) -> Response:
        """
        Runs a scan on a specified suite with a list of sys_ids and scan type in ServiceNow.
        """

        return _client.suite_scan(
            suite_sys_id=suite_sys_id, sys_ids=sys_ids, scan_type=scan_type
        )

    # Plugin and Update Set Tools
    @mcp.tool(
        tags={"plugins"},
    )
    async def activate_plugin(
        plugin_id: str = Field(description="The ID of the plugin to be activated"),
        _client=Depends(get_client),
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
    ) -> Response:
        """
        Rolls back a specified plugin in ServiceNow to its previous state by plugin ID.
        """

        return _client.rollback_plugin(plugin_id=plugin_id)

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
        auto_upgrade_base_app: Optional[bool] = Field(
            default=None,
            description="Flag indicating whether to auto-upgrade the base app",
        ),
        _client=Depends(get_client),
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
        credential_sys_id: Optional[str] = Field(
            default=None,
            description="The sys_id of the credential to be used for the import",
        ),
        mid_server_sys_id: Optional[str] = Field(
            default=None,
            description="The sys_id of the MID Server to be used for the import",
        ),
        branch_name: Optional[str] = Field(
            default=None, description="The name of the branch to be imported"
        ),
        auto_upgrade_base_app: Optional[bool] = Field(
            default=None,
            description="Flag indicating whether to auto-upgrade the base app",
        ),
        _client=Depends(get_client),
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
        browser_name: Optional[str] = Field(
            default=None, description="The name of the browser for the test run"
        ),
        browser_version: Optional[str] = Field(
            default=None, description="The version of the browser for the test run"
        ),
        os_name: Optional[str] = Field(
            default=None,
            description="The name of the operating system for the test run",
        ),
        os_version: Optional[str] = Field(
            default=None,
            description="The version of the operating system for the test run",
        ),
        _client=Depends(get_client),
    ) -> Response:
        """
        Executes a test suite in ServiceNow with specified browser and OS configurations.
        """

        return _client.run_test_suite(
            test_suite_sys_id=test_suite_sys_id,
            test_suite_name=test_suite_name,
            browser_name=browser_name,
            browser_version=browser_version,
            os_name=os_name,
            os_version=os_version,
        )

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
        description: Optional[str] = Field(
            default=None, description="Description of the update set"
        ),
        _client=Depends(get_client),
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
        update_source_id: Optional[str] = Field(
            default=None, description="Sys_id of the remote instance record"
        ),
        update_source_instance_id: Optional[str] = Field(
            default=None, description="Instance ID of the remote instance"
        ),
        auto_preview: Optional[bool] = Field(
            default=None,
            description="Flag that indicates whether to automatically preview the update set after retrieval",
        ),
        cleanup_retrieved: Optional[bool] = Field(
            default=None,
            description="Flag that indicates whether to remove the existing retrieved update set from the instance",
        ),
        _client=Depends(get_client),
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
        force_commit: Optional[str] = Field(
            default=None,
            description="Flag that indicates whether to force commit the update set",
        ),
        _client=Depends(get_client),
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
        remote_update_set_ids: List[str] = Field(
            description="List of sys_ids associated with update sets to commit. Sys_ids are committed in the order given"
        ),
        force_commit: Optional[str] = Field(
            default=None,
            description="Flag that indicates whether to force commit the update sets",
        ),
        _client=Depends(get_client),
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
        rollback_installs: Optional[bool] = Field(
            default=None,
            description="Flag that indicates whether to rollback the batch installation performed during the update set commit",
        ),
        _client=Depends(get_client),
    ) -> Response:
        """
        Backs out an update set in ServiceNow with an option to rollback installations.
        """

        return _client.update_set_back_out(
            update_set_id=update_set_id, rollback_installs=rollback_installs
        )

    # Batch API Tools
    @mcp.tool(
        tags={"batch"},
    )
    async def batch_request(
        rest_requests: List[Dict] = Field(
            description="List of requests to execute. Each item must correspond to BatchRequestItem model."
        ),
        batch_request_id: Optional[str] = Field(
            default=None, description="Client provided batch ID"
        ),
        _client=Depends(get_client),
    ) -> Response:
        """
        Sends multiple REST API requests in a single call.
        """
        return _client.batch_request(
            batch_request_id=batch_request_id, rest_requests=rest_requests
        )

    # Change Management Tools
    @mcp.tool(
        tags={"change_management"},
    )
    async def get_change_requests(
        order: Optional[str] = Field(
            default=None, description="Ordering parameter for sorting results"
        ),
        name_value_pairs: Optional[str] = Field(
            default=None,
            description="Dictionary of name-value pairs for filtering records entered as a string",
        ),
        sysparm_query: Optional[str] = Field(
            default=None, description="Query parameter for filtering results"
        ),
        text_search: Optional[str] = Field(
            default=None, description="Text search parameter for searching results"
        ),
        change_type: Optional[str] = Field(
            default=None,
            description="Type of change (emergency, normal, standard, model)",
        ),
        sysparm_offset: Optional[int] = Field(
            default=None, description="Offset for pagination"
        ),
        sysparm_limit: Optional[int] = Field(
            default=os.environ.get("SERVICENOW_RETURN_LIMIT", to_integer(string="5")),
            description="Limit for pagination",
        ),
        _client=Depends(get_client),
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
        order: Optional[str] = Field(
            default=None, description="Ordering parameter for sorting results"
        ),
        name_value_pairs: Optional[str] = Field(
            default=None,
            description="Dictionary of name-value pairs for filtering records entered as a string",
        ),
        sysparm_query: Optional[str] = Field(
            default=None, description="Query parameter for filtering results"
        ),
        text_search: Optional[str] = Field(
            default=None, description="Text search parameter for searching results"
        ),
        sysparm_offset: Optional[int] = Field(
            default=None, description="Offset for pagination"
        ),
        sysparm_limit: Optional[int] = Field(
            default=os.environ.get("SERVICENOW_RETURN_LIMIT", to_integer(string="5")),
            description="Limit for pagination",
        ),
        _client=Depends(get_client),
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
        change_type: Optional[str] = Field(
            default=None, description="Type of change (emergency, normal, standard)"
        ),
        _client=Depends(get_client),
        name_value_pairs: Optional[str] = Field(
            default=None,
            description="Dictionary of name-value pairs for filtering records entered as a string",
        ),
        sysparm_display_value: Optional[str] = Field(
            default=None,
            description="Display values for reference fields ('true', 'false', or 'all')",
        ),
        sysparm_exclude_reference_link: Optional[bool] = Field(
            default=None, description="Exclude reference links in the response"
        ),
        sysparm_fields: Optional[str] = Field(
            default=None,
            description="Comma-separated list of field names to include in the response",
        ),
        sysparm_limit: Optional[int] = Field(
            default=os.environ.get("SERVICENOW_RETURN_LIMIT", to_integer(string="5")),
            description="Maximum number of records to return",
        ),
        sysparm_no_count: Optional[bool] = Field(
            default=None,
            description="Do not include the total number of records in the response",
        ),
        sysparm_offset: Optional[int] = Field(
            default=None,
            description="Number of records to skip before starting the retrieval",
        ),
        sysparm_query: Optional[str] = Field(
            default=None, description="Encoded query string for filtering records"
        ),
        sysparm_query_category: Optional[str] = Field(
            default=None, description="Category to which the query belongs"
        ),
        sysparm_query_no_domain: Optional[bool] = Field(
            default=None, description="Exclude records based on domain separation"
        ),
        sysparm_suppress_pagination_header: Optional[bool] = Field(
            default=None, description="Suppress pagination headers in the response"
        ),
        sysparm_view: Optional[str] = Field(
            default=None, description="Display style ('desktop', 'mobile', or 'both')"
        ),
    ) -> Response | None:
        """
        Retrieves details of a specific change request in ServiceNow by sys_id and type.
        """

        if change_request_id:
            # Smart check: if it looks like a number (starts with INC), treat as query
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
        order: Optional[str] = Field(
            default=None, description="Ordering parameter for sorting results"
        ),
        name_value_pairs: Optional[str] = Field(
            default=None,
            description="Dictionary of name-value pairs for filtering records entered as a string",
        ),
        sysparm_query: Optional[str] = Field(
            default=None, description="Query parameter for filtering results"
        ),
        text_search: Optional[str] = Field(
            default=None, description="Text search parameter for searching results"
        ),
        sysparm_offset: Optional[int] = Field(
            default=None, description="Offset for pagination"
        ),
        sysparm_limit: Optional[int] = Field(
            default=os.environ.get("SERVICENOW_RETURN_LIMIT", to_integer(string="5")),
            description="Limit for pagination",
        ),
        _client=Depends(get_client),
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
        order: Optional[str] = Field(
            default=None, description="Ordering parameter for sorting results"
        ),
        name_value_pairs: Optional[str] = Field(
            default=None,
            description="Dictionary of name-value pairs for filtering records entered as a string",
        ),
        sysparm_query: Optional[str] = Field(
            default=None, description="Query parameter for filtering results"
        ),
        text_search: Optional[str] = Field(
            default=None, description="Text search parameter for searching results"
        ),
        change_type: Optional[str] = Field(
            default=None,
            description="Type of change (emergency, normal, standard, model)",
        ),
        sysparm_offset: Optional[int] = Field(
            default=None, description="Offset for pagination"
        ),
        sysparm_limit: Optional[int] = Field(
            default=os.environ.get("SERVICENOW_RETURN_LIMIT", to_integer(string="5")),
            description="Limit for pagination",
        ),
        _client=Depends(get_client),
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
    ) -> Response:
        """
        Retrieves details of a change request worker in ServiceNow by sys_id.
        """

        return _client.get_change_request_worker(worker_sys_id=worker_sys_id)

    @mcp.tool(
        tags={"change_management"},
    )
    async def create_change_request(
        name_value_pairs: Optional[str] = Field(
            default=None,
            description="Dictionary of name-value pairs for filtering records entered as a string",
        ),
        change_type: Optional[str] = Field(
            default="normal", description="Type of change (emergency, normal, standard)"
        ),
        standard_change_template_id: Optional[str] = Field(
            default=None,
            description="Sys ID of the standard change request template (if applicable)",
        ),
        _client=Depends(get_client),
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
        data: Dict[str, str] = Field(
            description="Name-value pairs providing details for the new task"
        ),
        _client=Depends(get_client),
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
        cmdb_ci_sys_ids: List[str] = Field(
            description="List of Sys IDs of CIs to associate with the change request"
        ),
        association_type: str = Field(
            description="Type of association (affected, impacted, offering)"
        ),
        refresh_impacted_services: Optional[bool] = Field(
            default=None,
            description="Flag to refresh impacted services (applicable for 'affected' association)",
        ),
        _client=Depends(get_client),
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
        name_value_pairs: Optional[str] = Field(
            default=None,
            description="Dictionary of name-value pairs for filtering records entered as a string",
        ),
        change_type: Optional[str] = Field(
            default=None,
            description="Type of change (emergency, normal, standard, model)",
        ),
        _client=Depends(get_client),
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
        name_value_pairs: Optional[str] = Field(
            default=None,
            description="Dictionary of name-value pairs for filtering records entered as a string",
        ),
        _client=Depends(get_client),
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
        change_type: Optional[str] = Field(
            default=None, description="Type of change (emergency, normal, standard)"
        ),
        _client=Depends(get_client),
    ) -> Response:
        """
        Deletes a change request from ServiceNow by sys_id and type.
        """

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
    ) -> Response:
        """
        Deletes a task associated with a change request in ServiceNow.
        """

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
    ) -> Response:
        """
        Deletes a conflict scan for a change request in ServiceNow.
        """

        return _client.delete_change_request_conflict_scan(
            change_request_sys_id=change_request_sys_id, task_sys_id=task_sys_id
        )

    # CI Lifecycle Management Tools
    @mcp.tool(
        tags={"cilifecycle"},
    )
    async def check_ci_lifecycle_compat_actions(
        actionName: str = Field(description="Name of the CI action"),
        otherActionName: str = Field(description="Name of the other CI action"),
        _client=Depends(get_client),
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
    ) -> Response:
        """
        Unregisters an operator for non-workflow users.
        """
        return _client.unregister_ci_lifecycle_operator(req_id=req_id)

    # DevOps Tools
    @mcp.tool(
        tags={"devops"},
    )
    async def check_devops_change_control(
        toolId: str = Field(description="Tool ID"),
        orchestrationTaskName: Optional[str] = Field(
            default=None, description="Orchestration Task Name"
        ),
        toolType: str = Field(default="jenkins", description="Tool Type"),
        orchestrationTaskURL: Optional[str] = Field(
            default=None, description="Orchestration Task URL"
        ),
        testConnection: Optional[bool] = Field(
            default=None, description="Test Connection"
        ),
        _client=Depends(get_client),
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
        artifacts: List[Dict] = Field(description="List of artifacts to register"),
        orchestrationToolId: Optional[str] = Field(
            default=None, description="Orchestration Tool ID"
        ),
        toolId: Optional[str] = Field(default=None, description="Artifact Tool ID"),
        branchName: Optional[str] = Field(default=None, description="Branch Name"),
        pipelineName: Optional[str] = Field(default=None, description="Pipeline Name"),
        projectName: Optional[str] = Field(default=None, description="Project Name"),
        stageName: Optional[str] = Field(default=None, description="Stage Name"),
        taskExecutionNumber: Optional[str] = Field(
            default=None, description="Task Execution Number"
        ),
        _client=Depends(get_client),
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

    # Import Set Tools
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
        data: Dict[str, str] = Field(
            description="Dictionary containing the field values for the new import set record"
        ),
        _client=Depends(get_client),
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
        data: List[Dict[str, str]] = Field(
            description="List of dictionaries containing field values for multiple new import set records"
        ),
        _client=Depends(get_client),
    ) -> Response:
        """
        Inserts multiple records into a specified import set on a ServiceNow instance.
        """

        return _client.insert_multiple_import_sets(table=table, data=data)

    # Incident Tools
    logger.info("DEBUG: Registering get_incidents...")

    @mcp.tool(
        tags={"incidents"},
    )
    async def get_incidents(
        incident_id: Optional[str] = Field(
            default=None,
            description="The sys_id or the incident number (INC######) of the incident record, if retrieving a specific incident",
        ),
        _client=Depends(get_client),
        name_value_pairs: Optional[str] = Field(
            default=None,
            description="Dictionary of name-value pairs for filtering records entered as a string",
        ),
        sysparm_display_value: Optional[str] = Field(
            default=None,
            description="Display values for reference fields ('true', 'false', or 'all')",
        ),
        sysparm_exclude_reference_link: Optional[bool] = Field(
            default=None, description="Exclude reference links in the response"
        ),
        sysparm_fields: Optional[str] = Field(
            default=None,
            description="Comma-separated list of field names to include in the response",
        ),
        sysparm_limit: Optional[int] = Field(
            default=os.environ.get("SERVICENOW_RETURN_LIMIT", to_integer(string="5")),
            description="Maximum number of records to return",
        ),
        sysparm_no_count: Optional[bool] = Field(
            default=None,
            description="Do not include the total number of records in the response",
        ),
        sysparm_offset: Optional[int] = Field(
            default=None,
            description="Number of records to skip before starting the retrieval",
        ),
        sysparm_query: Optional[str] = Field(
            default=None, description="Encoded query string for filtering records"
        ),
        sysparm_query_category: Optional[str] = Field(
            default=None, description="Category to which the query belongs"
        ),
        sysparm_query_no_domain: Optional[bool] = Field(
            default=None, description="Exclude records based on domain separation"
        ),
        sysparm_suppress_pagination_header: Optional[bool] = Field(
            default=None, description="Suppress pagination headers in the response"
        ),
        sysparm_view: Optional[str] = Field(
            default=None, description="Display style ('desktop', 'mobile', or 'both')"
        ),
    ) -> Response | None:
        """
        Retrieves incident records from a ServiceNow instance, optionally by specific incident ID.
        """

        if incident_id:
            # Smart check: if it looks like a number (starts with INC), treat as query
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
        data: Dict[str, str] = Field(
            description="Dictionary containing the field values for the new incident record"
        ),
        _client=Depends(get_client),
    ) -> Response:
        """
        Creates a new incident record on a ServiceNow instance with provided details.
        """
        return _client.create_incident(data=data)

    # Knowledge Management Tools
    @mcp.tool(
        tags={"knowledge_management"},
    )
    async def get_knowledge_articles(
        filter: Optional[str] = Field(
            default=None,
            description="Encoded query to filter the result set (e.g., =, !=, ^, ^OR, LIKE, STARTSWITH, ENDSWITH)",
        ),
        sysparm_fields: Optional[str] = Field(
            default=None,
            description="Comma-separated list of field names to include in the response",
        ),
        sysparm_limit: Optional[int] = Field(
            default=os.environ.get("SERVICENOW_RETURN_LIMIT", to_integer(string="5")),
            description="Maximum number of records to return",
        ),
        sysparm_offset: Optional[int] = Field(
            default=None,
            description="Number of records to skip before starting the retrieval",
        ),
        sysparm_query: Optional[str] = Field(
            default=None, description="Encoded query string for filtering records"
        ),
        sysparm_query_category: Optional[str] = Field(
            default=None, description="Category to which the query belongs"
        ),
        kb: Optional[str] = Field(
            default=None,
            description="Comma-separated list of knowledge base sys_ids to restrict results to",
        ),
        language: Optional[str] = Field(
            default=None,
            description="Comma-separated languages in ISO 639-1 format or 'all' to search all valid languages",
        ),
        _client=Depends(get_client),
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
        filter: Optional[str] = Field(
            default=None,
            description="Encoded query to filter the result set (e.g., =, !=, ^, ^OR, LIKE, STARTSWITH, ENDSWITH)",
        ),
        sysparm_fields: Optional[str] = Field(
            default=None,
            description="Comma-separated list of field names to include in the response",
        ),
        sysparm_limit: Optional[int] = Field(
            default=os.environ.get("SERVICENOW_RETURN_LIMIT", to_integer(string="5")),
            description="Maximum number of records to return",
        ),
        sysparm_search_id: Optional[str] = Field(
            default=None,
            description="Unique identifier of search that returned this article",
        ),
        sysparm_search_rank: Optional[str] = Field(
            default=None, description="Article search rank by click-rate"
        ),
        sysparm_update_view: Optional[bool] = Field(
            default=None,
            description="Update view count and record an entry in the Knowledge Use table",
        ),
        sysparm_offset: Optional[int] = Field(
            default=None,
            description="Number of records to skip before starting the retrieval",
        ),
        sysparm_query: Optional[str] = Field(
            default=None, description="Encoded query string for filtering records"
        ),
        sysparm_query_category: Optional[str] = Field(
            default=None, description="Category to which the query belongs"
        ),
        kb: Optional[str] = Field(
            default=None,
            description="Comma-separated list of knowledge base sys_ids to restrict results to",
        ),
        language: Optional[str] = Field(
            default=None,
            description="Comma-separated languages in ISO 639-1 format or 'all' to search all valid languages",
        ),
        _client=Depends(get_client),
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
        sysparm_fields: Optional[str] = Field(
            default=None,
            description="Comma-separated list of field names to include in the response",
        ),
        sysparm_limit: Optional[int] = Field(
            default=os.environ.get("SERVICENOW_RETURN_LIMIT", to_integer(string="5")),
            description="Maximum number of records to return",
        ),
        sysparm_offset: Optional[int] = Field(
            default=None,
            description="Number of records to skip before starting the retrieval",
        ),
        kb: Optional[str] = Field(
            default=None,
            description="Comma-separated list of knowledge base sys_ids to restrict results to",
        ),
        language: Optional[str] = Field(
            default=None,
            description="Comma-separated languages in ISO 639-1 format or 'all' to search all valid languages",
        ),
        _client=Depends(get_client),
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
        sysparm_fields: Optional[str] = Field(
            default=None,
            description="Comma-separated list of field names to include in the response",
        ),
        sysparm_limit: Optional[int] = Field(
            default=os.environ.get("SERVICENOW_RETURN_LIMIT", to_integer(string="5")),
            description="Maximum number of records to return",
        ),
        sysparm_offset: Optional[int] = Field(
            default=None,
            description="Number of records to skip before starting the retrieval",
        ),
        kb: Optional[str] = Field(
            default=None,
            description="Comma-separated list of knowledge base sys_ids to restrict results to",
        ),
        language: Optional[str] = Field(
            default=None,
            description="Comma-separated languages in ISO 639-1 format or 'all' to search all valid languages",
        ),
        _client=Depends(get_client),
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

    # Table API Tools
    @mcp.tool(
        tags={"table_api"},
    )
    async def delete_table_record(
        table: str = Field(description="The name of the table"),
        table_record_sys_id: str = Field(
            description="The sys_id of the record to be deleted"
        ),
        _client=Depends(get_client),
    ) -> Response:
        """
        Delete a record from the specified table on a ServiceNow instance.
        """

        return _client.delete_table_record(
            table=table, table_record_sys_id=table_record_sys_id
        )

    @mcp.tool(
        tags={"table_api"},
    )
    async def get_table(
        table: str = Field(description="The name of the table"),
        name_value_pairs: Optional[str] = Field(
            default=None,
            description="Dictionary of name-value pairs for filtering records entered as a string",
        ),
        sysparm_display_value: Optional[str] = Field(
            default=None,
            description="Display values for reference fields ('true', 'false', or 'all')",
        ),
        sysparm_exclude_reference_link: Optional[bool] = Field(
            default=None, description="Exclude reference links in the response"
        ),
        sysparm_fields: Optional[str] = Field(
            default=None,
            description="Comma-separated list of field names to include in the response",
        ),
        sysparm_limit: Optional[int] = Field(
            default=os.environ.get("SERVICENOW_RETURN_LIMIT", to_integer(string="5")),
            description="Maximum number of records to return",
        ),
        sysparm_no_count: Optional[bool] = Field(
            default=None,
            description="Do not include the total number of records in the response",
        ),
        sysparm_offset: Optional[int] = Field(
            default=None,
            description="Number of records to skip before starting the retrieval",
        ),
        sysparm_query: Optional[str] = Field(
            default=None, description="Encoded query string for filtering records"
        ),
        sysparm_query_category: Optional[str] = Field(
            default=None, description="Category to which the query belongs"
        ),
        sysparm_query_no_domain: Optional[bool] = Field(
            default=None, description="Exclude records based on domain separation"
        ),
        sysparm_suppress_pagination_header: Optional[bool] = Field(
            default=None, description="Suppress pagination headers in the response"
        ),
        sysparm_view: Optional[str] = Field(
            default=None, description="Display style ('desktop', 'mobile', or 'both')"
        ),
        _client=Depends(get_client),
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
        data: Dict[str, Any] = Field(
            description="Dictionary containing the fields to be updated"
        ),
        _client=Depends(get_client),
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
        data: Dict[str, Any] = Field(
            description="Dictionary containing the fields to be updated"
        ),
        _client=Depends(get_client),
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
        data: Dict[str, Any] = Field(
            description="Dictionary containing the field values for the new record"
        ),
        _client=Depends(get_client),
    ) -> Response:
        """
        Add a new record to the specified table on a ServiceNow instance.
        """

        return _client.add_table_record(table=table, data=data)

    @mcp.tool(
        tags={"auth"},
    )
    async def refresh_auth_token(
        _client=Depends(get_client),
    ) -> Response:
        """
        Refreshes the authentication token for the ServiceNow client.
        """

        return _client.refresh_auth_token()

    # Custom API Tools
    @mcp.tool(
        tags={"custom_api"},
    )
    async def api_request(
        method: str = Field(
            description="The HTTP method to use ('GET', 'POST', 'PUT', 'DELETE')"
        ),
        endpoint: str = Field(description="The API endpoint to send the request to"),
        data: Optional[Dict[str, Any]] = Field(
            default=None,
            description="Data to include in the request body (for non-JSON payloads)",
        ),
        json: Optional[Dict[str, Any]] = Field(
            default=None, description="JSON data to include in the request body"
        ),
        _client=Depends(get_client),
    ) -> Response:
        """
        Make a custom API request to a ServiceNow instance.
        """

        return _client.api_request(
            method=method, endpoint=endpoint, data=data, json=json
        )

    # Email Tools
    @mcp.tool(tags={"email"})
    async def send_email(
        to: Union[str, List[str]] = Field(description="Recipient email addresses"),
        subject: Optional[str] = Field(default=None, description="Email subject"),
        text: Optional[str] = Field(default=None, description="Email body text"),
        html: Optional[str] = Field(default=None, description="Email body HTML"),
        _client=Depends(get_client),
    ) -> Response:
        """Sends an email via ServiceNow."""
        return _client.send_email(to=to, subject=subject, text=text, html=html)

    # Data Classification Tools
    @mcp.tool(tags={"data_classification"})
    async def get_data_classification(
        sys_id: Optional[str] = Field(
            default=None, description="Classification record Sys ID"
        ),
        table_name: Optional[str] = Field(default=None, description="Table name"),
        column_name: Optional[str] = Field(default=None, description="Column name"),
        _client=Depends(get_client),
    ) -> Response:
        """Retrieves data classification information."""
        return _client.get_data_classification(
            sys_id=sys_id, table_name=table_name, column_name=column_name
        )

    # Attachment Tools
    @mcp.tool(tags={"attachment"})
    async def get_attachment(
        sys_id: str = Field(description="Attachment Sys ID"),
        _client=Depends(get_client),
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
        content_type: Optional[str] = Field(
            default=None, description="MIME type of the file"
        ),
        _client=Depends(get_client),
    ) -> Response:
        """Uploads an attachment to a record."""
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
    ) -> Response:
        """Deletes an attachment."""
        return _client.delete_attachment(sys_id=sys_id)

    # Aggregate Tools
    @mcp.tool(tags={"aggregate"})
    async def get_stats(
        table_name: str = Field(description="Table name to aggregate on"),
        query: Optional[str] = Field(default=None, description="Encoded query string"),
        group_by: Optional[str] = Field(default=None, description="Field to group by"),
        stats: Optional[str] = Field(default=None, description="Statistics function"),
        _client=Depends(get_client),
    ) -> Response:
        """Retrieves aggregate statistics for a table."""
        return _client.get_stats(
            table_name=table_name, query=query, group_by=group_by, stats=stats
        )

    # Activity Subscriptions Tools
    @mcp.tool(tags={"activity_subscriptions"})
    async def get_activity_subscriptions(
        sys_id: Optional[str] = Field(
            default=None, description="Activity Subscription Sys ID"
        ),
        _client=Depends(get_client),
    ) -> Response:
        """Retrieves activity subscriptions."""
        return _client.get_activity_subscriptions(sys_id=sys_id)

    # Account Tools
    @mcp.tool(tags={"account"})
    async def get_account(
        sys_id: Optional[str] = Field(default=None, description="Account Sys ID"),
        name: Optional[str] = Field(default=None, description="Account name"),
        number: Optional[str] = Field(default=None, description="Account number"),
        _client=Depends(get_client),
    ) -> Response:
        """Retrieves CSM account information."""
        return _client.get_account(sys_id=sys_id, name=name, number=number)

    # HR Tools
    @mcp.tool(tags={"hr"})
    async def get_hr_profile(
        sys_id: Optional[str] = Field(default=None, description="HR Profile Sys ID"),
        user: Optional[str] = Field(default=None, description="User Sys ID"),
        _client=Depends(get_client),
    ) -> Response:
        """Retrieves HR profile information."""
        return _client.get_hr_profile(sys_id=sys_id, user=user)

    # MetricBase Tools
    @mcp.tool(tags={"metricbase"})
    async def metricbase_insert(
        table_name: str = Field(description="Table name"),
        sys_id: str = Field(description="Record Sys ID"),
        metric_name: str = Field(description="Metric name"),
        values: List[Any] = Field(description="Values to insert"),
        start_time: Optional[str] = Field(default=None, description="Start time"),
        end_time: Optional[str] = Field(default=None, description="End time"),
        _client=Depends(get_client),
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

    # Service Qualification Tools
    @mcp.tool(tags={"service_qualification"})
    async def check_service_qualification(
        description: Optional[str] = Field(default=None, description="Description"),
        externalId: Optional[str] = Field(default=None, description="External ID"),
        relatedParty: List[Dict[str, Any]] = Field(
            default=None, description="List of related parties"
        ),
        service_qualitification_item: List[Dict[str, Any]] = Field(
            default=None, description="List of qualification items"
        ),
        _client=Depends(get_client),
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
        id: Optional[str] = Field(default=None, description="Qualification Request ID"),
        state: Optional[str] = Field(default=None, description="Filter by state"),
        _client=Depends(get_client),
    ) -> Response:
        """Retrieves a service qualification request."""
        return _client.get_service_qualification(id=id, state=state)

    @mcp.tool(tags={"service_qualification"})
    async def process_service_qualification_result(
        service_qualitification_item: List[Dict[str, Any]] = Field(
            description="Items to process"
        ),
        description: Optional[str] = Field(default=None, description="Description"),
        _client=Depends(get_client),
    ) -> Response:
        """Processes a service qualification result."""
        return _client.process_service_qualification_result(
            service_qualitification_item=service_qualitification_item,
            description=description,
        )

    # PPM Tools
    @mcp.tool(tags={"ppm"})
    async def insert_cost_plans(
        plans: List[Dict[str, Any]] = Field(description="List of cost plans"),
        _client=Depends(get_client),
    ) -> Response:
        """Creates cost plans."""
        return _client.insert_cost_plans(plans=plans)

    @mcp.tool(tags={"ppm"})
    async def insert_project_tasks(
        short_description: str = Field(description="Short description"),
        start_date: Optional[str] = Field(default=None, description="Start date"),
        end_date: Optional[str] = Field(default=None, description="End date"),
        child_tasks: Optional[List[Dict[str, Any]]] = Field(
            default=None, description="Child tasks"
        ),
        dependencies: Optional[List[Dict[str, Any]]] = Field(
            default=None, description="Dependencies"
        ),
        _client=Depends(get_client),
    ) -> Response:
        """Creates a project and associated project tasks."""
        return _client.insert_project_tasks(
            short_description=short_description,
            start_date=start_date,
            end_date=end_date,
            child_tasks=child_tasks,
            dependencies=dependencies,
        )

    # Product Inventory Tools
    @mcp.tool(tags={"product_inventory"})
    async def get_product_inventory(
        customer: Optional[str] = Field(default=None, description="Customer Sys ID"),
        place_id: Optional[str] = Field(default=None, description="Location ID"),
        status: Optional[str] = Field(default=None, description="Status filter"),
        limit: Optional[int] = Field(default=20, description="Limit"),
        offset: Optional[int] = Field(default=0, description="Offset"),
        _client=Depends(get_client),
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
    ) -> Response:
        """Deletes a product inventory record."""
        return _client.delete_product_inventory(id=id)


def register_prompts(mcp: FastMCP):
    # Prompts
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


def servicenow_mcp():
    print(f"servicenow_mcp v{__version__}")
    parser = argparse.ArgumentParser(description="ServiceNow MCP Server")
    parser.add_argument(
        "-t",
        "--transport",
        default=DEFAULT_TRANSPORT,
        choices=["stdio", "streamable-http", "sse"],
        help="Transport method: 'stdio', 'streamable-http', or 'sse' [legacy] (default: stdio)",
    )
    parser.add_argument(
        "-s",
        "--host",
        default=DEFAULT_HOST,
        help="Host address for HTTP transport (default: 0.0.0.0)",
    )
    parser.add_argument(
        "-p",
        "--port",
        type=int,
        default=DEFAULT_PORT,
        help="Port number for HTTP transport (default: 8000)",
    )
    parser.add_argument(
        "--auth-type",
        default="none",
        choices=["none", "static", "jwt", "oauth-proxy", "oidc-proxy", "remote-oauth"],
        help="Authentication type for MCP server: 'none' (disabled), 'static' (internal), 'jwt' (external token verification), 'oauth-proxy', 'oidc-proxy', 'remote-oauth' (external) (default: none)",
    )
    # JWT/Token params
    parser.add_argument(
        "--token-jwks-uri", default=None, help="JWKS URI for JWT verification"
    )
    parser.add_argument(
        "--token-issuer", default=None, help="Issuer for JWT verification"
    )
    parser.add_argument(
        "--token-audience", default=None, help="Audience for JWT verification"
    )
    parser.add_argument(
        "--token-algorithm",
        default=os.getenv("FASTMCP_SERVER_AUTH_JWT_ALGORITHM"),
        choices=[
            "HS256",
            "HS384",
            "HS512",
            "RS256",
            "RS384",
            "RS512",
            "ES256",
            "ES384",
            "ES512",
        ],
        help="JWT signing algorithm (required for HMAC or static key). Auto-detected for JWKS.",
    )
    parser.add_argument(
        "--token-secret",
        default=os.getenv("FASTMCP_SERVER_AUTH_JWT_PUBLIC_KEY"),
        help="Shared secret for HMAC (HS*) or PEM public key for static asymmetric verification.",
    )
    parser.add_argument(
        "--token-public-key",
        default=os.getenv("FASTMCP_SERVER_AUTH_JWT_PUBLIC_KEY"),
        help="Path to PEM public key file or inline PEM string (for static asymmetric keys).",
    )
    parser.add_argument(
        "--required-scopes",
        default=os.getenv("FASTMCP_SERVER_AUTH_JWT_REQUIRED_SCOPES"),
        help="Comma-separated list of required scopes (e.g., servicenow.read,servicenow.write).",
    )
    # OAuth Proxy params
    parser.add_argument(
        "--oauth-upstream-auth-endpoint",
        default=None,
        help="Upstream authorization endpoint for OAuth Proxy",
    )
    parser.add_argument(
        "--oauth-upstream-token-endpoint",
        default=None,
        help="Upstream token endpoint for OAuth Proxy",
    )
    parser.add_argument(
        "--oauth-upstream-client-id",
        default=None,
        help="Upstream client ID for OAuth Proxy",
    )
    parser.add_argument(
        "--oauth-upstream-client-secret",
        default=None,
        help="Upstream client secret for OAuth Proxy",
    )
    parser.add_argument(
        "--oauth-base-url", default=None, help="Base URL for OAuth Proxy"
    )
    # OIDC Proxy params
    parser.add_argument(
        "--oidc-config-url", default=None, help="OIDC configuration URL"
    )
    parser.add_argument("--oidc-client-id", default=None, help="OIDC client ID")
    parser.add_argument("--oidc-client-secret", default=None, help="OIDC client secret")
    parser.add_argument("--oidc-base-url", default=None, help="Base URL for OIDC Proxy")
    # Remote OAuth params
    parser.add_argument(
        "--remote-auth-servers",
        default=None,
        help="Comma-separated list of authorization servers for Remote OAuth",
    )
    parser.add_argument(
        "--remote-base-url", default=None, help="Base URL for Remote OAuth"
    )
    # Common
    parser.add_argument(
        "--allowed-client-redirect-uris",
        default=None,
        help="Comma-separated list of allowed client redirect URIs",
    )
    # Eunomia params
    parser.add_argument(
        "--eunomia-type",
        default="none",
        choices=["none", "embedded", "remote"],
        help="Eunomia authorization type: 'none' (disabled), 'embedded' (built-in), 'remote' (external) (default: none)",
    )
    parser.add_argument(
        "--eunomia-policy-file",
        default="mcp_policies.json",
        help="Policy file for embedded Eunomia (default: mcp_policies.json)",
    )
    parser.add_argument(
        "--eunomia-remote-url", default=None, help="URL for remote Eunomia server"
    )
    # Delegation params
    parser.add_argument(
        "--enable-delegation",
        action="store_true",
        default=to_boolean(os.environ.get("ENABLE_DELEGATION", "False")),
        help="Enable OIDC token delegation to ServiceNow",
    )
    parser.add_argument(
        "--audience",
        default=os.environ.get("SERVICENOW_AUDIENCE", None),
        help="Audience for the delegated ServiceNow token",
    )
    parser.add_argument(
        "--delegated-scopes",
        default=os.environ.get("DELEGATED_SCOPES", "api"),
        help="Scopes for the delegated ServiceNow token (space-separated)",
    )
    parser.add_argument(
        "--openapi-file",
        default=None,
        help="Path to the OpenAPI JSON file to import additional tools from",
    )
    parser.add_argument(
        "--openapi-base-url",
        default=None,
        help="Base URL for the OpenAPI client (overrides ServiceNow instance URL)",
    )
    parser.add_argument(
        "--openapi-use-token",
        action="store_true",
        help="Use the incoming Bearer token (from MCP request) to authenticate OpenAPI import",
    )

    parser.add_argument(
        "--openapi-username",
        default=os.getenv("OPENAPI_USERNAME"),
        help="Username for basic auth during OpenAPI import",
    )

    parser.add_argument(
        "--openapi-password",
        default=os.getenv("OPENAPI_PASSWORD"),
        help="Password for basic auth during OpenAPI import",
    )

    parser.add_argument(
        "--openapi-client-id",
        default=os.getenv("OPENAPI_CLIENT_ID"),
        help="OAuth client ID for OpenAPI import",
    )

    parser.add_argument(
        "--openapi-client-secret",
        default=os.getenv("OPENAPI_CLIENT_SECRET"),
        help="OAuth client secret for OpenAPI import",
    )

    args = parser.parse_args()

    if args.port < 0 or args.port > 65535:
        print(f"Error: Port {args.port} is out of valid range (0-65535).")
        sys.exit(1)

    # Update config with CLI arguments
    config["enable_delegation"] = args.enable_delegation
    config["audience"] = args.audience or config["audience"]
    config["delegated_scopes"] = args.delegated_scopes or config["delegated_scopes"]
    config["oidc_config_url"] = args.oidc_config_url or config["oidc_config_url"]
    config["oidc_client_id"] = args.oidc_client_id or config["oidc_client_id"]
    config["oidc_client_secret"] = (
        args.oidc_client_secret or config["oidc_client_secret"]
    )

    # Configure delegation if enabled
    if config["enable_delegation"]:
        if args.auth_type != "oidc-proxy":
            logger.error("Token delegation requires auth-type=oidc-proxy")
            sys.exit(1)
        if not config["audience"]:
            logger.error("audience is required for delegation")
            sys.exit(1)
        if not all(
            [
                config["oidc_config_url"],
                config["oidc_client_id"],
                config["oidc_client_secret"],
            ]
        ):
            logger.error(
                "Delegation requires complete OIDC configuration (oidc-config-url, oidc-client-id, oidc-client-secret)"
            )
            sys.exit(1)

        # Fetch OIDC configuration to get token_endpoint
        try:
            logger.info(
                "Fetching OIDC configuration",
                extra={"oidc_config_url": config["oidc_config_url"]},
            )
            oidc_config_resp = requests.get(config["oidc_config_url"])
            oidc_config_resp.raise_for_status()
            oidc_config = oidc_config_resp.json()
            config["token_endpoint"] = oidc_config.get("token_endpoint")
            if not config["token_endpoint"]:
                logger.error("No token_endpoint found in OIDC configuration")
                raise ValueError("No token_endpoint found in OIDC configuration")
            logger.info(
                "OIDC configuration fetched successfully",
                extra={"token_endpoint": config["token_endpoint"]},
            )
        except Exception as e:
            print(f"Failed to fetch OIDC configuration: {e}")
            logger.error(
                "Failed to fetch OIDC configuration",
                extra={"error_type": type(e).__name__, "error_message": str(e)},
            )
            sys.exit(1)

    # Set auth based on type
    auth = None
    allowed_uris = (
        args.allowed_client_redirect_uris.split(",")
        if args.allowed_client_redirect_uris
        else None
    )

    if args.auth_type == "none":
        auth = None
    elif args.auth_type == "static":
        auth = StaticTokenVerifier(
            tokens={
                "test-token": {"client_id": "test-user", "scopes": ["read", "write"]},
                "admin-token": {"client_id": "admin", "scopes": ["admin"]},
            }
        )
    elif args.auth_type == "jwt":
        # Fallback to env vars if not provided via CLI
        jwks_uri = args.token_jwks_uri or os.getenv("FASTMCP_SERVER_AUTH_JWT_JWKS_URI")
        issuer = args.token_issuer or os.getenv("FASTMCP_SERVER_AUTH_JWT_ISSUER")
        audience = args.token_audience or os.getenv("FASTMCP_SERVER_AUTH_JWT_AUDIENCE")
        algorithm = args.token_algorithm
        secret_or_key = args.token_secret or args.token_public_key
        public_key_pem = None

        if not (jwks_uri or secret_or_key):
            logger.error(
                "JWT auth requires either --token-jwks-uri or --token-secret/--token-public-key"
            )
            sys.exit(1)
        if not (issuer and audience):
            logger.error("JWT requires --token-issuer and --token-audience")
            sys.exit(1)

        # Load static public key from file if path is given
        if args.token_public_key and os.path.isfile(args.token_public_key):
            try:
                with open(args.token_public_key, "r") as f:
                    public_key_pem = f.read()
                logger.info(f"Loaded static public key from {args.token_public_key}")
            except Exception as e:
                print(f"Failed to read public key file: {e}")
                logger.error(f"Failed to read public key file: {e}")
                sys.exit(1)
        elif args.token_public_key:
            public_key_pem = args.token_public_key  # Inline PEM

        # Validation: Conflicting options
        if jwks_uri and (algorithm or secret_or_key):
            logger.warning(
                "JWKS mode ignores --token-algorithm and --token-secret/--token-public-key"
            )

        # HMAC mode
        if algorithm and algorithm.startswith("HS"):
            if not secret_or_key:
                logger.error(f"HMAC algorithm {algorithm} requires --token-secret")
                sys.exit(1)
            if jwks_uri:
                logger.error("Cannot use --token-jwks-uri with HMAC")
                sys.exit(1)
            public_key = secret_or_key
        else:
            public_key = public_key_pem

        # Required scopes
        required_scopes = None
        if args.required_scopes:
            required_scopes = [
                s.strip() for s in args.required_scopes.split(",") if s.strip()
            ]

        try:
            auth = JWTVerifier(
                jwks_uri=jwks_uri,
                public_key=public_key,
                issuer=issuer,
                audience=audience,
                algorithm=(
                    algorithm if algorithm and algorithm.startswith("HS") else None
                ),
                required_scopes=required_scopes,
            )
            logger.info(
                "JWTVerifier configured",
                extra={
                    "mode": (
                        "JWKS"
                        if jwks_uri
                        else (
                            "HMAC"
                            if algorithm and algorithm.startswith("HS")
                            else "Static Key"
                        )
                    ),
                    "algorithm": algorithm,
                    "required_scopes": required_scopes,
                },
            )
        except Exception as e:
            print(f"Failed to initialize JWTVerifier: {e}")
            logger.error(f"Failed to initialize JWTVerifier: {e}")
            sys.exit(1)
    elif args.auth_type == "oauth-proxy":
        if not (
            args.oauth_upstream_auth_endpoint
            and args.oauth_upstream_token_endpoint
            and args.oauth_upstream_client_id
            and args.oauth_upstream_client_secret
            and args.oauth_base_url
            and args.token_jwks_uri
            and args.token_issuer
            and args.token_audience
        ):
            print(
                "oauth-proxy requires oauth-upstream-auth-endpoint, oauth-upstream-token-endpoint, "
                "oauth-upstream-client-id, oauth-upstream-client-secret, oauth-base-url, token-jwks-uri, "
                "token-issuer, token-audience"
            )
            logger.error(
                "oauth-proxy requires oauth-upstream-auth-endpoint, oauth-upstream-token-endpoint, "
                "oauth-upstream-client-id, oauth-upstream-client-secret, oauth-base-url, token-jwks-uri, "
                "token-issuer, token-audience",
                extra={
                    "auth_endpoint": args.oauth_upstream_auth_endpoint,
                    "token_endpoint": args.oauth_upstream_token_endpoint,
                    "client_id": args.oauth_upstream_client_id,
                    "base_url": args.oauth_base_url,
                    "jwks_uri": args.token_jwks_uri,
                    "issuer": args.token_issuer,
                    "audience": args.token_audience,
                },
            )
            sys.exit(1)
        token_verifier = JWTVerifier(
            jwks_uri=args.token_jwks_uri,
            issuer=args.token_issuer,
            audience=args.token_audience,
        )
        auth = OAuthProxy(
            upstream_authorization_endpoint=args.oauth_upstream_auth_endpoint,
            upstream_token_endpoint=args.oauth_upstream_token_endpoint,
            upstream_client_id=args.oauth_upstream_client_id,
            upstream_client_secret=args.oauth_upstream_client_secret,
            token_verifier=token_verifier,
            base_url=args.oauth_base_url,
            allowed_client_redirect_uris=allowed_uris,
        )
    elif args.auth_type == "oidc-proxy":
        if not (
            args.oidc_config_url
            and args.oidc_client_id
            and args.oidc_client_secret
            and args.oidc_base_url
        ):
            logger.error(
                "oidc-proxy requires oidc-config-url, oidc-client-id, oidc-client-secret, oidc-base-url",
                extra={
                    "config_url": args.oidc_config_url,
                    "client_id": args.oidc_client_id,
                    "base_url": args.oidc_base_url,
                },
            )
            sys.exit(1)
        auth = OIDCProxy(
            config_url=args.oidc_config_url,
            client_id=args.oidc_client_id,
            client_secret=args.oidc_client_secret,
            base_url=args.oidc_base_url,
            allowed_client_redirect_uris=allowed_uris,
        )
    elif args.auth_type == "remote-oauth":
        if not (
            args.remote_auth_servers
            and args.remote_base_url
            and args.token_jwks_uri
            and args.token_issuer
            and args.token_audience
        ):
            logger.error(
                "remote-oauth requires remote-auth-servers, remote-base-url, token-jwks-uri, token-issuer, token-audience",
                extra={
                    "auth_servers": args.remote_auth_servers,
                    "base_url": args.remote_base_url,
                    "jwks_uri": args.token_jwks_uri,
                    "issuer": args.token_issuer,
                    "audience": args.token_audience,
                },
            )
            sys.exit(1)
        auth_servers = [url.strip() for url in args.remote_auth_servers.split(",")]
        token_verifier = JWTVerifier(
            jwks_uri=args.token_jwks_uri,
            issuer=args.token_issuer,
            audience=args.token_audience,
        )
        auth = RemoteAuthProvider(
            token_verifier=token_verifier,
            authorization_servers=auth_servers,
            base_url=args.remote_base_url,
        )

    # === 2. Build Middleware List ===
    middlewares: List[
        Union[
            UserTokenMiddleware,
            ErrorHandlingMiddleware,
            RateLimitingMiddleware,
            TimingMiddleware,
            LoggingMiddleware,
            JWTClaimsLoggingMiddleware,
            EunomiaMcpMiddleware,
        ]
    ] = [
        ErrorHandlingMiddleware(include_traceback=True, transform_errors=True),
        RateLimitingMiddleware(max_requests_per_second=10.0, burst_capacity=20),
        TimingMiddleware(),
        LoggingMiddleware(),
        JWTClaimsLoggingMiddleware(),
    ]

    if args.openapi_file:
        if config["enable_delegation"]:
            raise ValueError("OpenAPI import not supported with delegation enabled")

        try:
            with open(args.openapi_file, "r") as f:
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
                    # Use CLI/env credentials
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

                instance = os.getenv("SERVICENOW_INSTANCE")
                if not instance:
                    raise ValueError("SERVICENOW_INSTANCE required")

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

        except Exception as exc:
            print(f"OpenAPI import failed: {exc}")
            logger.error("OpenAPI import failed", extra={"error": str(exc)})
            sys.exit(1)
    else:
        imported_tools, imported_resources = [], []

    if config["enable_delegation"] or args.auth_type == "jwt":
        middlewares.insert(0, UserTokenMiddleware(config=config))  # Must be first

    if args.eunomia_type in ["embedded", "remote"]:
        try:
            from eunomia_mcp import create_eunomia_middleware

            policy_file = args.eunomia_policy_file or "mcp_policies.json"
            eunomia_endpoint = (
                args.eunomia_remote_url if args.eunomia_type == "remote" else None
            )
            eunomia_mw = create_eunomia_middleware(
                policy_file=policy_file, eunomia_endpoint=eunomia_endpoint
            )
            middlewares.append(eunomia_mw)
            logger.info(f"Eunomia middleware enabled ({args.eunomia_type})")
        except Exception as e:
            print(f"Failed to load Eunomia middleware: {e}")
            logger.error("Failed to load Eunomia middleware", extra={"error": str(e)})
            sys.exit(1)

    mcp = FastMCP("ServiceNow", auth=auth)
    register_tools(mcp)
    register_prompts(mcp)

    for tool in imported_tools:
        mcp.add_tool(tool)
    for resource in imported_resources:
        mcp.add_resource(resource)

    for mw in middlewares:
        mcp.add_middleware(mw)

    print("\nStarting ServiceNow MCP Server")
    print(f"  Transport: {args.transport.upper()}")
    print(f"  Auth: {args.auth_type}")
    print(f"  Delegation: {'ON' if config['enable_delegation'] else 'OFF'}")
    print(f"  Eunomia: {args.eunomia_type}")
    print(f"  Imported OpenAPI Tools: {len(imported_tools)} total\n")

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
    servicenow_mcp()
