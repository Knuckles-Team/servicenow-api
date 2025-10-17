#!/usr/bin/python
# coding: utf-8

import os
import argparse
import sys
import logging
from typing import Optional, List, Dict, Any, Union
from pydantic import Field
from fastmcp import FastMCP
from fastmcp.server.auth.oidc_proxy import OIDCProxy
from fastmcp.server.auth import OAuthProxy, RemoteAuthProvider
from fastmcp.server.auth.providers.jwt import JWTVerifier, StaticTokenVerifier
from fastmcp.server.middleware.logging import LoggingMiddleware
from fastmcp.server.middleware.timing import TimingMiddleware
from fastmcp.server.middleware.rate_limiting import RateLimitingMiddleware
from fastmcp.server.middleware.error_handling import ErrorHandlingMiddleware
from servicenow_api.servicenow_api import Api

mcp = FastMCP("ServiceNow")


def to_boolean(string: Union[str, bool] = None) -> bool:
    if isinstance(string, bool):
        return string
    if not string:
        return False
    normalized = str(string).strip().lower()
    true_values = {"t", "true", "y", "yes", "1"}
    false_values = {"f", "false", "n", "no", "0"}
    if normalized in true_values:
        return True
    elif normalized in false_values:
        return False
    else:
        raise ValueError(f"Cannot convert '{string}' to boolean")


# Application Service Tools
@mcp.tool(
    exclude_args=[
        "servicenow_instance",
        "username",
        "password",
        "client_id",
        "client_secret",
        "verify",
    ],
    tags={"application"},
)
def get_application(
    application_id: str = Field(
        description="The unique identifier of the application to retrieve"
    ),
    servicenow_instance: str = Field(
        default=os.environ.get("SERVICENOW_INSTANCE", None),
        description="The URL of the ServiceNow instance (e.g., https://yourinstance.servicenow.com)",
    ),
    username: str = Field(
        default=os.environ.get("SERVICENOW_USERNAME", None),
        description="Username for basic authentication",
    ),
    password: str = Field(
        default=os.environ.get("SERVICENOW_PASSWORD", None),
        description="Password for basic authentication",
    ),
    client_id: Optional[str] = Field(
        default=os.environ.get("SERVICENOW_CLIENT_ID", None),
        description="Client ID for OAuth authentication",
    ),
    client_secret: Optional[str] = Field(
        default=os.environ.get("SERVICENOW_CLIENT_SECRET", None),
        description="Client secret for OAuth authentication",
    ),
    verify: Optional[bool] = Field(
        default=to_boolean(os.environ.get("SERVICENOW_VERIFY", "True")),
        description="Whether to verify SSL certificates",
    ),
) -> dict:
    """
    Retrieves details of a specific application from a ServiceNow instance by its unique identifier.
    """
    client = Api(
        url=servicenow_instance,
        username=username,
        password=password,
        client_id=client_id,
        client_secret=client_secret,
        verify=verify,
    )
    response = client.get_application(application_id=application_id)
    return response.result


# CMDB Tools
@mcp.tool(
    exclude_args=[
        "servicenow_instance",
        "username",
        "password",
        "client_id",
        "client_secret",
        "verify",
    ],
    tags={"cmdb"},
)
def get_cmdb(
    cmdb_id: str = Field(
        description="The unique identifier of the CMDB record to retrieve"
    ),
    servicenow_instance: str = Field(
        default=os.environ.get("SERVICENOW_INSTANCE", None),
        description="The URL of the ServiceNow instance (e.g., https://yourinstance.servicenow.com)",
    ),
    username: str = Field(
        default=os.environ.get("SERVICENOW_USERNAME", None),
        description="Username for basic authentication",
    ),
    password: str = Field(
        default=os.environ.get("SERVICENOW_PASSWORD", None),
        description="Password for basic authentication",
    ),
    client_id: Optional[str] = Field(
        default=os.environ.get("SERVICENOW_CLIENT_ID", None),
        description="Client ID for OAuth authentication",
    ),
    client_secret: Optional[str] = Field(
        default=os.environ.get("SERVICENOW_CLIENT_SECRET", None),
        description="Client secret for OAuth authentication",
    ),
    verify: Optional[bool] = Field(
        default=to_boolean(os.environ.get("SERVICENOW_VERIFY", "True")),
        description="Whether to verify SSL certificates",
    ),
) -> dict:
    """
    Fetches a specific Configuration Management Database (CMDB) record from a ServiceNow instance using its unique identifier.
    """
    client = Api(
        url=servicenow_instance,
        username=username,
        password=password,
        client_id=client_id,
        client_secret=client_secret,
        verify=verify,
    )
    response = client.get_cmdb(cmdb_id=cmdb_id)
    return response.result


# CI/CD Tools
@mcp.tool(
    exclude_args=[
        "servicenow_instance",
        "username",
        "password",
        "client_id",
        "client_secret",
        "verify",
    ],
    tags={"cicd"},
)
def batch_install_result(
    result_id: str = Field(
        description="The ID associated with the batch installation result"
    ),
    servicenow_instance: str = Field(
        default=os.environ.get("SERVICENOW_INSTANCE", None),
        description="The URL of the ServiceNow instance (e.g., https://yourinstance.servicenow.com)",
    ),
    username: str = Field(
        default=os.environ.get("SERVICENOW_USERNAME", None),
        description="Username for basic authentication",
    ),
    password: str = Field(
        default=os.environ.get("SERVICENOW_PASSWORD", None),
        description="Password for basic authentication",
    ),
    client_id: Optional[str] = Field(
        default=os.environ.get("SERVICENOW_CLIENT_ID", None),
        description="Client ID for OAuth authentication",
    ),
    client_secret: Optional[str] = Field(
        default=os.environ.get("SERVICENOW_CLIENT_SECRET", None),
        description="Client secret for OAuth authentication",
    ),
    verify: Optional[bool] = Field(
        default=to_boolean(os.environ.get("SERVICENOW_VERIFY", "True")),
        description="Whether to verify SSL certificates",
    ),
) -> dict:
    """
    Retrieves the result of a batch installation process in ServiceNow by result ID.
    """
    client = Api(
        url=servicenow_instance,
        username=username,
        password=password,
        client_id=client_id,
        client_secret=client_secret,
        verify=verify,
    )
    response = client.batch_install_result(result_id=result_id)
    return response.result


@mcp.tool(
    exclude_args=[
        "servicenow_instance",
        "username",
        "password",
        "client_id",
        "client_secret",
        "verify",
    ],
    tags={"cicd"},
)
def instance_scan_progress(
    progress_id: str = Field(
        description="The ID associated with the instance scan progress"
    ),
    servicenow_instance: str = Field(
        default=os.environ.get("SERVICENOW_INSTANCE", None),
        description="The URL of the ServiceNow instance (e.g., https://yourinstance.servicenow.com)",
    ),
    username: str = Field(
        default=os.environ.get("SERVICENOW_USERNAME", None),
        description="Username for basic authentication",
    ),
    password: str = Field(
        default=os.environ.get("SERVICENOW_PASSWORD", None),
        description="Password for basic authentication",
    ),
    client_id: Optional[str] = Field(
        default=os.environ.get("SERVICENOW_CLIENT_ID", None),
        description="Client ID for OAuth authentication",
    ),
    client_secret: Optional[str] = Field(
        default=os.environ.get("SERVICENOW_CLIENT_SECRET", None),
        description="Client secret for OAuth authentication",
    ),
    verify: Optional[bool] = Field(
        default=to_boolean(os.environ.get("SERVICENOW_VERIFY", "True")),
        description="Whether to verify SSL certificates",
    ),
) -> dict:
    """
    Gets the progress status of an instance scan in ServiceNow by progress ID.
    """
    client = Api(
        url=servicenow_instance,
        username=username,
        password=password,
        client_id=client_id,
        client_secret=client_secret,
        verify=verify,
    )
    response = client.instance_scan_progress(progress_id=progress_id)
    return response.result


@mcp.tool(
    exclude_args=[
        "servicenow_instance",
        "username",
        "password",
        "client_id",
        "client_secret",
        "verify",
    ],
    tags={"cicd"},
)
def progress(
    progress_id: str = Field(description="The ID associated with the progress"),
    servicenow_instance: str = Field(
        default=os.environ.get("SERVICENOW_INSTANCE", None),
        description="The URL of the ServiceNow instance (e.g., https://yourinstance.servicenow.com)",
    ),
    username: str = Field(
        default=os.environ.get("SERVICENOW_USERNAME", None),
        description="Username for basic authentication",
    ),
    password: str = Field(
        default=os.environ.get("SERVICENOW_PASSWORD", None),
        description="Password for basic authentication",
    ),
    client_id: Optional[str] = Field(
        default=os.environ.get("SERVICENOW_CLIENT_ID", None),
        description="Client ID for OAuth authentication",
    ),
    client_secret: Optional[str] = Field(
        default=os.environ.get("SERVICENOW_CLIENT_SECRET", None),
        description="Client secret for OAuth authentication",
    ),
    verify: Optional[bool] = Field(
        default=to_boolean(os.environ.get("SERVICENOW_VERIFY", "True")),
        description="Whether to verify SSL certificates",
    ),
) -> dict:
    """
    Retrieves the progress status of a specified process in ServiceNow by progress ID.
    """
    client = Api(
        url=servicenow_instance,
        username=username,
        password=password,
        client_id=client_id,
        client_secret=client_secret,
        verify=verify,
    )
    response = client.progress(progress_id=progress_id)
    return response.result


@mcp.tool(
    exclude_args=[
        "servicenow_instance",
        "username",
        "password",
        "client_id",
        "client_secret",
        "verify",
    ],
    tags={"cicd"},
)
def batch_install(
    name: str = Field(description="The name of the batch installation"),
    packages: str = Field(description="The packages to be installed in the batch"),
    servicenow_instance: str = Field(
        default=os.environ.get("SERVICENOW_INSTANCE", None),
        description="The URL of the ServiceNow instance (e.g., https://yourinstance.servicenow.com)",
    ),
    notes: Optional[str] = Field(
        default=None, description="Additional notes for the batch installation"
    ),
    username: str = Field(
        default=os.environ.get("SERVICENOW_USERNAME", None),
        description="Username for basic authentication",
    ),
    password: str = Field(
        default=os.environ.get("SERVICENOW_PASSWORD", None),
        description="Password for basic authentication",
    ),
    client_id: Optional[str] = Field(
        default=os.environ.get("SERVICENOW_CLIENT_ID", None),
        description="Client ID for OAuth authentication",
    ),
    client_secret: Optional[str] = Field(
        default=os.environ.get("SERVICENOW_CLIENT_SECRET", None),
        description="Client secret for OAuth authentication",
    ),
    verify: Optional[bool] = Field(
        default=to_boolean(os.environ.get("SERVICENOW_VERIFY", "True")),
        description="Whether to verify SSL certificates",
    ),
) -> dict:
    """
    Initiates a batch installation of specified packages in ServiceNow with optional notes.
    """
    client = Api(
        url=servicenow_instance,
        username=username,
        password=password,
        client_id=client_id,
        client_secret=client_secret,
        verify=verify,
    )
    response = client.batch_install(name=name, packages=packages, notes=notes)
    return response.result


@mcp.tool(
    exclude_args=[
        "servicenow_instance",
        "username",
        "password",
        "client_id",
        "client_secret",
        "verify",
    ],
    tags={"cicd"},
)
def batch_rollback(
    rollback_id: str = Field(description="The ID associated with the batch rollback"),
    servicenow_instance: str = Field(
        default=os.environ.get("SERVICENOW_INSTANCE", None),
        description="The URL of the ServiceNow instance (e.g., https://yourinstance.servicenow.com)",
    ),
    username: str = Field(
        default=os.environ.get("SERVICENOW_USERNAME", None),
        description="Username for basic authentication",
    ),
    password: str = Field(
        default=os.environ.get("SERVICENOW_PASSWORD", None),
        description="Password for basic authentication",
    ),
    client_id: Optional[str] = Field(
        default=os.environ.get("SERVICENOW_CLIENT_ID", None),
        description="Client ID for OAuth authentication",
    ),
    client_secret: Optional[str] = Field(
        default=os.environ.get("SERVICENOW_CLIENT_SECRET", None),
        description="Client secret for OAuth authentication",
    ),
    verify: Optional[bool] = Field(
        default=to_boolean(os.environ.get("SERVICENOW_VERIFY", "True")),
        description="Whether to verify SSL certificates",
    ),
) -> dict:
    """
    Performs a rollback of a batch installation in ServiceNow using the rollback ID.
    """
    client = Api(
        url=servicenow_instance,
        username=username,
        password=password,
        client_id=client_id,
        client_secret=client_secret,
        verify=verify,
    )
    response = client.batch_rollback(rollback_id=rollback_id)
    return response.result


@mcp.tool(
    exclude_args=[
        "servicenow_instance",
        "username",
        "password",
        "client_id",
        "client_secret",
        "verify",
    ],
    tags={"cicd"},
)
def app_repo_install(
    app_sys_id: str = Field(
        description="The sys_id of the application to be installed"
    ),
    scope: str = Field(description="The scope of the application"),
    servicenow_instance: str = Field(
        default=os.environ.get("SERVICENOW_INSTANCE", None),
        description="The URL of the ServiceNow instance (e.g., https://yourinstance.servicenow.com)",
    ),
    auto_upgrade_base_app: Optional[bool] = Field(
        default=None, description="Flag indicating whether to auto-upgrade the base app"
    ),
    base_app_version: Optional[str] = Field(
        default=None, description="The version of the base app"
    ),
    version: Optional[str] = Field(
        default=None, description="The version of the application to be installed"
    ),
    username: str = Field(
        default=os.environ.get("SERVICENOW_USERNAME", None),
        description="Username for basic authentication",
    ),
    password: str = Field(
        default=os.environ.get("SERVICENOW_PASSWORD", None),
        description="Password for basic authentication",
    ),
    client_id: Optional[str] = Field(
        default=os.environ.get("SERVICENOW_CLIENT_ID", None),
        description="Client ID for OAuth authentication",
    ),
    client_secret: Optional[str] = Field(
        default=os.environ.get("SERVICENOW_CLIENT_SECRET", None),
        description="Client secret for OAuth authentication",
    ),
    verify: Optional[bool] = Field(
        default=to_boolean(os.environ.get("SERVICENOW_VERIFY", "True")),
        description="Whether to verify SSL certificates",
    ),
) -> dict:
    """
    Installs an application from a repository in ServiceNow with specified parameters.
    """
    client = Api(
        url=servicenow_instance,
        username=username,
        password=password,
        client_id=client_id,
        client_secret=client_secret,
        verify=verify,
    )
    response = client.app_repo_install(
        app_sys_id=app_sys_id,
        scope=scope,
        auto_upgrade_base_app=auto_upgrade_base_app,
        base_app_version=base_app_version,
        version=version,
    )
    return response.result


@mcp.tool(
    exclude_args=[
        "servicenow_instance",
        "username",
        "password",
        "client_id",
        "client_secret",
        "verify",
    ],
    tags={"cicd"},
)
def app_repo_publish(
    app_sys_id: str = Field(
        description="The sys_id of the application to be published"
    ),
    scope: str = Field(description="The scope of the application"),
    servicenow_instance: str = Field(
        default=os.environ.get("SERVICENOW_INSTANCE", None),
        description="The URL of the ServiceNow instance (e.g., https://yourinstance.servicenow.com)",
    ),
    dev_notes: Optional[str] = Field(
        default=None, description="Development notes for the published version"
    ),
    version: Optional[str] = Field(
        default=None, description="The version of the application to be published"
    ),
    username: str = Field(
        default=os.environ.get("SERVICENOW_USERNAME", None),
        description="Username for basic authentication",
    ),
    password: str = Field(
        default=os.environ.get("SERVICENOW_PASSWORD", None),
        description="Password for basic authentication",
    ),
    client_id: Optional[str] = Field(
        default=os.environ.get("SERVICENOW_CLIENT_ID", None),
        description="Client ID for OAuth authentication",
    ),
    client_secret: Optional[str] = Field(
        default=os.environ.get("SERVICENOW_CLIENT_SECRET", None),
        description="Client secret for OAuth authentication",
    ),
    verify: Optional[bool] = Field(
        default=to_boolean(os.environ.get("SERVICENOW_VERIFY", "True")),
        description="Whether to verify SSL certificates",
    ),
) -> dict:
    """
    Publishes an application to a repository in ServiceNow with development notes and version.
    """
    client = Api(
        url=servicenow_instance,
        username=username,
        password=password,
        client_id=client_id,
        client_secret=client_secret,
        verify=verify,
    )
    response = client.app_repo_publish(
        app_sys_id=app_sys_id, scope=scope, dev_notes=dev_notes, version=version
    )
    return response.result


@mcp.tool(
    exclude_args=[
        "servicenow_instance",
        "username",
        "password",
        "client_id",
        "client_secret",
        "verify",
    ],
    tags={"cicd"},
)
def app_repo_rollback(
    app_sys_id: str = Field(
        description="The sys_id of the application to be rolled back"
    ),
    scope: str = Field(description="The scope of the application"),
    version: str = Field(
        description="The version of the application to be rolled back"
    ),
    servicenow_instance: str = Field(
        default=os.environ.get("SERVICENOW_INSTANCE", None),
        description="The URL of the ServiceNow instance (e.g., https://yourinstance.servicenow.com)",
    ),
    username: str = Field(
        default=os.environ.get("SERVICENOW_USERNAME", None),
        description="Username for basic authentication",
    ),
    password: str = Field(
        default=os.environ.get("SERVICENOW_PASSWORD", None),
        description="Password for basic authentication",
    ),
    client_id: Optional[str] = Field(
        default=os.environ.get("SERVICENOW_CLIENT_ID", None),
        description="Client ID for OAuth authentication",
    ),
    client_secret: Optional[str] = Field(
        default=os.environ.get("SERVICENOW_CLIENT_SECRET", None),
        description="Client secret for OAuth authentication",
    ),
    verify: Optional[bool] = Field(
        default=to_boolean(os.environ.get("SERVICENOW_VERIFY", "True")),
        description="Whether to verify SSL certificates",
    ),
) -> dict:
    """
    Rolls back an application to a previous version in ServiceNow by sys_id, scope, and version.
    """
    client = Api(
        url=servicenow_instance,
        username=username,
        password=password,
        client_id=client_id,
        client_secret=client_secret,
        verify=verify,
    )
    response = client.app_repo_rollback(
        app_sys_id=app_sys_id, scope=scope, version=version
    )
    return response.result


@mcp.tool(
    exclude_args=[
        "servicenow_instance",
        "username",
        "password",
        "client_id",
        "client_secret",
        "verify",
    ],
    tags={"cicd"},
)
def full_scan(
    servicenow_instance: str = Field(
        default=os.environ.get("SERVICENOW_INSTANCE", None),
        description="The URL of the ServiceNow instance (e.g., https://yourinstance.servicenow.com)",
    ),
    username: str = Field(
        default=os.environ.get("SERVICENOW_USERNAME", None),
        description="Username for basic authentication",
    ),
    password: str = Field(
        default=os.environ.get("SERVICENOW_PASSWORD", None),
        description="Password for basic authentication",
    ),
    client_id: Optional[str] = Field(
        default=os.environ.get("SERVICENOW_CLIENT_ID", None),
        description="Client ID for OAuth authentication",
    ),
    client_secret: Optional[str] = Field(
        default=os.environ.get("SERVICENOW_CLIENT_SECRET", None),
        description="Client secret for OAuth authentication",
    ),
    verify: Optional[bool] = Field(
        default=to_boolean(os.environ.get("SERVICENOW_VERIFY", "True")),
        description="Whether to verify SSL certificates",
    ),
) -> dict:
    """
    Initiates a full scan of the ServiceNow instance.
    """
    client = Api(
        url=servicenow_instance,
        username=username,
        password=password,
        client_id=client_id,
        client_secret=client_secret,
        verify=verify,
    )
    response = client.full_scan()
    return response.result


@mcp.tool(
    exclude_args=[
        "servicenow_instance",
        "username",
        "password",
        "client_id",
        "client_secret",
        "verify",
    ],
    tags={"cicd"},
)
def point_scan(
    target_sys_id: str = Field(description="The sys_id of the target instance"),
    target_table: str = Field(description="The table of the target instance"),
    servicenow_instance: str = Field(
        default=os.environ.get("SERVICENOW_INSTANCE", None),
        description="The URL of the ServiceNow instance (e.g., https://yourinstance.servicenow.com)",
    ),
    username: str = Field(
        default=os.environ.get("SERVICENOW_USERNAME", None),
        description="Username for basic authentication",
    ),
    password: str = Field(
        default=os.environ.get("SERVICENOW_PASSWORD", None),
        description="Password for basic authentication",
    ),
    client_id: Optional[str] = Field(
        default=os.environ.get("SERVICENOW_CLIENT_ID", None),
        description="Client ID for OAuth authentication",
    ),
    client_secret: Optional[str] = Field(
        default=os.environ.get("SERVICENOW_CLIENT_SECRET", None),
        description="Client secret for OAuth authentication",
    ),
    verify: Optional[bool] = Field(
        default=to_boolean(os.environ.get("SERVICENOW_VERIFY", "True")),
        description="Whether to verify SSL certificates",
    ),
) -> dict:
    """
    Performs a targeted scan on a specific instance and table in ServiceNow.
    """
    client = Api(
        url=servicenow_instance,
        username=username,
        password=password,
        client_id=client_id,
        client_secret=client_secret,
        verify=verify,
    )
    response = client.point_scan(target_sys_id=target_sys_id, target_table=target_table)
    return response.result


@mcp.tool(
    exclude_args=[
        "servicenow_instance",
        "username",
        "password",
        "client_id",
        "client_secret",
        "verify",
    ],
    tags={"cicd"},
)
def combo_suite_scan(
    combo_sys_id: str = Field(description="The sys_id of the combo to be scanned"),
    servicenow_instance: str = Field(
        default=os.environ.get("SERVICENOW_INSTANCE", None),
        description="The URL of the ServiceNow instance (e.g., https://yourinstance.servicenow.com)",
    ),
    username: str = Field(
        default=os.environ.get("SERVICENOW_USERNAME", None),
        description="Username for basic authentication",
    ),
    password: str = Field(
        default=os.environ.get("SERVICENOW_PASSWORD", None),
        description="Password for basic authentication",
    ),
    client_id: Optional[str] = Field(
        default=os.environ.get("SERVICENOW_CLIENT_ID", None),
        description="Client ID for OAuth authentication",
    ),
    client_secret: Optional[str] = Field(
        default=os.environ.get("SERVICENOW_CLIENT_SECRET", None),
        description="Client secret for OAuth authentication",
    ),
    verify: Optional[bool] = Field(
        default=to_boolean(os.environ.get("SERVICENOW_VERIFY", "True")),
        description="Whether to verify SSL certificates",
    ),
) -> dict:
    """
    Executes a scan on a combination of suites in ServiceNow by combo sys_id.
    """
    client = Api(
        url=servicenow_instance,
        username=username,
        password=password,
        client_id=client_id,
        client_secret=client_secret,
        verify=verify,
    )
    response = client.combo_suite_scan(combo_sys_id=combo_sys_id)
    return response.result


@mcp.tool(
    exclude_args=[
        "servicenow_instance",
        "username",
        "password",
        "client_id",
        "client_secret",
        "verify",
    ],
    tags={"cicd"},
)
def suite_scan(
    suite_sys_id: str = Field(description="The sys_id of the suite to be scanned"),
    sys_ids: List[str] = Field(
        description="List of sys_ids representing app_scope_sys_ids for the suite scan"
    ),
    scan_type: str = Field(
        default="scoped_apps", description="Type of scan to be performed"
    ),
    servicenow_instance: str = Field(
        default=os.environ.get("SERVICENOW_INSTANCE", None),
        description="The URL of the ServiceNow instance (e.g., https://yourinstance.servicenow.com)",
    ),
    username: str = Field(
        default=os.environ.get("SERVICENOW_USERNAME", None),
        description="Username for basic authentication",
    ),
    password: str = Field(
        default=os.environ.get("SERVICENOW_PASSWORD", None),
        description="Password for basic authentication",
    ),
    client_id: Optional[str] = Field(
        default=os.environ.get("SERVICENOW_CLIENT_ID", None),
        description="Client ID for OAuth authentication",
    ),
    client_secret: Optional[str] = Field(
        default=os.environ.get("SERVICENOW_CLIENT_SECRET", None),
        description="Client secret for OAuth authentication",
    ),
    verify: Optional[bool] = Field(
        default=to_boolean(os.environ.get("SERVICENOW_VERIFY", "True")),
        description="Whether to verify SSL certificates",
    ),
) -> dict:
    """
    Runs a scan on a specified suite with a list of sys_ids and scan type in ServiceNow.
    """
    client = Api(
        url=servicenow_instance,
        username=username,
        password=password,
        client_id=client_id,
        client_secret=client_secret,
        verify=verify,
    )
    response = client.suite_scan(
        suite_sys_id=suite_sys_id, sys_ids=sys_ids, scan_type=scan_type
    )
    return response.result


# Plugin and Update Set Tools
@mcp.tool(
    exclude_args=[
        "servicenow_instance",
        "username",
        "password",
        "client_id",
        "client_secret",
        "verify",
    ],
    tags={"plugins"},
)
def activate_plugin(
    plugin_id: str = Field(description="The ID of the plugin to be activated"),
    servicenow_instance: str = Field(
        default=os.environ.get("SERVICENOW_INSTANCE", None),
        description="The URL of the ServiceNow instance (e.g., https://yourinstance.servicenow.com)",
    ),
    username: str = Field(
        default=os.environ.get("SERVICENOW_USERNAME", None),
        description="Username for basic authentication",
    ),
    password: str = Field(
        default=os.environ.get("SERVICENOW_PASSWORD", None),
        description="Password for basic authentication",
    ),
    client_id: Optional[str] = Field(
        default=os.environ.get("SERVICENOW_CLIENT_ID", None),
        description="Client ID for OAuth authentication",
    ),
    client_secret: Optional[str] = Field(
        default=os.environ.get("SERVICENOW_CLIENT_SECRET", None),
        description="Client secret for OAuth authentication",
    ),
    verify: Optional[bool] = Field(
        default=to_boolean(os.environ.get("SERVICENOW_VERIFY", "True")),
        description="Whether to verify SSL certificates",
    ),
) -> dict:
    """
    Activates a specified plugin in ServiceNow by plugin ID.
    """
    client = Api(
        url=servicenow_instance,
        username=username,
        password=password,
        client_id=client_id,
        client_secret=client_secret,
        verify=verify,
    )
    response = client.activate_plugin(plugin_id=plugin_id)
    return response.result


@mcp.tool(
    exclude_args=[
        "servicenow_instance",
        "username",
        "password",
        "client_id",
        "client_secret",
        "verify",
    ],
    tags={"plugins"},
)
def rollback_plugin(
    plugin_id: str = Field(description="The ID of the plugin to be rolled back"),
    servicenow_instance: str = Field(
        default=os.environ.get("SERVICENOW_INSTANCE", None),
        description="The URL of the ServiceNow instance (e.g., https://yourinstance.servicenow.com)",
    ),
    username: str = Field(
        default=os.environ.get("SERVICENOW_USERNAME", None),
        description="Username for basic authentication",
    ),
    password: str = Field(
        default=os.environ.get("SERVICENOW_PASSWORD", None),
        description="Password for basic authentication",
    ),
    client_id: Optional[str] = Field(
        default=os.environ.get("SERVICENOW_CLIENT_ID", None),
        description="Client ID for OAuth authentication",
    ),
    client_secret: Optional[str] = Field(
        default=os.environ.get("SERVICENOW_CLIENT_SECRET", None),
        description="Client secret for OAuth authentication",
    ),
    verify: Optional[bool] = Field(
        default=to_boolean(os.environ.get("SERVICENOW_VERIFY", "True")),
        description="Whether to verify SSL certificates",
    ),
) -> dict:
    """
    Rolls back a specified plugin in ServiceNow to its previous state by plugin ID.
    """
    client = Api(
        url=servicenow_instance,
        username=username,
        password=password,
        client_id=client_id,
        client_secret=client_secret,
        verify=verify,
    )
    response = client.rollback_plugin(plugin_id=plugin_id)
    return response.result


@mcp.tool(
    exclude_args=[
        "servicenow_instance",
        "username",
        "password",
        "client_id",
        "client_secret",
        "verify",
    ],
    tags={"source_control"},
)
def apply_remote_source_control_changes(
    app_sys_id: str = Field(
        description="The sys_id of the application for which changes should be applied"
    ),
    scope: str = Field(description="The scope of the changes"),
    branch_name: str = Field(
        description="The name of the branch containing the changes"
    ),
    servicenow_instance: str = Field(
        default=os.environ.get("SERVICENOW_INSTANCE", None),
        description="The URL of the ServiceNow instance (e.g., https://yourinstance.servicenow.com)",
    ),
    auto_upgrade_base_app: Optional[bool] = Field(
        default=None, description="Flag indicating whether to auto-upgrade the base app"
    ),
    username: str = Field(
        default=os.environ.get("SERVICENOW_USERNAME", None),
        description="Username for basic authentication",
    ),
    password: str = Field(
        default=os.environ.get("SERVICENOW_PASSWORD", None),
        description="Password for basic authentication",
    ),
    client_id: Optional[str] = Field(
        default=os.environ.get("SERVICENOW_CLIENT_ID", None),
        description="Client ID for OAuth authentication",
    ),
    client_secret: Optional[str] = Field(
        default=os.environ.get("SERVICENOW_CLIENT_SECRET", None),
        description="Client secret for OAuth authentication",
    ),
    verify: Optional[bool] = Field(
        default=to_boolean(os.environ.get("SERVICENOW_VERIFY", "True")),
        description="Whether to verify SSL certificates",
    ),
) -> dict:
    """
    Applies changes from a remote source control branch to a ServiceNow application.
    """
    client = Api(
        url=servicenow_instance,
        username=username,
        password=password,
        client_id=client_id,
        client_secret=client_secret,
        verify=verify,
    )
    response = client.apply_remote_source_control_changes(
        app_sys_id=app_sys_id,
        scope=scope,
        branch_name=branch_name,
        auto_upgrade_base_app=auto_upgrade_base_app,
    )
    return response.result


@mcp.tool(
    exclude_args=[
        "servicenow_instance",
        "username",
        "password",
        "client_id",
        "client_secret",
        "verify",
    ],
    tags={"source_control"},
)
def import_repository(
    repo_url: str = Field(description="The URL of the repository to be imported"),
    servicenow_instance: str = Field(
        default=os.environ.get("SERVICENOW_INSTANCE", None),
        description="The URL of the ServiceNow instance (e.g., https://yourinstance.servicenow.com)",
    ),
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
        default=None, description="Flag indicating whether to auto-upgrade the base app"
    ),
    username: str = Field(
        default=os.environ.get("SERVICENOW_USERNAME", None),
        description="Username for basic authentication",
    ),
    password: str = Field(
        default=os.environ.get("SERVICENOW_PASSWORD", None),
        description="Password for basic authentication",
    ),
    client_id: Optional[str] = Field(
        default=os.environ.get("SERVICENOW_CLIENT_ID", None),
        description="Client ID for OAuth authentication",
    ),
    client_secret: Optional[str] = Field(
        default=os.environ.get("SERVICENOW_CLIENT_SECRET", None),
        description="Client secret for OAuth authentication",
    ),
    verify: Optional[bool] = Field(
        default=to_boolean(os.environ.get("SERVICENOW_VERIFY", "True")),
        description="Whether to verify SSL certificates",
    ),
) -> dict:
    """
    Imports a repository into ServiceNow with specified credentials and branch.
    """
    client = Api(
        url=servicenow_instance,
        username=username,
        password=password,
        client_id=client_id,
        client_secret=client_secret,
        verify=verify,
    )
    response = client.import_repository(
        credential_sys_id=credential_sys_id,
        mid_server_sys_id=mid_server_sys_id,
        repo_url=repo_url,
        branch_name=branch_name,
        auto_upgrade_base_app=auto_upgrade_base_app,
    )
    return response.result


@mcp.tool(
    exclude_args=[
        "servicenow_instance",
        "username",
        "password",
        "client_id",
        "client_secret",
        "verify",
    ],
    tags={"testing"},
)
def run_test_suite(
    test_suite_sys_id: str = Field(
        description="The sys_id of the test suite to be run"
    ),
    test_suite_name: str = Field(description="The name of the test suite to be run"),
    servicenow_instance: str = Field(
        default=os.environ.get("SERVICENOW_INSTANCE", None),
        description="The URL of the ServiceNow instance (e.g., https://yourinstance.servicenow.com)",
    ),
    browser_name: Optional[str] = Field(
        default=None, description="The name of the browser for the test run"
    ),
    browser_version: Optional[str] = Field(
        default=None, description="The version of the browser for the test run"
    ),
    os_name: Optional[str] = Field(
        default=None, description="The name of the operating system for the test run"
    ),
    os_version: Optional[str] = Field(
        default=None, description="The version of the operating system for the test run"
    ),
    username: str = Field(
        default=os.environ.get("SERVICENOW_USERNAME", None),
        description="Username for basic authentication",
    ),
    password: str = Field(
        default=os.environ.get("SERVICENOW_PASSWORD", None),
        description="Password for basic authentication",
    ),
    client_id: Optional[str] = Field(
        default=os.environ.get("SERVICENOW_CLIENT_ID", None),
        description="Client ID for OAuth authentication",
    ),
    client_secret: Optional[str] = Field(
        default=os.environ.get("SERVICENOW_CLIENT_SECRET", None),
        description="Client secret for OAuth authentication",
    ),
    verify: Optional[bool] = Field(
        default=to_boolean(os.environ.get("SERVICENOW_VERIFY", "True")),
        description="Whether to verify SSL certificates",
    ),
) -> dict:
    """
    Executes a test suite in ServiceNow with specified browser and OS configurations.
    """
    client = Api(
        url=servicenow_instance,
        username=username,
        password=password,
        client_id=client_id,
        client_secret=client_secret,
        verify=verify,
    )
    response = client.run_test_suite(
        test_suite_sys_id=test_suite_sys_id,
        test_suite_name=test_suite_name,
        browser_name=browser_name,
        browser_version=browser_version,
        os_name=os_name,
        os_version=os_version,
    )
    return response.result


@mcp.tool(
    exclude_args=[
        "servicenow_instance",
        "username",
        "password",
        "client_id",
        "client_secret",
        "verify",
    ],
    tags={"update_sets"},
)
def update_set_create(
    update_set_name: str = Field(description="Name to give the update set"),
    scope: str = Field(
        description="The scope name of the application in which to create the new update set"
    ),
    sys_id: str = Field(
        description="Sys_id of the application in which to create the new update set"
    ),
    servicenow_instance: str = Field(
        default=os.environ.get("SERVICENOW_INSTANCE", None),
        description="The URL of the ServiceNow instance (e.g., https://yourinstance.servicenow.com)",
    ),
    description: Optional[str] = Field(
        default=None, description="Description of the update set"
    ),
    username: str = Field(
        default=os.environ.get("SERVICENOW_USERNAME", None),
        description="Username for basic authentication",
    ),
    password: str = Field(
        default=os.environ.get("SERVICENOW_PASSWORD", None),
        description="Password for basic authentication",
    ),
    client_id: Optional[str] = Field(
        default=os.environ.get("SERVICENOW_CLIENT_ID", None),
        description="Client ID for OAuth authentication",
    ),
    client_secret: Optional[str] = Field(
        default=os.environ.get("SERVICENOW_CLIENT_SECRET", None),
        description="Client secret for OAuth authentication",
    ),
    verify: Optional[bool] = Field(
        default=to_boolean(os.environ.get("SERVICENOW_VERIFY", "True")),
        description="Whether to verify SSL certificates",
    ),
) -> dict:
    """
    Creates a new update set in ServiceNow with a given name, scope, and description.
    """
    client = Api(
        url=servicenow_instance,
        username=username,
        password=password,
        client_id=client_id,
        client_secret=client_secret,
        verify=verify,
    )
    response = client.update_set_create(
        update_set_name=update_set_name,
        description=description,
        scope=scope,
        sys_id=sys_id,
    )
    return response.result


@mcp.tool(
    exclude_args=[
        "servicenow_instance",
        "username",
        "password",
        "client_id",
        "client_secret",
        "verify",
    ],
    tags={"update_sets"},
)
def update_set_retrieve(
    update_set_id: str = Field(
        description="Sys_id of the update set on the source instance from where the update set was retrieved"
    ),
    servicenow_instance: str = Field(
        default=os.environ.get("SERVICENOW_INSTANCE", None),
        description="The URL of the ServiceNow instance (e.g., https://yourinstance.servicenow.com)",
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
    username: str = Field(
        default=os.environ.get("SERVICENOW_USERNAME", None),
        description="Username for basic authentication",
    ),
    password: str = Field(
        default=os.environ.get("SERVICENOW_PASSWORD", None),
        description="Password for basic authentication",
    ),
    client_id: Optional[str] = Field(
        default=os.environ.get("SERVICENOW_CLIENT_ID", None),
        description="Client ID for OAuth authentication",
    ),
    client_secret: Optional[str] = Field(
        default=os.environ.get("SERVICENOW_CLIENT_SECRET", None),
        description="Client secret for OAuth authentication",
    ),
    verify: Optional[bool] = Field(
        default=to_boolean(os.environ.get("SERVICENOW_VERIFY", "True")),
        description="Whether to verify SSL certificates",
    ),
) -> dict:
    """
    Retrieves an update set from a source instance in ServiceNow with optional preview and cleanup.
    """
    client = Api(
        url=servicenow_instance,
        username=username,
        password=password,
        client_id=client_id,
        client_secret=client_secret,
        verify=verify,
    )
    response = client.update_set_retrieve(
        update_set_id=update_set_id,
        update_source_id=update_source_id,
        update_source_instance_id=update_source_instance_id,
        auto_preview=auto_preview,
        cleanup_retrieved=cleanup_retrieved,
    )
    return response.result


@mcp.tool(
    exclude_args=[
        "servicenow_instance",
        "username",
        "password",
        "client_id",
        "client_secret",
        "verify",
    ],
    tags={"update_sets"},
)
def update_set_preview(
    remote_update_set_id: str = Field(
        description="Sys_id of the update set to preview"
    ),
    servicenow_instance: str = Field(
        default=os.environ.get("SERVICENOW_INSTANCE", None),
        description="The URL of the ServiceNow instance (e.g., https://yourinstance.servicenow.com)",
    ),
    username: str = Field(
        default=os.environ.get("SERVICENOW_USERNAME", None),
        description="Username for basic authentication",
    ),
    password: str = Field(
        default=os.environ.get("SERVICENOW_PASSWORD", None),
        description="Password for basic authentication",
    ),
    client_id: Optional[str] = Field(
        default=os.environ.get("SERVICENOW_CLIENT_ID", None),
        description="Client ID for OAuth authentication",
    ),
    client_secret: Optional[str] = Field(
        default=os.environ.get("SERVICENOW_CLIENT_SECRET", None),
        description="Client secret for OAuth authentication",
    ),
    verify: Optional[bool] = Field(
        default=to_boolean(os.environ.get("SERVICENOW_VERIFY", "True")),
        description="Whether to verify SSL certificates",
    ),
) -> dict:
    """
    Previews an update set in ServiceNow by its remote sys_id.
    """
    client = Api(
        url=servicenow_instance,
        username=username,
        password=password,
        client_id=client_id,
        client_secret=client_secret,
        verify=verify,
    )
    response = client.update_set_preview(remote_update_set_id=remote_update_set_id)
    return response.result


@mcp.tool(
    exclude_args=[
        "servicenow_instance",
        "username",
        "password",
        "client_id",
        "client_secret",
        "verify",
    ],
    tags={"update_sets"},
)
def update_set_commit(
    remote_update_set_id: str = Field(description="Sys_id of the update set to commit"),
    servicenow_instance: str = Field(
        default=os.environ.get("SERVICENOW_INSTANCE", None),
        description="The URL of the ServiceNow instance (e.g., https://yourinstance.servicenow.com)",
    ),
    force_commit: Optional[str] = Field(
        default=None,
        description="Flag that indicates whether to force commit the update set",
    ),
    username: str = Field(
        default=os.environ.get("SERVICENOW_USERNAME", None),
        description="Username for basic authentication",
    ),
    password: str = Field(
        default=os.environ.get("SERVICENOW_PASSWORD", None),
        description="Password for basic authentication",
    ),
    client_id: Optional[str] = Field(
        default=os.environ.get("SERVICENOW_CLIENT_ID", None),
        description="Client ID for OAuth authentication",
    ),
    client_secret: Optional[str] = Field(
        default=os.environ.get("SERVICENOW_CLIENT_SECRET", None),
        description="Client secret for OAuth authentication",
    ),
    verify: Optional[bool] = Field(
        default=to_boolean(os.environ.get("SERVICENOW_VERIFY", "True")),
        description="Whether to verify SSL certificates",
    ),
) -> dict:
    """
    Commits an update set in ServiceNow with an option to force commit.
    """
    client = Api(
        url=servicenow_instance,
        username=username,
        password=password,
        client_id=client_id,
        client_secret=client_secret,
        verify=verify,
    )
    response = client.update_set_commit(
        remote_update_set_id=remote_update_set_id, force_commit=force_commit
    )
    return response.result


@mcp.tool(
    exclude_args=[
        "servicenow_instance",
        "username",
        "password",
        "client_id",
        "client_secret",
        "verify",
    ],
    tags={"update_sets"},
)
def update_set_commit_multiple(
    remote_update_set_ids: List[str] = Field(
        description="List of sys_ids associated with update sets to commit. Sys_ids are committed in the order given"
    ),
    servicenow_instance: str = Field(
        default=os.environ.get("SERVICENOW_INSTANCE", None),
        description="The URL of the ServiceNow instance (e.g., https://yourinstance.servicenow.com)",
    ),
    force_commit: Optional[str] = Field(
        default=None,
        description="Flag that indicates whether to force commit the update sets",
    ),
    username: str = Field(
        default=os.environ.get("SERVICENOW_USERNAME", None),
        description="Username for basic authentication",
    ),
    password: str = Field(
        default=os.environ.get("SERVICENOW_PASSWORD", None),
        description="Password for basic authentication",
    ),
    client_id: Optional[str] = Field(
        default=os.environ.get("SERVICENOW_CLIENT_ID", None),
        description="Client ID for OAuth authentication",
    ),
    client_secret: Optional[str] = Field(
        default=os.environ.get("SERVICENOW_CLIENT_SECRET", None),
        description="Client secret for OAuth authentication",
    ),
    verify: Optional[bool] = Field(
        default=to_boolean(os.environ.get("SERVICENOW_VERIFY", "True")),
        description="Whether to verify SSL certificates",
    ),
) -> dict:
    """
    Commits multiple update sets in ServiceNow in the specified order.
    """
    client = Api(
        url=servicenow_instance,
        username=username,
        password=password,
        client_id=client_id,
        client_secret=client_secret,
        verify=verify,
    )
    response = client.update_set_commit_multiple(
        remote_update_set_ids=remote_update_set_ids, force_commit=force_commit
    )
    return response.result


@mcp.tool(
    exclude_args=[
        "servicenow_instance",
        "username",
        "password",
        "client_id",
        "client_secret",
        "verify",
    ],
    tags={"update_sets"},
)
def update_set_back_out(
    update_set_id: str = Field(description="Sys_id of the update set"),
    servicenow_instance: str = Field(
        default=os.environ.get("SERVICENOW_INSTANCE", None),
        description="The URL of the ServiceNow instance (e.g., https://yourinstance.servicenow.com)",
    ),
    rollback_installs: Optional[bool] = Field(
        default=None,
        description="Flag that indicates whether to rollback the batch installation performed during the update set commit",
    ),
    username: str = Field(
        default=os.environ.get("SERVICENOW_USERNAME", None),
        description="Username for basic authentication",
    ),
    password: str = Field(
        default=os.environ.get("SERVICENOW_PASSWORD", None),
        description="Password for basic authentication",
    ),
    client_id: Optional[str] = Field(
        default=os.environ.get("SERVICENOW_CLIENT_ID", None),
        description="Client ID for OAuth authentication",
    ),
    client_secret: Optional[str] = Field(
        default=os.environ.get("SERVICENOW_CLIENT_SECRET", None),
        description="Client secret for OAuth authentication",
    ),
    verify: Optional[bool] = Field(
        default=to_boolean(os.environ.get("SERVICENOW_VERIFY", "True")),
        description="Whether to verify SSL certificates",
    ),
) -> dict:
    """
    Backs out an update set in ServiceNow with an option to rollback installations.
    """
    client = Api(
        url=servicenow_instance,
        username=username,
        password=password,
        client_id=client_id,
        client_secret=client_secret,
        verify=verify,
    )
    response = client.update_set_back_out(
        update_set_id=update_set_id, rollback_installs=rollback_installs
    )
    return response.result


# Change Management Tools
@mcp.tool(
    exclude_args=[
        "servicenow_instance",
        "username",
        "password",
        "client_id",
        "client_secret",
        "verify",
    ],
    tags={"change_management"},
)
def get_change_requests(
    servicenow_instance: str = Field(
        default=os.environ.get("SERVICENOW_INSTANCE", None),
        description="The URL of the ServiceNow instance (e.g., https://yourinstance.servicenow.com)",
    ),
    order: Optional[str] = Field(
        default=None, description="Ordering parameter for sorting results"
    ),
    name_value_pairs: Optional[Dict[str, str]] = Field(
        default=None, description="Additional name-value pairs for filtering"
    ),
    sysparm_query: Optional[str] = Field(
        default=None, description="Query parameter for filtering results"
    ),
    text_search: Optional[str] = Field(
        default=None, description="Text search parameter for searching results"
    ),
    change_type: Optional[str] = Field(
        default=None, description="Type of change (emergency, normal, standard, model)"
    ),
    sysparm_offset: Optional[int] = Field(
        default=None, description="Offset for pagination"
    ),
    sysparm_limit: Optional[int] = Field(
        default=10, description="Limit for pagination"
    ),
    username: str = Field(
        default=os.environ.get("SERVICENOW_USERNAME", None),
        description="Username for basic authentication",
    ),
    password: str = Field(
        default=os.environ.get("SERVICENOW_PASSWORD", None),
        description="Password for basic authentication",
    ),
    client_id: Optional[str] = Field(
        default=os.environ.get("SERVICENOW_CLIENT_ID", None),
        description="Client ID for OAuth authentication",
    ),
    client_secret: Optional[str] = Field(
        default=os.environ.get("SERVICENOW_CLIENT_SECRET", None),
        description="Client secret for OAuth authentication",
    ),
    verify: Optional[bool] = Field(
        default=to_boolean(os.environ.get("SERVICENOW_VERIFY", "True")),
        description="Whether to verify SSL certificates",
    ),
) -> Union[List, Dict]:
    """
    Retrieves change requests from ServiceNow with optional filtering and pagination.
    """
    client = Api(
        url=servicenow_instance,
        username=username,
        password=password,
        client_id=client_id,
        client_secret=client_secret,
        verify=verify,
    )
    response = client.get_change_requests(
        order=order,
        name_value_pairs=name_value_pairs,
        sysparm_query=sysparm_query,
        text_search=text_search,
        change_type=change_type,
        sysparm_offset=sysparm_offset,
        sysparm_limit=sysparm_limit,
    )
    return response.result


@mcp.tool(
    exclude_args=[
        "servicenow_instance",
        "username",
        "password",
        "client_id",
        "client_secret",
        "verify",
    ],
    tags={"change_management"},
)
def get_change_request_nextstate(
    change_request_sys_id: str = Field(description="Sys ID of the change request"),
    servicenow_instance: str = Field(
        default=os.environ.get("SERVICENOW_INSTANCE", None),
        description="The URL of the ServiceNow instance (e.g., https://yourinstance.servicenow.com)",
    ),
    username: str = Field(
        default=os.environ.get("SERVICENOW_USERNAME", None),
        description="Username for basic authentication",
    ),
    password: str = Field(
        default=os.environ.get("SERVICENOW_PASSWORD", None),
        description="Password for basic authentication",
    ),
    client_id: Optional[str] = Field(
        default=os.environ.get("SERVICENOW_CLIENT_ID", None),
        description="Client ID for OAuth authentication",
    ),
    client_secret: Optional[str] = Field(
        default=os.environ.get("SERVICENOW_CLIENT_SECRET", None),
        description="Client secret for OAuth authentication",
    ),
    verify: Optional[bool] = Field(
        default=to_boolean(os.environ.get("SERVICENOW_VERIFY", "True")),
        description="Whether to verify SSL certificates",
    ),
) -> dict:
    """
    Gets the next state for a specific change request in ServiceNow.
    """
    client = Api(
        url=servicenow_instance,
        username=username,
        password=password,
        client_id=client_id,
        client_secret=client_secret,
        verify=verify,
    )
    response = client.get_change_request_nextstate(
        change_request_sys_id=change_request_sys_id
    )
    return response.result


@mcp.tool(
    exclude_args=[
        "servicenow_instance",
        "username",
        "password",
        "client_id",
        "client_secret",
        "verify",
    ],
    tags={"change_management"},
)
def get_change_request_schedule(
    cmdb_ci_sys_id: str = Field(description="Sys ID of the CI (Configuration Item)"),
    servicenow_instance: str = Field(
        default=os.environ.get("SERVICENOW_INSTANCE", None),
        description="The URL of the ServiceNow instance (e.g., https://yourinstance.servicenow.com)",
    ),
    username: str = Field(
        default=os.environ.get("SERVICENOW_USERNAME", None),
        description="Username for basic authentication",
    ),
    password: str = Field(
        default=os.environ.get("SERVICENOW_PASSWORD", None),
        description="Password for basic authentication",
    ),
    client_id: Optional[str] = Field(
        default=os.environ.get("SERVICENOW_CLIENT_ID", None),
        description="Client ID for OAuth authentication",
    ),
    client_secret: Optional[str] = Field(
        default=os.environ.get("SERVICENOW_CLIENT_SECRET", None),
        description="Client secret for OAuth authentication",
    ),
    verify: Optional[bool] = Field(
        default=to_boolean(os.environ.get("SERVICENOW_VERIFY", "True")),
        description="Whether to verify SSL certificates",
    ),
) -> dict:
    """
    Retrieves the schedule for a change request based on a Configuration Item (CI) in ServiceNow.
    """
    client = Api(
        url=servicenow_instance,
        username=username,
        password=password,
        client_id=client_id,
        client_secret=client_secret,
        verify=verify,
    )
    response = client.get_change_request_schedule(cmdb_ci_sys_id=cmdb_ci_sys_id)
    return response.result


@mcp.tool(
    exclude_args=[
        "servicenow_instance",
        "username",
        "password",
        "client_id",
        "client_secret",
        "verify",
    ],
    tags={"change_management"},
)
def get_change_request_tasks(
    change_request_sys_id: str = Field(description="Sys ID of the change request"),
    servicenow_instance: str = Field(
        default=os.environ.get("SERVICENOW_INSTANCE", None),
        description="The URL of the ServiceNow instance (e.g., https://yourinstance.servicenow.com)",
    ),
    order: Optional[str] = Field(
        default=None, description="Ordering parameter for sorting results"
    ),
    name_value_pairs: Optional[Dict[str, str]] = Field(
        default=None, description="Additional name-value pairs for filtering"
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
        default=10, description="Limit for pagination"
    ),
    username: str = Field(
        default=os.environ.get("SERVICENOW_USERNAME", None),
        description="Username for basic authentication",
    ),
    password: str = Field(
        default=os.environ.get("SERVICENOW_PASSWORD", None),
        description="Password for basic authentication",
    ),
    client_id: Optional[str] = Field(
        default=os.environ.get("SERVICENOW_CLIENT_ID", None),
        description="Client ID for OAuth authentication",
    ),
    client_secret: Optional[str] = Field(
        default=os.environ.get("SERVICENOW_CLIENT_SECRET", None),
        description="Client secret for OAuth authentication",
    ),
    verify: Optional[bool] = Field(
        default=to_boolean(os.environ.get("SERVICENOW_VERIFY", "True")),
        description="Whether to verify SSL certificates",
    ),
) -> Union[List, Dict]:
    """
    Fetches tasks associated with a change request in ServiceNow with optional filtering.
    """
    client = Api(
        url=servicenow_instance,
        username=username,
        password=password,
        client_id=client_id,
        client_secret=client_secret,
        verify=verify,
    )
    response = client.get_change_request_tasks(
        change_request_sys_id=change_request_sys_id,
        order=order,
        name_value_pairs=name_value_pairs,
        sysparm_query=sysparm_query,
        text_search=text_search,
        sysparm_offset=sysparm_offset,
        sysparm_limit=sysparm_limit,
    )
    return response.result


@mcp.tool(
    exclude_args=[
        "servicenow_instance",
        "username",
        "password",
        "client_id",
        "client_secret",
        "verify",
    ],
    tags={"change_management"},
)
def get_change_request(
    change_request_sys_id: str = Field(description="Sys ID of the change request"),
    servicenow_instance: str = Field(
        default=os.environ.get("SERVICENOW_INSTANCE", None),
        description="The URL of the ServiceNow instance (e.g., https://yourinstance.servicenow.com)",
    ),
    change_type: Optional[str] = Field(
        default=None, description="Type of change (emergency, normal, standard)"
    ),
    username: str = Field(
        default=os.environ.get("SERVICENOW_USERNAME", None),
        description="Username for basic authentication",
    ),
    password: str = Field(
        default=os.environ.get("SERVICENOW_PASSWORD", None),
        description="Password for basic authentication",
    ),
    client_id: Optional[str] = Field(
        default=os.environ.get("SERVICENOW_CLIENT_ID", None),
        description="Client ID for OAuth authentication",
    ),
    client_secret: Optional[str] = Field(
        default=os.environ.get("SERVICENOW_CLIENT_SECRET", None),
        description="Client secret for OAuth authentication",
    ),
    verify: Optional[bool] = Field(
        default=to_boolean(os.environ.get("SERVICENOW_VERIFY", "True")),
        description="Whether to verify SSL certificates",
    ),
) -> dict:
    """
    Retrieves details of a specific change request in ServiceNow by sys_id and type.
    """
    client = Api(
        url=servicenow_instance,
        username=username,
        password=password,
        client_id=client_id,
        client_secret=client_secret,
        verify=verify,
    )
    response = client.get_change_request(
        change_request_sys_id=change_request_sys_id, change_type=change_type
    )
    return response.result


@mcp.tool(
    exclude_args=[
        "servicenow_instance",
        "username",
        "password",
        "client_id",
        "client_secret",
        "verify",
    ],
    tags={"change_management"},
)
def get_change_request_ci(
    change_request_sys_id: str = Field(description="Sys ID of the change request"),
    servicenow_instance: str = Field(
        default=os.environ.get("SERVICENOW_INSTANCE", None),
        description="The URL of the ServiceNow instance (e.g., https://yourinstance.servicenow.com)",
    ),
    username: str = Field(
        default=os.environ.get("SERVICENOW_USERNAME", None),
        description="Username for basic authentication",
    ),
    password: str = Field(
        default=os.environ.get("SERVICENOW_PASSWORD", None),
        description="Password for basic authentication",
    ),
    client_id: Optional[str] = Field(
        default=os.environ.get("SERVICENOW_CLIENT_ID", None),
        description="Client ID for OAuth authentication",
    ),
    client_secret: Optional[str] = Field(
        default=os.environ.get("SERVICENOW_CLIENT_SECRET", None),
        description="Client secret for OAuth authentication",
    ),
    verify: Optional[bool] = Field(
        default=to_boolean(os.environ.get("SERVICENOW_VERIFY", "True")),
        description="Whether to verify SSL certificates",
    ),
) -> dict:
    """
    Gets Configuration Items (CIs) associated with a change request in ServiceNow.
    """
    client = Api(
        url=servicenow_instance,
        username=username,
        password=password,
        client_id=client_id,
        client_secret=client_secret,
        verify=verify,
    )
    response = client.get_change_request_ci(change_request_sys_id=change_request_sys_id)
    return response.result


@mcp.tool(
    exclude_args=[
        "servicenow_instance",
        "username",
        "password",
        "client_id",
        "client_secret",
        "verify",
    ],
    tags={"change_management"},
)
def get_change_request_conflict(
    change_request_sys_id: str = Field(description="Sys ID of the change request"),
    servicenow_instance: str = Field(
        default=os.environ.get("SERVICENOW_INSTANCE", None),
        description="The URL of the ServiceNow instance (e.g., https://yourinstance.servicenow.com)",
    ),
    username: str = Field(
        default=os.environ.get("SERVICENOW_USERNAME", None),
        description="Username for basic authentication",
    ),
    password: str = Field(
        default=os.environ.get("SERVICENOW_PASSWORD", None),
        description="Password for basic authentication",
    ),
    client_id: Optional[str] = Field(
        default=os.environ.get("SERVICENOW_CLIENT_ID", None),
        description="Client ID for OAuth authentication",
    ),
    client_secret: Optional[str] = Field(
        default=os.environ.get("SERVICENOW_CLIENT_SECRET", None),
        description="Client secret for OAuth authentication",
    ),
    verify: Optional[bool] = Field(
        default=to_boolean(os.environ.get("SERVICENOW_VERIFY", "True")),
        description="Whether to verify SSL certificates",
    ),
) -> dict:
    """
    Checks for conflicts in a change request in ServiceNow.
    """
    client = Api(
        url=servicenow_instance,
        username=username,
        password=password,
        client_id=client_id,
        client_secret=client_secret,
        verify=verify,
    )
    response = client.get_change_request_conflict(
        change_request_sys_id=change_request_sys_id
    )
    return response.result


@mcp.tool(
    exclude_args=[
        "servicenow_instance",
        "username",
        "password",
        "client_id",
        "client_secret",
        "verify",
    ],
    tags={"change_management"},
)
def get_standard_change_request_templates(
    servicenow_instance: str = Field(
        default=os.environ.get("SERVICENOW_INSTANCE", None),
        description="The URL of the ServiceNow instance (e.g., https://yourinstance.servicenow.com)",
    ),
    order: Optional[str] = Field(
        default=None, description="Ordering parameter for sorting results"
    ),
    name_value_pairs: Optional[Dict[str, str]] = Field(
        default=None, description="Additional name-value pairs for filtering"
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
        default=10, description="Limit for pagination"
    ),
    username: str = Field(
        default=os.environ.get("SERVICENOW_USERNAME", None),
        description="Username for basic authentication",
    ),
    password: str = Field(
        default=os.environ.get("SERVICENOW_PASSWORD", None),
        description="Password for basic authentication",
    ),
    client_id: Optional[str] = Field(
        default=os.environ.get("SERVICENOW_CLIENT_ID", None),
        description="Client ID for OAuth authentication",
    ),
    client_secret: Optional[str] = Field(
        default=os.environ.get("SERVICENOW_CLIENT_SECRET", None),
        description="Client secret for OAuth authentication",
    ),
    verify: Optional[bool] = Field(
        default=to_boolean(os.environ.get("SERVICENOW_VERIFY", "True")),
        description="Whether to verify SSL certificates",
    ),
) -> dict:
    """
    Retrieves standard change request templates from ServiceNow with optional filtering.
    """
    client = Api(
        url=servicenow_instance,
        username=username,
        password=password,
        client_id=client_id,
        client_secret=client_secret,
        verify=verify,
    )
    response = client.get_standard_change_request_templates(
        order=order,
        name_value_pairs=name_value_pairs,
        sysparm_query=sysparm_query,
        text_search=text_search,
        sysparm_offset=sysparm_offset,
        sysparm_limit=sysparm_limit,
    )
    return response.result


@mcp.tool(
    exclude_args=[
        "servicenow_instance",
        "username",
        "password",
        "client_id",
        "client_secret",
        "verify",
    ],
    tags={"change_management"},
)
def get_change_request_models(
    servicenow_instance: str = Field(
        default=os.environ.get("SERVICENOW_INSTANCE", None),
        description="The URL of the ServiceNow instance (e.g., https://yourinstance.servicenow.com)",
    ),
    order: Optional[str] = Field(
        default=None, description="Ordering parameter for sorting results"
    ),
    name_value_pairs: Optional[Dict[str, str]] = Field(
        default=None, description="Additional name-value pairs for filtering"
    ),
    sysparm_query: Optional[str] = Field(
        default=None, description="Query parameter for filtering results"
    ),
    text_search: Optional[str] = Field(
        default=None, description="Text search parameter for searching results"
    ),
    change_type: Optional[str] = Field(
        default=None, description="Type of change (emergency, normal, standard, model)"
    ),
    sysparm_offset: Optional[int] = Field(
        default=None, description="Offset for pagination"
    ),
    sysparm_limit: Optional[int] = Field(
        default=10, description="Limit for pagination"
    ),
    username: str = Field(
        default=os.environ.get("SERVICENOW_USERNAME", None),
        description="Username for basic authentication",
    ),
    password: str = Field(
        default=os.environ.get("SERVICENOW_PASSWORD", None),
        description="Password for basic authentication",
    ),
    client_id: Optional[str] = Field(
        default=os.environ.get("SERVICENOW_CLIENT_ID", None),
        description="Client ID for OAuth authentication",
    ),
    client_secret: Optional[str] = Field(
        default=os.environ.get("SERVICENOW_CLIENT_SECRET", None),
        description="Client secret for OAuth authentication",
    ),
    verify: Optional[bool] = Field(
        default=to_boolean(os.environ.get("SERVICENOW_VERIFY", "True")),
        description="Whether to verify SSL certificates",
    ),
) -> dict:
    """
    Fetches change request models from ServiceNow with optional filtering and type.
    """
    client = Api(
        url=servicenow_instance,
        username=username,
        password=password,
        client_id=client_id,
        client_secret=client_secret,
        verify=verify,
    )
    response = client.get_change_request_models(
        order=order,
        name_value_pairs=name_value_pairs,
        sysparm_query=sysparm_query,
        text_search=text_search,
        change_type=change_type,
        sysparm_offset=sysparm_offset,
        sysparm_limit=sysparm_limit,
    )
    return response.result


@mcp.tool(
    exclude_args=[
        "servicenow_instance",
        "username",
        "password",
        "client_id",
        "client_secret",
        "verify",
    ],
    tags={"change_management"},
)
def get_standard_change_request_model(
    model_sys_id: str = Field(
        description="Sys ID of the standard change request model"
    ),
    servicenow_instance: str = Field(
        default=os.environ.get("SERVICENOW_INSTANCE", None),
        description="The URL of the ServiceNow instance (e.g., https://yourinstance.servicenow.com)",
    ),
    username: str = Field(
        default=os.environ.get("SERVICENOW_USERNAME", None),
        description="Username for basic authentication",
    ),
    password: str = Field(
        default=os.environ.get("SERVICENOW_PASSWORD", None),
        description="Password for basic authentication",
    ),
    client_id: Optional[str] = Field(
        default=os.environ.get("SERVICENOW_CLIENT_ID", None),
        description="Client ID for OAuth authentication",
    ),
    client_secret: Optional[str] = Field(
        default=os.environ.get("SERVICENOW_CLIENT_SECRET", None),
        description="Client secret for OAuth authentication",
    ),
    verify: Optional[bool] = Field(
        default=to_boolean(os.environ.get("SERVICENOW_VERIFY", "True")),
        description="Whether to verify SSL certificates",
    ),
) -> dict:
    """
    Retrieves a specific standard change request model in ServiceNow by sys_id.
    """
    client = Api(
        url=servicenow_instance,
        username=username,
        password=password,
        client_id=client_id,
        client_secret=client_secret,
        verify=verify,
    )
    response = client.get_standard_change_request_model(model_sys_id=model_sys_id)
    return response.result


@mcp.tool(
    exclude_args=[
        "servicenow_instance",
        "username",
        "password",
        "client_id",
        "client_secret",
        "verify",
    ],
    tags={"change_management"},
)
def get_standard_change_request_template(
    template_sys_id: str = Field(
        description="Sys ID of the standard change request template"
    ),
    servicenow_instance: str = Field(
        default=os.environ.get("SERVICENOW_INSTANCE", None),
        description="The URL of the ServiceNow instance (e.g., https://yourinstance.servicenow.com)",
    ),
    username: str = Field(
        default=os.environ.get("SERVICENOW_USERNAME", None),
        description="Username for basic authentication",
    ),
    password: str = Field(
        default=os.environ.get("SERVICENOW_PASSWORD", None),
        description="Password for basic authentication",
    ),
    client_id: Optional[str] = Field(
        default=os.environ.get("SERVICENOW_CLIENT_ID", None),
        description="Client ID for OAuth authentication",
    ),
    client_secret: Optional[str] = Field(
        default=os.environ.get("SERVICENOW_CLIENT_SECRET", None),
        description="Client secret for OAuth authentication",
    ),
    verify: Optional[bool] = Field(
        default=to_boolean(os.environ.get("SERVICENOW_VERIFY", "True")),
        description="Whether to verify SSL certificates",
    ),
) -> dict:
    """
    Gets a specific standard change request template in ServiceNow by sys_id.
    """
    client = Api(
        url=servicenow_instance,
        username=username,
        password=password,
        client_id=client_id,
        client_secret=client_secret,
        verify=verify,
    )
    response = client.get_standard_change_request_template(
        template_sys_id=template_sys_id
    )
    return response.result


@mcp.tool(
    exclude_args=[
        "servicenow_instance",
        "username",
        "password",
        "client_id",
        "client_secret",
        "verify",
    ],
    tags={"change_management"},
)
def get_change_request_worker(
    worker_sys_id: str = Field(description="Sys ID of the change request worker"),
    servicenow_instance: str = Field(
        default=os.environ.get("SERVICENOW_INSTANCE", None),
        description="The URL of the ServiceNow instance (e.g., https://yourinstance.servicenow.com)",
    ),
    username: str = Field(
        default=os.environ.get("SERVICENOW_USERNAME", None),
        description="Username for basic authentication",
    ),
    password: str = Field(
        default=os.environ.get("SERVICENOW_PASSWORD", None),
        description="Password for basic authentication",
    ),
    client_id: Optional[str] = Field(
        default=os.environ.get("SERVICENOW_CLIENT_ID", None),
        description="Client ID for OAuth authentication",
    ),
    client_secret: Optional[str] = Field(
        default=os.environ.get("SERVICENOW_CLIENT_SECRET", None),
        description="Client secret for OAuth authentication",
    ),
    verify: Optional[bool] = Field(
        default=to_boolean(os.environ.get("SERVICENOW_VERIFY", "True")),
        description="Whether to verify SSL certificates",
    ),
) -> dict:
    """
    Retrieves details of a change request worker in ServiceNow by sys_id.
    """
    client = Api(
        url=servicenow_instance,
        username=username,
        password=password,
        client_id=client_id,
        client_secret=client_secret,
        verify=verify,
    )
    response = client.get_change_request_worker(worker_sys_id=worker_sys_id)
    return response.result


@mcp.tool(
    exclude_args=[
        "servicenow_instance",
        "username",
        "password",
        "client_id",
        "client_secret",
        "verify",
    ],
    tags={"change_management"},
)
def create_change_request(
    name_value_pairs: Dict[str, str] = Field(
        description="Name-value pairs providing details for the new change request"
    ),
    servicenow_instance: str = Field(
        default=os.environ.get("SERVICENOW_INSTANCE", None),
        description="The URL of the ServiceNow instance (e.g., https://yourinstance.servicenow.com)",
    ),
    change_type: Optional[str] = Field(
        default=None, description="Type of change (emergency, normal, standard)"
    ),
    standard_change_template_id: Optional[str] = Field(
        default=None,
        description="Sys ID of the standard change request template (if applicable)",
    ),
    username: str = Field(
        default=os.environ.get("SERVICENOW_USERNAME", None),
        description="Username for basic authentication",
    ),
    password: str = Field(
        default=os.environ.get("SERVICENOW_PASSWORD", None),
        description="Password for basic authentication",
    ),
    client_id: Optional[str] = Field(
        default=os.environ.get("SERVICENOW_CLIENT_ID", None),
        description="Client ID for OAuth authentication",
    ),
    client_secret: Optional[str] = Field(
        default=os.environ.get("SERVICENOW_CLIENT_SECRET", None),
        description="Client secret for OAuth authentication",
    ),
    verify: Optional[bool] = Field(
        default=to_boolean(os.environ.get("SERVICENOW_VERIFY", "True")),
        description="Whether to verify SSL certificates",
    ),
) -> dict:
    """
    Creates a new change request in ServiceNow with specified details and type.
    """
    client = Api(
        url=servicenow_instance,
        username=username,
        password=password,
        client_id=client_id,
        client_secret=client_secret,
        verify=verify,
    )
    response = client.create_change_request(
        name_value_pairs=name_value_pairs,
        change_type=change_type,
        standard_change_template_id=standard_change_template_id,
    )
    return response.result


@mcp.tool(
    exclude_args=[
        "servicenow_instance",
        "username",
        "password",
        "client_id",
        "client_secret",
        "verify",
    ],
    tags={"change_management"},
)
def create_change_request_task(
    change_request_sys_id: str = Field(description="Sys ID of the change request"),
    data: Dict[str, str] = Field(
        description="Name-value pairs providing details for the new task"
    ),
    servicenow_instance: str = Field(
        default=os.environ.get("SERVICENOW_INSTANCE", None),
        description="The URL of the ServiceNow instance (e.g., https://yourinstance.servicenow.com)",
    ),
    username: str = Field(
        default=os.environ.get("SERVICENOW_USERNAME", None),
        description="Username for basic authentication",
    ),
    password: str = Field(
        default=os.environ.get("SERVICENOW_PASSWORD", None),
        description="Password for basic authentication",
    ),
    client_id: Optional[str] = Field(
        default=os.environ.get("SERVICENOW_CLIENT_ID", None),
        description="Client ID for OAuth authentication",
    ),
    client_secret: Optional[str] = Field(
        default=os.environ.get("SERVICENOW_CLIENT_SECRET", None),
        description="Client secret for OAuth authentication",
    ),
    verify: Optional[bool] = Field(
        default=to_boolean(os.environ.get("SERVICENOW_VERIFY", "True")),
        description="Whether to verify SSL certificates",
    ),
) -> dict:
    """
    Creates a task for a change request in ServiceNow with provided details.
    """
    client = Api(
        url=servicenow_instance,
        username=username,
        password=password,
        client_id=client_id,
        client_secret=client_secret,
        verify=verify,
    )
    response = client.create_change_request_task(
        change_request_sys_id=change_request_sys_id, data=data
    )
    return response.result


@mcp.tool(
    exclude_args=[
        "servicenow_instance",
        "username",
        "password",
        "client_id",
        "client_secret",
        "verify",
    ],
    tags={"change_management"},
)
def create_change_request_ci_association(
    change_request_sys_id: str = Field(description="Sys ID of the change request"),
    cmdb_ci_sys_ids: List[str] = Field(
        description="List of Sys IDs of CIs to associate with the change request"
    ),
    association_type: str = Field(
        description="Type of association (affected, impacted, offering)"
    ),
    servicenow_instance: str = Field(
        default=os.environ.get("SERVICENOW_INSTANCE", None),
        description="The URL of the ServiceNow instance (e.g., https://yourinstance.servicenow.com)",
    ),
    refresh_impacted_services: Optional[bool] = Field(
        default=None,
        description="Flag to refresh impacted services (applicable for 'affected' association)",
    ),
    username: str = Field(
        default=os.environ.get("SERVICENOW_USERNAME", None),
        description="Username for basic authentication",
    ),
    password: str = Field(
        default=os.environ.get("SERVICENOW_PASSWORD", None),
        description="Password for basic authentication",
    ),
    client_id: Optional[str] = Field(
        default=os.environ.get("SERVICENOW_CLIENT_ID", None),
        description="Client ID for OAuth authentication",
    ),
    client_secret: Optional[str] = Field(
        default=os.environ.get("SERVICENOW_CLIENT_SECRET", None),
        description="Client secret for OAuth authentication",
    ),
    verify: Optional[bool] = Field(
        default=to_boolean(os.environ.get("SERVICENOW_VERIFY", "True")),
        description="Whether to verify SSL certificates",
    ),
) -> dict:
    """
    Associates Configuration Items (CIs) with a change request in ServiceNow.
    """
    client = Api(
        url=servicenow_instance,
        username=username,
        password=password,
        client_id=client_id,
        client_secret=client_secret,
        verify=verify,
    )
    response = client.create_change_request_ci_association(
        change_request_sys_id=change_request_sys_id,
        cmdb_ci_sys_ids=cmdb_ci_sys_ids,
        association_type=association_type,
        refresh_impacted_services=refresh_impacted_services,
    )
    return response.result


@mcp.tool(
    exclude_args=[
        "servicenow_instance",
        "username",
        "password",
        "client_id",
        "client_secret",
        "verify",
    ],
    tags={"change_management"},
)
def calculate_standard_change_request_risk(
    change_request_sys_id: str = Field(
        description="Sys ID of the standard change request"
    ),
    servicenow_instance: str = Field(
        default=os.environ.get("SERVICENOW_INSTANCE", None),
        description="The URL of the ServiceNow instance (e.g., https://yourinstance.servicenow.com)",
    ),
    username: str = Field(
        default=os.environ.get("SERVICENOW_USERNAME", None),
        description="Username for basic authentication",
    ),
    password: str = Field(
        default=os.environ.get("SERVICENOW_PASSWORD", None),
        description="Password for basic authentication",
    ),
    client_id: Optional[str] = Field(
        default=os.environ.get("SERVICENOW_CLIENT_ID", None),
        description="Client ID for OAuth authentication",
    ),
    client_secret: Optional[str] = Field(
        default=os.environ.get("SERVICENOW_CLIENT_SECRET", None),
        description="Client secret for OAuth authentication",
    ),
    verify: Optional[bool] = Field(
        default=to_boolean(os.environ.get("SERVICENOW_VERIFY", "True")),
        description="Whether to verify SSL certificates",
    ),
) -> dict:
    """
    Calculates the risk for a standard change request in ServiceNow.
    """
    client = Api(
        url=servicenow_instance,
        username=username,
        password=password,
        client_id=client_id,
        client_secret=client_secret,
        verify=verify,
    )
    response = client.calculate_standard_change_request_risk(
        change_request_sys_id=change_request_sys_id
    )
    return response.result


@mcp.tool(
    exclude_args=[
        "servicenow_instance",
        "username",
        "password",
        "client_id",
        "client_secret",
        "verify",
    ],
    tags={"change_management"},
)
def check_change_request_conflict(
    change_request_sys_id: str = Field(description="Sys ID of the change request"),
    servicenow_instance: str = Field(
        default=os.environ.get("SERVICENOW_INSTANCE", None),
        description="The URL of the ServiceNow instance (e.g., https://yourinstance.servicenow.com)",
    ),
    username: str = Field(
        default=os.environ.get("SERVICENOW_USERNAME", None),
        description="Username for basic authentication",
    ),
    password: str = Field(
        default=os.environ.get("SERVICENOW_PASSWORD", None),
        description="Password for basic authentication",
    ),
    client_id: Optional[str] = Field(
        default=os.environ.get("SERVICENOW_CLIENT_ID", None),
        description="Client ID for OAuth authentication",
    ),
    client_secret: Optional[str] = Field(
        default=os.environ.get("SERVICENOW_CLIENT_SECRET", None),
        description="Client secret for OAuth authentication",
    ),
    verify: Optional[bool] = Field(
        default=to_boolean(os.environ.get("SERVICENOW_VERIFY", "True")),
        description="Whether to verify SSL certificates",
    ),
) -> dict:
    """
    Checks for conflicts in a change request in ServiceNow.
    """
    client = Api(
        url=servicenow_instance,
        username=username,
        password=password,
        client_id=client_id,
        client_secret=client_secret,
        verify=verify,
    )
    response = client.check_change_request_conflict(
        change_request_sys_id=change_request_sys_id
    )
    return response.result


@mcp.tool(
    exclude_args=[
        "servicenow_instance",
        "username",
        "password",
        "client_id",
        "client_secret",
        "verify",
    ],
    tags={"change_management"},
)
def refresh_change_request_impacted_services(
    change_request_sys_id: str = Field(description="Sys ID of the change request"),
    servicenow_instance: str = Field(
        default=os.environ.get("SERVICENOW_INSTANCE", None),
        description="The URL of the ServiceNow instance (e.g., https://yourinstance.servicenow.com)",
    ),
    username: str = Field(
        default=os.environ.get("SERVICENOW_USERNAME", None),
        description="Username for basic authentication",
    ),
    password: str = Field(
        default=os.environ.get("SERVICENOW_PASSWORD", None),
        description="Password for basic authentication",
    ),
    client_id: Optional[str] = Field(
        default=os.environ.get("SERVICENOW_CLIENT_ID", None),
        description="Client ID for OAuth authentication",
    ),
    client_secret: Optional[str] = Field(
        default=os.environ.get("SERVICENOW_CLIENT_SECRET", None),
        description="Client secret for OAuth authentication",
    ),
    verify: Optional[bool] = Field(
        default=to_boolean(os.environ.get("SERVICENOW_VERIFY", "True")),
        description="Whether to verify SSL certificates",
    ),
) -> dict:
    """
    Refreshes the impacted services for a change request in ServiceNow.
    """
    client = Api(
        url=servicenow_instance,
        username=username,
        password=password,
        client_id=client_id,
        client_secret=client_secret,
        verify=verify,
    )
    response = client.refresh_change_request_impacted_services(
        change_request_sys_id=change_request_sys_id
    )
    return response.result


@mcp.tool(
    exclude_args=[
        "servicenow_instance",
        "username",
        "password",
        "client_id",
        "client_secret",
        "verify",
    ],
    tags={"change_management"},
)
def approve_change_request(
    change_request_sys_id: str = Field(description="Sys ID of the change request"),
    state: str = Field(
        description="State to set the change request to (approved or rejected)"
    ),
    servicenow_instance: str = Field(
        default=os.environ.get("SERVICENOW_INSTANCE", None),
        description="The URL of the ServiceNow instance (e.g., https://yourinstance.servicenow.com)",
    ),
    username: str = Field(
        default=os.environ.get("SERVICENOW_USERNAME", None),
        description="Username for basic authentication",
    ),
    password: str = Field(
        default=os.environ.get("SERVICENOW_PASSWORD", None),
        description="Password for basic authentication",
    ),
    client_id: Optional[str] = Field(
        default=os.environ.get("SERVICENOW_CLIENT_ID", None),
        description="Client ID for OAuth authentication",
    ),
    client_secret: Optional[str] = Field(
        default=os.environ.get("SERVICENOW_CLIENT_SECRET", None),
        description="Client secret for OAuth authentication",
    ),
    verify: Optional[bool] = Field(
        default=to_boolean(os.environ.get("SERVICENOW_VERIFY", "True")),
        description="Whether to verify SSL certificates",
    ),
) -> dict:
    """
    Approves or rejects a change request in ServiceNow by setting its state.
    """
    client = Api(
        url=servicenow_instance,
        username=username,
        password=password,
        client_id=client_id,
        client_secret=client_secret,
        verify=verify,
    )
    response = client.approve_change_request(
        change_request_sys_id=change_request_sys_id, state=state
    )
    return response.result


@mcp.tool(
    exclude_args=[
        "servicenow_instance",
        "username",
        "password",
        "client_id",
        "client_secret",
        "verify",
    ],
    tags={"change_management"},
)
def update_change_request(
    change_request_sys_id: str = Field(description="Sys ID of the change request"),
    name_value_pairs: Dict[str, str] = Field(
        description="New name-value pairs providing updated details for the change request"
    ),
    servicenow_instance: str = Field(
        default=os.environ.get("SERVICENOW_INSTANCE", None),
        description="The URL of the ServiceNow instance (e.g., https://yourinstance.servicenow.com)",
    ),
    change_type: Optional[str] = Field(
        default=None, description="Type of change (emergency, normal, standard, model)"
    ),
    username: str = Field(
        default=os.environ.get("SERVICENOW_USERNAME", None),
        description="Username for basic authentication",
    ),
    password: str = Field(
        default=os.environ.get("SERVICENOW_PASSWORD", None),
        description="Password for basic authentication",
    ),
    client_id: Optional[str] = Field(
        default=os.environ.get("SERVICENOW_CLIENT_ID", None),
        description="Client ID for OAuth authentication",
    ),
    client_secret: Optional[str] = Field(
        default=os.environ.get("SERVICENOW_CLIENT_SECRET", None),
        description="Client secret for OAuth authentication",
    ),
    verify: Optional[bool] = Field(
        default=to_boolean(os.environ.get("SERVICENOW_VERIFY", "True")),
        description="Whether to verify SSL certificates",
    ),
) -> dict:
    """
    Updates a change request in ServiceNow with new details and type.
    """
    client = Api(
        url=servicenow_instance,
        username=username,
        password=password,
        client_id=client_id,
        client_secret=client_secret,
        verify=verify,
    )
    response = client.update_change_request(
        change_request_sys_id=change_request_sys_id,
        name_value_pairs=name_value_pairs,
        change_type=change_type,
    )
    return response.result


@mcp.tool(
    exclude_args=[
        "servicenow_instance",
        "username",
        "password",
        "client_id",
        "client_secret",
        "verify",
    ],
    tags={"change_management"},
)
def update_change_request_first_available(
    change_request_sys_id: str = Field(description="Sys ID of the change request"),
    servicenow_instance: str = Field(
        default=os.environ.get("SERVICENOW_INSTANCE", None),
        description="The URL of the ServiceNow instance (e.g., https://yourinstance.servicenow.com)",
    ),
    username: str = Field(
        default=os.environ.get("SERVICENOW_USERNAME", None),
        description="Username for basic authentication",
    ),
    password: str = Field(
        default=os.environ.get("SERVICENOW_PASSWORD", None),
        description="Password for basic authentication",
    ),
    client_id: Optional[str] = Field(
        default=os.environ.get("SERVICENOW_CLIENT_ID", None),
        description="Client ID for OAuth authentication",
    ),
    client_secret: Optional[str] = Field(
        default=os.environ.get("SERVICENOW_CLIENT_SECRET", None),
        description="Client secret for OAuth authentication",
    ),
    verify: Optional[bool] = Field(
        default=to_boolean(os.environ.get("SERVICENOW_VERIFY", "True")),
        description="Whether to verify SSL certificates",
    ),
) -> dict:
    """
    Updates a change request to the first available state in ServiceNow.
    """
    client = Api(
        url=servicenow_instance,
        username=username,
        password=password,
        client_id=client_id,
        client_secret=client_secret,
        verify=verify,
    )
    response = client.update_change_request_first_available(
        change_request_sys_id=change_request_sys_id
    )
    return response.result


@mcp.tool(
    exclude_args=[
        "servicenow_instance",
        "username",
        "password",
        "client_id",
        "client_secret",
        "verify",
    ],
    tags={"change_management"},
)
def update_change_request_task(
    change_request_sys_id: str = Field(description="Sys ID of the change request"),
    change_request_task_sys_id: str = Field(
        description="Sys ID of the change request task"
    ),
    name_value_pairs: Dict[str, str] = Field(
        description="New name-value pairs providing updated details for the task"
    ),
    servicenow_instance: str = Field(
        default=os.environ.get("SERVICENOW_INSTANCE", None),
        description="The URL of the ServiceNow instance (e.g., https://yourinstance.servicenow.com)",
    ),
    username: str = Field(
        default=os.environ.get("SERVICENOW_USERNAME", None),
        description="Username for basic authentication",
    ),
    password: str = Field(
        default=os.environ.get("SERVICENOW_PASSWORD", None),
        description="Password for basic authentication",
    ),
    client_id: Optional[str] = Field(
        default=os.environ.get("SERVICENOW_CLIENT_ID", None),
        description="Client ID for OAuth authentication",
    ),
    client_secret: Optional[str] = Field(
        default=os.environ.get("SERVICENOW_CLIENT_SECRET", None),
        description="Client secret for OAuth authentication",
    ),
    verify: Optional[bool] = Field(
        default=to_boolean(os.environ.get("SERVICENOW_VERIFY", "True")),
        description="Whether to verify SSL certificates",
    ),
) -> dict:
    """
    Updates a task for a change request in ServiceNow with new details.
    """
    client = Api(
        url=servicenow_instance,
        username=username,
        password=password,
        client_id=client_id,
        client_secret=client_secret,
        verify=verify,
    )
    response = client.update_change_request_task(
        change_request_sys_id=change_request_sys_id,
        change_request_task_sys_id=change_request_task_sys_id,
        name_value_pairs=name_value_pairs,
    )
    return response.result


@mcp.tool(
    exclude_args=[
        "servicenow_instance",
        "username",
        "password",
        "client_id",
        "client_secret",
        "verify",
    ],
    tags={"change_management"},
)
def delete_change_request(
    change_request_sys_id: str = Field(description="Sys ID of the change request"),
    servicenow_instance: str = Field(
        default=os.environ.get("SERVICENOW_INSTANCE", None),
        description="The URL of the ServiceNow instance (e.g., https://yourinstance.servicenow.com)",
    ),
    change_type: Optional[str] = Field(
        default=None, description="Type of change (emergency, normal, standard)"
    ),
    username: str = Field(
        default=os.environ.get("SERVICENOW_USERNAME", None),
        description="Username for basic authentication",
    ),
    password: str = Field(
        default=os.environ.get("SERVICENOW_PASSWORD", None),
        description="Password for basic authentication",
    ),
    client_id: Optional[str] = Field(
        default=os.environ.get("SERVICENOW_CLIENT_ID", None),
        description="Client ID for OAuth authentication",
    ),
    client_secret: Optional[str] = Field(
        default=os.environ.get("SERVICENOW_CLIENT_SECRET", None),
        description="Client secret for OAuth authentication",
    ),
    verify: Optional[bool] = Field(
        default=to_boolean(os.environ.get("SERVICENOW_VERIFY", "True")),
        description="Whether to verify SSL certificates",
    ),
) -> dict:
    """
    Deletes a change request from ServiceNow by sys_id and type.
    """
    client = Api(
        url=servicenow_instance,
        username=username,
        password=password,
        client_id=client_id,
        client_secret=client_secret,
        verify=verify,
    )
    response = client.delete_change_request(
        change_request_sys_id=change_request_sys_id, change_type=change_type
    )
    return response.result


@mcp.tool(
    exclude_args=[
        "servicenow_instance",
        "username",
        "password",
        "client_id",
        "client_secret",
        "verify",
    ],
    tags={"change_management"},
)
def delete_change_request_task(
    change_request_sys_id: str = Field(description="Sys ID of the change request"),
    task_sys_id: str = Field(
        description="Sys ID of the task associated with the change request"
    ),
    servicenow_instance: str = Field(
        default=os.environ.get("SERVICENOW_INSTANCE", None),
        description="The URL of the ServiceNow instance (e.g., https://yourinstance.servicenow.com)",
    ),
    username: str = Field(
        default=os.environ.get("SERVICENOW_USERNAME", None),
        description="Username for basic authentication",
    ),
    password: str = Field(
        default=os.environ.get("SERVICENOW_PASSWORD", None),
        description="Password for basic authentication",
    ),
    client_id: Optional[str] = Field(
        default=os.environ.get("SERVICENOW_CLIENT_ID", None),
        description="Client ID for OAuth authentication",
    ),
    client_secret: Optional[str] = Field(
        default=os.environ.get("SERVICENOW_CLIENT_SECRET", None),
        description="Client secret for OAuth authentication",
    ),
    verify: Optional[bool] = Field(
        default=to_boolean(os.environ.get("SERVICENOW_VERIFY", "True")),
        description="Whether to verify SSL certificates",
    ),
) -> dict:
    """
    Deletes a task associated with a change request in ServiceNow.
    """
    client = Api(
        url=servicenow_instance,
        username=username,
        password=password,
        client_id=client_id,
        client_secret=client_secret,
        verify=verify,
    )
    response = client.delete_change_request_task(
        change_request_sys_id=change_request_sys_id, task_sys_id=task_sys_id
    )
    return response.result


@mcp.tool(
    exclude_args=[
        "servicenow_instance",
        "username",
        "password",
        "client_id",
        "client_secret",
        "verify",
    ],
    tags={"change_management"},
)
def delete_change_request_conflict_scan(
    change_request_sys_id: str = Field(description="Sys ID of the change request"),
    task_sys_id: str = Field(
        description="Sys ID of the task associated with the change request"
    ),
    servicenow_instance: str = Field(
        default=os.environ.get("SERVICENOW_INSTANCE", None),
        description="The URL of the ServiceNow instance (e.g., https://yourinstance.servicenow.com)",
    ),
    username: str = Field(
        default=os.environ.get("SERVICENOW_USERNAME", None),
        description="Username for basic authentication",
    ),
    password: str = Field(
        default=os.environ.get("SERVICENOW_PASSWORD", None),
        description="Password for basic authentication",
    ),
    client_id: Optional[str] = Field(
        default=os.environ.get("SERVICENOW_CLIENT_ID", None),
        description="Client ID for OAuth authentication",
    ),
    client_secret: Optional[str] = Field(
        default=os.environ.get("SERVICENOW_CLIENT_SECRET", None),
        description="Client secret for OAuth authentication",
    ),
    verify: Optional[bool] = Field(
        default=to_boolean(os.environ.get("SERVICENOW_VERIFY", "True")),
        description="Whether to verify SSL certificates",
    ),
) -> dict:
    """
    Deletes a conflict scan for a change request in ServiceNow.
    """
    client = Api(
        url=servicenow_instance,
        username=username,
        password=password,
        client_id=client_id,
        client_secret=client_secret,
        verify=verify,
    )
    response = client.delete_change_request_conflict_scan(
        change_request_sys_id=change_request_sys_id, task_sys_id=task_sys_id
    )
    return response.result


# Import Set Tools
@mcp.tool(
    exclude_args=[
        "servicenow_instance",
        "username",
        "password",
        "client_id",
        "client_secret",
        "verify",
    ],
    tags={"import_sets"},
)
def get_import_set(
    table: str = Field(
        description="The name of the table associated with the import set"
    ),
    import_set_sys_id: str = Field(description="The sys_id of the import set record"),
    servicenow_instance: str = Field(
        default=os.environ.get("SERVICENOW_INSTANCE", None),
        description="The URL of the ServiceNow instance (e.g., https://yourinstance.servicenow.com)",
    ),
    username: str = Field(
        default=os.environ.get("SERVICENOW_USERNAME", None),
        description="Username for basic authentication",
    ),
    password: str = Field(
        default=os.environ.get("SERVICENOW_PASSWORD", None),
        description="Password for basic authentication",
    ),
    client_id: Optional[str] = Field(
        default=os.environ.get("SERVICENOW_CLIENT_ID", None),
        description="Client ID for OAuth authentication",
    ),
    client_secret: Optional[str] = Field(
        default=os.environ.get("SERVICENOW_CLIENT_SECRET", None),
        description="Client secret for OAuth authentication",
    ),
    verify: Optional[bool] = Field(
        default=to_boolean(os.environ.get("SERVICENOW_VERIFY", "True")),
        description="Whether to verify SSL certificates",
    ),
) -> dict:
    """
    Retrieves details of a specific import set record from a ServiceNow instance.
    """
    client = Api(
        url=servicenow_instance,
        username=username,
        password=password,
        client_id=client_id,
        client_secret=client_secret,
        verify=verify,
    )
    response = client.get_import_set(table=table, import_set_sys_id=import_set_sys_id)
    return response.result


@mcp.tool(
    exclude_args=[
        "servicenow_instance",
        "username",
        "password",
        "client_id",
        "client_secret",
        "verify",
    ],
    tags={"import_sets"},
)
def insert_import_set(
    table: str = Field(
        description="The name of the table associated with the import set"
    ),
    data: Dict[str, str] = Field(
        description="Dictionary containing the field values for the new import set record"
    ),
    servicenow_instance: str = Field(
        default=os.environ.get("SERVICENOW_INSTANCE", None),
        description="The URL of the ServiceNow instance (e.g., https://yourinstance.servicenow.com)",
    ),
    username: str = Field(
        default=os.environ.get("SERVICENOW_USERNAME", None),
        description="Username for basic authentication",
    ),
    password: str = Field(
        default=os.environ.get("SERVICENOW_PASSWORD", None),
        description="Password for basic authentication",
    ),
    client_id: Optional[str] = Field(
        default=os.environ.get("SERVICENOW_CLIENT_ID", None),
        description="Client ID for OAuth authentication",
    ),
    client_secret: Optional[str] = Field(
        default=os.environ.get("SERVICENOW_CLIENT_SECRET", None),
        description="Client secret for OAuth authentication",
    ),
    verify: Optional[bool] = Field(
        default=to_boolean(os.environ.get("SERVICENOW_VERIFY", "True")),
        description="Whether to verify SSL certificates",
    ),
) -> dict:
    """
    Inserts a new record into a specified import set on a ServiceNow instance.
    """
    client = Api(
        url=servicenow_instance,
        username=username,
        password=password,
        client_id=client_id,
        client_secret=client_secret,
        verify=verify,
    )
    response = client.insert_import_set(table=table, data=data)
    return response.result


@mcp.tool(
    exclude_args=[
        "servicenow_instance",
        "username",
        "password",
        "client_id",
        "client_secret",
        "verify",
    ],
    tags={"import_sets"},
)
def insert_multiple_import_sets(
    table: str = Field(
        description="The name of the table associated with the import set"
    ),
    data: List[Dict[str, str]] = Field(
        description="List of dictionaries containing field values for multiple new import set records"
    ),
    servicenow_instance: str = Field(
        default=os.environ.get("SERVICENOW_INSTANCE", None),
        description="The URL of the ServiceNow instance (e.g., https://yourinstance.servicenow.com)",
    ),
    username: str = Field(
        default=os.environ.get("SERVICENOW_USERNAME", None),
        description="Username for basic authentication",
    ),
    password: str = Field(
        default=os.environ.get("SERVICENOW_PASSWORD", None),
        description="Password for basic authentication",
    ),
    client_id: Optional[str] = Field(
        default=os.environ.get("SERVICENOW_CLIENT_ID", None),
        description="Client ID for OAuth authentication",
    ),
    client_secret: Optional[str] = Field(
        default=os.environ.get("SERVICENOW_CLIENT_SECRET", None),
        description="Client secret for OAuth authentication",
    ),
    verify: Optional[bool] = Field(
        default=to_boolean(os.environ.get("SERVICENOW_VERIFY", "True")),
        description="Whether to verify SSL certificates",
    ),
) -> dict:
    """
    Inserts multiple records into a specified import set on a ServiceNow instance.
    """
    client = Api(
        url=servicenow_instance,
        username=username,
        password=password,
        client_id=client_id,
        client_secret=client_secret,
        verify=verify,
    )
    response = client.insert_multiple_import_sets(table=table, data=data)
    return response.result


# Incident Tools
@mcp.tool(
    exclude_args=[
        "servicenow_instance",
        "username",
        "password",
        "client_id",
        "client_secret",
        "verify",
    ],
    tags={"incidents"},
)
def get_incidents(
    incident_id: Optional[str] = Field(
        default=None,
        description="The sys_id of the incident record, if retrieving a specific incident",
    ),
    servicenow_instance: str = Field(
        default=os.environ.get("SERVICENOW_INSTANCE", None),
        description="The URL of the ServiceNow instance (e.g., https://yourinstance.servicenow.com)",
    ),
    username: str = Field(
        default=os.environ.get("SERVICENOW_USERNAME", None),
        description="Username for basic authentication",
    ),
    password: str = Field(
        default=os.environ.get("SERVICENOW_PASSWORD", None),
        description="Password for basic authentication",
    ),
    client_id: Optional[str] = Field(
        default=os.environ.get("SERVICENOW_CLIENT_ID", None),
        description="Client ID for OAuth authentication",
    ),
    client_secret: Optional[str] = Field(
        default=os.environ.get("SERVICENOW_CLIENT_SECRET", None),
        description="Client secret for OAuth authentication",
    ),
    verify: Optional[bool] = Field(
        default=to_boolean(os.environ.get("SERVICENOW_VERIFY", "True")),
        description="Whether to verify SSL certificates",
    ),
) -> Union[List, Dict]:
    """
    Retrieves incident records from a ServiceNow instance, optionally by specific incident ID.
    """
    client = Api(
        url=servicenow_instance,
        username=username,
        password=password,
        client_id=client_id,
        client_secret=client_secret,
        verify=verify,
    )
    if incident_id:
        response = client.get_incident(incident_id=incident_id)
    else:
        response = client.get_incidents()
    return response.result


@mcp.tool(
    exclude_args=[
        "servicenow_instance",
        "username",
        "password",
        "client_id",
        "client_secret",
        "verify",
    ],
    tags={"incidents"},
)
def create_incident(
    data: Dict[str, str] = Field(
        description="Dictionary containing the field values for the new incident record"
    ),
    servicenow_instance: str = Field(
        default=os.environ.get("SERVICENOW_INSTANCE", None),
        description="The URL of the ServiceNow instance (e.g., https://yourinstance.servicenow.com)",
    ),
    username: str = Field(
        default=os.environ.get("SERVICENOW_USERNAME", None),
        description="Username for basic authentication",
    ),
    password: str = Field(
        default=os.environ.get("SERVICENOW_PASSWORD", None),
        description="Password for basic authentication",
    ),
    client_id: Optional[str] = Field(
        default=os.environ.get("SERVICENOW_CLIENT_ID", None),
        description="Client ID for OAuthBlog authentication",
    ),
    client_secret: Optional[str] = Field(
        default=os.environ.get("SERVICENOW_CLIENT_SECRET", None),
        description="Client secret for OAuth authentication",
    ),
    verify: Optional[bool] = Field(
        default=to_boolean(os.environ.get("SERVICENOW_VERIFY", "True")),
        description="Whether to verify SSL certificates",
    ),
) -> dict:
    """
    Creates a new incident record on a ServiceNow instance with provided details.
    """
    client = Api(
        url=servicenow_instance,
        username=username,
        password=password,
        client_id=client_id,
        client_secret=client_secret,
        verify=verify,
    )
    response = client.create_incident(data=data)
    return response.result


# Knowledge Management Tools
@mcp.tool(
    exclude_args=[
        "servicenow_instance",
        "username",
        "password",
        "client_id",
        "client_secret",
        "verify",
    ],
    tags={"knowledge_management"},
)
def get_knowledge_articles(
    servicenow_instance: str = Field(
        default=os.environ.get("SERVICENOW_INSTANCE", None),
        description="The URL of the ServiceNow instance (e.g., https://yourinstance.servicenow.com)",
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
        default=10, description="Maximum number of records to return"
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
    username: str = Field(
        default=os.environ.get("SERVICENOW_USERNAME", None),
        description="Username for basic authentication",
    ),
    password: str = Field(
        default=os.environ.get("SERVICENOW_PASSWORD", None),
        description="Password for basic authentication",
    ),
    client_id: Optional[str] = Field(
        default=os.environ.get("SERVICENOW_CLIENT_ID", None),
        description="Client ID for OAuth authentication",
    ),
    client_secret: Optional[str] = Field(
        default=os.environ.get("SERVICENOW_CLIENT_SECRET", None),
        description="Client secret for OAuth authentication",
    ),
    verify: Optional[bool] = Field(
        default=to_boolean(os.environ.get("SERVICENOW_VERIFY", "True")),
        description="Whether to verify SSL certificates",
    ),
) -> Union[List, Dict]:
    """
    Get all Knowledge Base articles from a ServiceNow instance.
    """
    client = Api(
        url=servicenow_instance,
        username=username,
        password=password,
        client_id=client_id,
        client_secret=client_secret,
        verify=verify,
    )
    response = client.get_knowledge_articles(
        filter=filter,
        sysparm_fields=sysparm_fields,
        sysparm_limit=sysparm_limit,
        sysparm_offset=sysparm_offset,
        sysparm_query=sysparm_query,
        sysparm_query_category=sysparm_query_category,
        kb=kb,
        language=language,
    )
    return response.result


@mcp.tool(
    exclude_args=[
        "servicenow_instance",
        "username",
        "password",
        "client_id",
        "client_secret",
        "verify",
    ],
    tags={"knowledge_management"},
)
def get_knowledge_article(
    article_sys_id: str = Field(description="The sys_id of the Knowledge Base article"),
    servicenow_instance: str = Field(
        default=os.environ.get("SERVICENOW_INSTANCE", None),
        description="The URL of the ServiceNow instance (e.g., https://yourinstance.servicenow.com)",
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
        default=10, description="Maximum number of records to return"
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
    username: str = Field(
        default=os.environ.get("SERVICENOW_USERNAME", None),
        description="Username for basic authentication",
    ),
    password: str = Field(
        default=os.environ.get("SERVICENOW_PASSWORD", None),
        description="Password for basic authentication",
    ),
    client_id: Optional[str] = Field(
        default=os.environ.get("SERVICENOW_CLIENT_ID", None),
        description="Client ID for OAuth authentication",
    ),
    client_secret: Optional[str] = Field(
        default=os.environ.get("SERVICENOW_CLIENT_SECRET", None),
        description="Client secret for OAuth authentication",
    ),
    verify: Optional[bool] = Field(
        default=to_boolean(os.environ.get("SERVICENOW_VERIFY", "True")),
        description="Whether to verify SSL certificates",
    ),
) -> dict:
    """
    Get a specific Knowledge Base article from a ServiceNow instance.
    """
    client = Api(
        url=servicenow_instance,
        username=username,
        password=password,
        client_id=client_id,
        client_secret=client_secret,
        verify=verify,
    )
    response = client.get_knowledge_article(
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
    return response.result


@mcp.tool(
    exclude_args=[
        "servicenow_instance",
        "username",
        "password",
        "client_id",
        "client_secret",
        "verify",
    ],
    tags={"knowledge_management"},
)
def get_knowledge_article_attachment(
    article_sys_id: str = Field(description="The sys_id of the Knowledge Base article"),
    attachment_sys_id: str = Field(description="The sys_id of the attachment"),
    servicenow_instance: str = Field(
        default=os.environ.get("SERVICENOW_INSTANCE", None),
        description="The URL of the ServiceNow instance (e.g., https://yourinstance.servicenow.com)",
    ),
    username: str = Field(
        default=os.environ.get("SERVICENOW_USERNAME", None),
        description="Username for basic authentication",
    ),
    password: str = Field(
        default=os.environ.get("SERVICENOW_PASSWORD", None),
        description="Password for basic authentication",
    ),
    client_id: Optional[str] = Field(
        default=os.environ.get("SERVICENOW_CLIENT_ID", None),
        description="Client ID for OAuth authentication",
    ),
    client_secret: Optional[str] = Field(
        default=os.environ.get("SERVICENOW_CLIENT_SECRET", None),
        description="Client secret for OAuth authentication",
    ),
    verify: Optional[bool] = Field(
        default=to_boolean(os.environ.get("SERVICENOW_VERIFY", "True")),
        description="Whether to verify SSL certificates",
    ),
) -> dict:
    """
    Get a Knowledge Base article attachment from a ServiceNow instance.
    """
    client = Api(
        url=servicenow_instance,
        username=username,
        password=password,
        client_id=client_id,
        client_secret=client_secret,
        verify=verify,
    )
    response = client.get_knowledge_article_attachment(
        article_sys_id=article_sys_id, attachment_sys_id=attachment_sys_id
    )
    return response.result


@mcp.tool(
    exclude_args=[
        "servicenow_instance",
        "username",
        "password",
        "client_id",
        "client_secret",
        "verify",
    ],
    tags={"knowledge_management"},
)
def get_featured_knowledge_article(
    servicenow_instance: str = Field(
        default=os.environ.get("SERVICENOW_INSTANCE", None),
        description="The URL of the ServiceNow instance (e.g., https://yourinstance.servicenow.com)",
    ),
    sysparm_fields: Optional[str] = Field(
        default=None,
        description="Comma-separated list of field names to include in the response",
    ),
    sysparm_limit: Optional[int] = Field(
        default=10, description="Maximum number of records to return"
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
    username: str = Field(
        default=os.environ.get("SERVICENOW_USERNAME", None),
        description="Username for basic authentication",
    ),
    password: str = Field(
        default=os.environ.get("SERVICENOW_PASSWORD", None),
        description="Password for basic authentication",
    ),
    client_id: Optional[str] = Field(
        default=os.environ.get("SERVICENOW_CLIENT_ID", None),
        description="Client ID for OAuth authentication",
    ),
    client_secret: Optional[str] = Field(
        default=os.environ.get("SERVICENOW_CLIENT_SECRET", None),
        description="Client secret for OAuth authentication",
    ),
    verify: Optional[bool] = Field(
        default=to_boolean(os.environ.get("SERVICENOW_VERIFY", "True")),
        description="Whether to verify SSL certificates",
    ),
) -> dict:
    """
    Get featured Knowledge Base articles from a ServiceNow instance.
    """
    client = Api(
        url=servicenow_instance,
        username=username,
        password=password,
        client_id=client_id,
        client_secret=client_secret,
        verify=verify,
    )
    response = client.get_featured_knowledge_article(
        sysparm_fields=sysparm_fields,
        sysparm_limit=sysparm_limit,
        sysparm_offset=sysparm_offset,
        kb=kb,
        language=language,
    )
    return response.result


@mcp.tool(
    exclude_args=[
        "servicenow_instance",
        "username",
        "password",
        "client_id",
        "client_secret",
        "verify",
    ],
    tags={"knowledge_management"},
)
def get_most_viewed_knowledge_articles(
    servicenow_instance: str = Field(
        default=os.environ.get("SERVICENOW_INSTANCE", None),
        description="The URL of the ServiceNow instance (e.g., https://yourinstance.servicenow.com)",
    ),
    sysparm_fields: Optional[str] = Field(
        default=None,
        description="Comma-separated list of field names to include in the response",
    ),
    sysparm_limit: Optional[int] = Field(
        default=10, description="Maximum number of records to return"
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
    username: str = Field(
        default=os.environ.get("SERVICENOW_USERNAME", None),
        description="Username for basic authentication",
    ),
    password: str = Field(
        default=os.environ.get("SERVICENOW_PASSWORD", None),
        description="Password for basic authentication",
    ),
    client_id: Optional[str] = Field(
        default=os.environ.get("SERVICENOW_CLIENT_ID", None),
        description="Client ID for OAuth authentication",
    ),
    client_secret: Optional[str] = Field(
        default=os.environ.get("SERVICENOW_CLIENT_SECRET", None),
        description="Client secret for OAuth authentication",
    ),
    verify: Optional[bool] = Field(
        default=to_boolean(os.environ.get("SERVICENOW_VERIFY", "True")),
        description="Whether to verify SSL certificates",
    ),
) -> dict:
    """
    Get most viewed Knowledge Base articles from a ServiceNow instance.
    """
    client = Api(
        url=servicenow_instance,
        username=username,
        password=password,
        client_id=client_id,
        client_secret=client_secret,
        verify=verify,
    )
    response = client.get_most_viewed_knowledge_articles(
        sysparm_fields=sysparm_fields,
        sysparm_limit=sysparm_limit,
        sysparm_offset=sysparm_offset,
        kb=kb,
        language=language,
    )
    return response.result


# Table API Tools
@mcp.tool(
    exclude_args=[
        "servicenow_instance",
        "username",
        "password",
        "client_id",
        "client_secret",
        "verify",
    ],
    tags={"table_api"},
)
def delete_table_record(
    table: str = Field(description="The name of the table"),
    table_record_sys_id: str = Field(
        description="The sys_id of the record to be deleted"
    ),
    servicenow_instance: str = Field(
        default=os.environ.get("SERVICENOW_INSTANCE", None),
        description="The URL of the ServiceNow instance (e.g., https://yourinstance.servicenow.com)",
    ),
    username: str = Field(
        default=os.environ.get("SERVICENOW_USERNAME", None),
        description="Username for basic authentication",
    ),
    password: str = Field(
        default=os.environ.get("SERVICENOW_PASSWORD", None),
        description="Password for basic authentication",
    ),
    client_id: Optional[str] = Field(
        default=os.environ.get("SERVICENOW_CLIENT_ID", None),
        description="Client ID for OAuth authentication",
    ),
    client_secret: Optional[str] = Field(
        default=os.environ.get("SERVICENOW_CLIENT_SECRET", None),
        description="Client secret for OAuth authentication",
    ),
    verify: Optional[bool] = Field(
        default=to_boolean(os.environ.get("SERVICENOW_VERIFY", "True")),
        description="Whether to verify SSL certificates",
    ),
) -> dict:
    """
    Delete a record from the specified table on a ServiceNow instance.
    """
    client = Api(
        url=servicenow_instance,
        username=username,
        password=password,
        client_id=client_id,
        client_secret=client_secret,
        verify=verify,
    )
    response = client.delete_table_record(
        table=table, table_record_sys_id=table_record_sys_id
    )
    return response.result


@mcp.tool(
    exclude_args=[
        "servicenow_instance",
        "username",
        "password",
        "client_id",
        "client_secret",
        "verify",
    ],
    tags={"table_api"},
)
def get_table(
    table: str = Field(description="The name of the table"),
    servicenow_instance: str = Field(
        default=os.environ.get("SERVICENOW_INSTANCE", None),
        description="The URL of the ServiceNow instance (e.g., https://yourinstance.servicenow.com)",
    ),
    name_value_pairs: Optional[Dict[str, str]] = Field(
        default=None, description="Dictionary of name-value pairs for filtering records"
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
        default=10, description="Maximum number of records to return"
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
    username: str = Field(
        default=os.environ.get("SERVICENOW_USERNAME", None),
        description="Username for basic authentication",
    ),
    password: str = Field(
        default=os.environ.get("SERVICENOW_PASSWORD", None),
        description="Password for basic authentication",
    ),
    client_id: Optional[str] = Field(
        default=os.environ.get("SERVICENOW_CLIENT_ID", None),
        description="Client ID for OAuth authentication",
    ),
    client_secret: Optional[str] = Field(
        default=os.environ.get("SERVICENOW_CLIENT_SECRET", None),
        description="Client secret for OAuth authentication",
    ),
    verify: Optional[bool] = Field(
        default=to_boolean(os.environ.get("SERVICENOW_VERIFY", "True")),
        description="Whether to verify SSL certificates",
    ),
) -> dict:
    """
    Get records from the specified table on a ServiceNow instance.
    """
    client = Api(
        url=servicenow_instance,
        username=username,
        password=password,
        client_id=client_id,
        client_secret=client_secret,
        verify=verify,
    )
    response = client.get_table(
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
    return response.result


@mcp.tool(
    exclude_args=[
        "servicenow_instance",
        "username",
        "password",
        "client_id",
        "client_secret",
        "verify",
    ],
    tags={"table_api"},
)
def get_table_record(
    table: str = Field(description="The name of the table"),
    table_record_sys_id: str = Field(
        description="The sys_id of the record to be retrieved"
    ),
    servicenow_instance: str = Field(
        default=os.environ.get("SERVICENOW_INSTANCE", None),
        description="The URL of the ServiceNow instance (e.g., https://yourinstance.servicenow.com)",
    ),
    username: str = Field(
        default=os.environ.get("SERVICENOW_USERNAME", None),
        description="Username for basic authentication",
    ),
    password: str = Field(
        default=os.environ.get("SERVICENOW_PASSWORD", None),
        description="Password for basic authentication",
    ),
    client_id: Optional[str] = Field(
        default=os.environ.get("SERVICENOW_CLIENT_ID", None),
        description="Client ID for OAuth authentication",
    ),
    client_secret: Optional[str] = Field(
        default=os.environ.get("SERVICENOW_CLIENT_SECRET", None),
        description="Client secret for OAuth authentication",
    ),
    verify: Optional[bool] = Field(
        default=to_boolean(os.environ.get("SERVICENOW_VERIFY", "True")),
        description="Whether to verify SSL certificates",
    ),
) -> dict:
    """
    Get a specific record from the specified table on a ServiceNow instance.
    """
    client = Api(
        url=servicenow_instance,
        username=username,
        password=password,
        client_id=client_id,
        client_secret=client_secret,
        verify=verify,
    )
    response = client.get_table_record(
        table=table, table_record_sys_id=table_record_sys_id
    )
    return response.result


@mcp.tool(
    exclude_args=[
        "servicenow_instance",
        "username",
        "password",
        "client_id",
        "client_secret",
        "verify",
    ],
    tags={"table_api"},
)
def patch_table_record(
    table: str = Field(description="The name of the table"),
    table_record_sys_id: str = Field(
        description="The sys_id of the record to be updated"
    ),
    data: Dict[str, Any] = Field(
        description="Dictionary containing the fields to be updated"
    ),
    servicenow_instance: str = Field(
        default=os.environ.get("SERVICENOW_INSTANCE", None),
        description="The URL of the ServiceNow instance (e.g., https://yourinstance.servicenow.com)",
    ),
    username: str = Field(
        default=os.environ.get("SERVICENOW_USERNAME", None),
        description="Username for basic authentication",
    ),
    password: str = Field(
        default=os.environ.get("SERVICENOW_PASSWORD", None),
        description="Password for basic authentication",
    ),
    client_id: Optional[str] = Field(
        default=os.environ.get("SERVICENOW_CLIENT_ID", None),
        description="Client ID for OAuth authentication",
    ),
    client_secret: Optional[str] = Field(
        default=os.environ.get("SERVICENOW_CLIENT_SECRET", None),
        description="Client secret for OAuth authentication",
    ),
    verify: Optional[bool] = Field(
        default=to_boolean(os.environ.get("SERVICENOW_VERIFY", "True")),
        description="Whether to verify SSL certificates",
    ),
) -> dict:
    """
    Partially update a record in the specified table on a ServiceNow instance.
    """
    client = Api(
        url=servicenow_instance,
        username=username,
        password=password,
        client_id=client_id,
        client_secret=client_secret,
        verify=verify,
    )
    response = client.patch_table_record(
        table=table, table_record_sys_id=table_record_sys_id, data=data
    )
    return response.result


@mcp.tool(
    exclude_args=[
        "servicenow_instance",
        "username",
        "password",
        "client_id",
        "client_secret",
        "verify",
    ],
    tags={"table_api"},
)
def update_table_record(
    table: str = Field(description="The name of the table"),
    table_record_sys_id: str = Field(
        description="The sys_id of the record to be updated"
    ),
    data: Dict[str, Any] = Field(
        description="Dictionary containing the fields to be updated"
    ),
    servicenow_instance: str = Field(
        default=os.environ.get("SERVICENOW_INSTANCE", None),
        description="The URL of the ServiceNow instance (e.g., https://yourinstance.servicenow.com)",
    ),
    username: str = Field(
        default=os.environ.get("SERVICENOW_USERNAME", None),
        description="Username for basic authentication",
    ),
    password: str = Field(
        default=os.environ.get("SERVICENOW_PASSWORD", None),
        description="Password for basic authentication",
    ),
    client_id: Optional[str] = Field(
        default=os.environ.get("SERVICENOW_CLIENT_ID", None),
        description="Client ID for OAuth authentication",
    ),
    client_secret: Optional[str] = Field(
        default=os.environ.get("SERVICENOW_CLIENT_SECRET", None),
        description="Client secret for OAuth authentication",
    ),
    verify: Optional[bool] = Field(
        default=to_boolean(os.environ.get("SERVICENOW_VERIFY", "True")),
        description="Whether to verify SSL certificates",
    ),
) -> dict:
    """
    Fully update a record in the specified table on a ServiceNow instance.
    """
    client = Api(
        url=servicenow_instance,
        username=username,
        password=password,
        client_id=client_id,
        client_secret=client_secret,
        verify=verify,
    )
    response = client.update_table_record(
        table=table, table_record_sys_id=table_record_sys_id, data=data
    )
    return response.result


@mcp.tool(
    exclude_args=[
        "servicenow_instance",
        "username",
        "password",
        "client_id",
        "client_secret",
        "verify",
    ],
    tags={"table_api"},
)
def add_table_record(
    table: str = Field(description="The name of the table"),
    data: Dict[str, Any] = Field(
        description="Dictionary containing the field values for the new record"
    ),
    servicenow_instance: str = Field(
        default=os.environ.get("SERVICENOW_INSTANCE", None),
        description="The URL of the ServiceNow instance (e.g., https://yourinstance.servicenow.com)",
    ),
    username: str = Field(
        default=os.environ.get("SERVICENOW_USERNAME", None),
        description="Username for basic authentication",
    ),
    password: str = Field(
        default=os.environ.get("SERVICENOW_PASSWORD", None),
        description="Password for basic authentication",
    ),
    client_id: Optional[str] = Field(
        default=os.environ.get("SERVICENOW_CLIENT_ID", None),
        description="Client ID for OAuth authentication",
    ),
    client_secret: Optional[str] = Field(
        default=os.environ.get("SERVICENOW_CLIENT_SECRET", None),
        description="Client secret for OAuth authentication",
    ),
    verify: Optional[bool] = Field(
        default=to_boolean(os.environ.get("SERVICENOW_VERIFY", "True")),
        description="Whether to verify SSL certificates",
    ),
) -> dict:
    """
    Add a new record to the specified table on a ServiceNow instance.
    """
    client = Api(
        url=servicenow_instance,
        username=username,
        password=password,
        client_id=client_id,
        client_secret=client_secret,
        verify=verify,
    )
    response = client.add_table_record(table=table, data=data)
    return response.result


@mcp.tool(
    exclude_args=[
        "servicenow_instance",
        "username",
        "password",
        "client_id",
        "client_secret",
        "verify",
    ],
    tags={"auth"},
)
def refresh_auth_token(
    servicenow_instance: str = Field(
        default=os.environ.get("SERVICENOW_INSTANCE", None),
        description="The URL of the ServiceNow instance (e.g., https://yourinstance.servicenow.com)",
    ),
    username: str = Field(
        default=os.environ.get("SERVICENOW_USERNAME", None),
        description="Username for basic authentication",
    ),
    password: str = Field(
        default=os.environ.get("SERVICENOW_PASSWORD", None),
        description="Password for basic authentication",
    ),
    client_id: Optional[str] = Field(
        default=os.environ.get("SERVICENOW_CLIENT_ID", None),
        description="Client ID for OAuth authentication",
    ),
    client_secret: Optional[str] = Field(
        default=os.environ.get("SERVICENOW_CLIENT_SECRET", None),
        description="Client secret for OAuth authentication",
    ),
    verify: Optional[bool] = Field(
        default=to_boolean(os.environ.get("SERVICENOW_VERIFY", "True")),
        description="Whether to verify SSL certificates",
    ),
) -> dict:
    """
    Refreshes the authentication token for the ServiceNow client.
    """
    client = Api(
        url=servicenow_instance,
        username=username,
        password=password,
        client_id=client_id,
        client_secret=client_secret,
        verify=verify,
    )
    response = client.refresh_auth_token()
    return {"access_token": response.access_token}


# Custom API Tools
@mcp.tool(
    exclude_args=[
        "servicenow_instance",
        "username",
        "password",
        "client_id",
        "client_secret",
        "verify",
    ],
    tags={"custom_api"},
)
def api_request(
    method: str = Field(
        description="The HTTP method to use ('GET', 'POST', 'PUT', 'DELETE')"
    ),
    endpoint: str = Field(description="The API endpoint to send the request to"),
    servicenow_instance: str = Field(
        default=os.environ.get("SERVICENOW_INSTANCE", None),
        description="The URL of the ServiceNow instance (e.g., https://yourinstance.servicenow.com)",
    ),
    data: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Data to include in the request body (for non-JSON payloads)",
    ),
    json: Optional[Dict[str, Any]] = Field(
        default=None, description="JSON data to include in the request body"
    ),
    username: str = Field(
        default=os.environ.get("SERVICENOW_USERNAME", None),
        description="Username for basic authentication",
    ),
    password: str = Field(
        default=os.environ.get("SERVICENOW_PASSWORD", None),
        description="Password for basic authentication",
    ),
    client_id: Optional[str] = Field(
        default=os.environ.get("SERVICENOW_CLIENT_ID", None),
        description="Client ID for OAuth authentication",
    ),
    client_secret: Optional[str] = Field(
        default=os.environ.get("SERVICENOW_CLIENT_SECRET", None),
        description="Client secret for OAuth authentication",
    ),
    verify: Optional[bool] = Field(
        default=to_boolean(os.environ.get("SERVICENOW_VERIFY", "True")),
        description="Whether to verify SSL certificates",
    ),
) -> dict:
    """
    Make a custom API request to a ServiceNow instance.
    """
    client = Api(
        url=servicenow_instance,
        username=username,
        password=password,
        client_id=client_id,
        client_secret=client_secret,
        verify=verify,
    )
    response = client.api_request(
        method=method, endpoint=endpoint, data=data, json=json
    )
    return response.result


# Resources
@mcp.resource("data://instance_config")
def get_instance_config() -> dict:
    """
    Provides the current ServiceNow instance configuration.
    """
    return {
        "instance": os.environ.get("SERVICENOW_INSTANCE"),
        "verify": to_boolean(os.environ.get("SERVICENOW_VERIFY", "True")),
    }


@mcp.resource("data://incident_categories")
def get_incident_categories(
    servicenow_instance: str = os.environ.get("SERVICENOW_INSTANCE", None),
    username: str = os.environ.get("SERVICENOW_USERNAME", None),
    password: str = os.environ.get("SERVICENOW_PASSWORD", None),
    client_id: str = os.environ.get("SERVICENOW_CLIENT_ID", None),
    client_secret: str = os.environ.get("SERVICENOW_CLIENT_SECRET", None),
    verify: bool = to_boolean(os.environ.get("SERVICENOW_VERIFY", "True")),
) -> List[str]:
    """
    Retrieves unique incident categories from ServiceNow.
    """
    client = Api(
        url=servicenow_instance,
        username=username,
        password=password,
        client_id=client_id,
        client_secret=client_secret,
        verify=verify,
    )
    response = client.get_table(
        table="incident", sysparm_fields="category", sysparm_limit=1000
    )
    categories = set(r.get("category") for r in response.result if r.get("category"))
    return list(categories)


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
    return f"Create a new ServiceNow incident with short description: '{short_description}', full description: '{description}', and priority: {priority}. Use the add_table_record tool with table='incident'."


@mcp.prompt
def query_table_prompt(
    table: str,
    query: str,
) -> str:
    """
    Generates a prompt for querying a ServiceNow table.
    """
    return f"Query the ServiceNow table '{table}' with filter: '{query}'. Use the get_table tool with appropriate parameters."


def servicenow_api_mcp():
    parser = argparse.ArgumentParser(description="ServiceNow API MCP Runner")
    parser.add_argument(
        "-t",
        "--transport",
        default="stdio",
        choices=["stdio", "http", "sse"],
        help="Transport method: 'stdio', 'http', or 'sse' [legacy] (default: stdio)",
    )
    parser.add_argument(
        "-s",
        "--host",
        default="0.0.0.0",
        help="Host address for HTTP transport (default: 0.0.0.0)",
    )
    parser.add_argument(
        "-p",
        "--port",
        type=int,
        default=8000,
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

    args = parser.parse_args()

    if args.port < 0 or args.port > 65535:
        print(f"Error: Port {args.port} is out of valid range (0-65535).")
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
        # Internal static tokens (hardcoded example)
        auth = StaticTokenVerifier(
            tokens={
                "test-token": {"client_id": "test-user", "scopes": ["read", "write"]},
                "admin-token": {"client_id": "admin", "scopes": ["admin"]},
            }
        )
    elif args.auth_type == "jwt":
        if not (args.token_jwks_uri and args.token_issuer and args.token_audience):
            print(
                "Error: jwt requires --token-jwks-uri, --token-issuer, --token-audience"
            )
            sys.exit(1)
        auth = JWTVerifier(
            jwks_uri=args.token_jwks_uri,
            issuer=args.token_issuer,
            audience=args.token_audience,
        )
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
                "Error: oauth-proxy requires --oauth-upstream-auth-endpoint, --oauth-upstream-token-endpoint, --oauth-upstream-client-id, --oauth-upstream-client-secret, --oauth-base-url, --token-jwks-uri, --token-issuer, --token-audience"
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
            print(
                "Error: oidc-proxy requires --oidc-config-url, --oidc-client-id, --oidc-client-secret, --oidc-base-url"
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
            print(
                "Error: remote-oauth requires --remote-auth-servers, --remote-base-url, --token-jwks-uri, --token-issuer, --token-audience"
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
    mcp.auth = auth
    if args.eunomia_type != "none":
        from eunomia_mcp import create_eunomia_middleware

        if args.eunomia_type == "embedded":
            if not args.eunomia_policy_file:
                print("Error: embedded Eunomia requires --eunomia-policy-file")
                sys.exit(1)
            middleware = create_eunomia_middleware(policy_file=args.eunomia_policy_file)
            mcp.add_middleware(middleware)
        elif args.eunomia_type == "remote":
            if not args.eunomia_remote_url:
                print("Error: remote Eunomia requires --eunomia-remote-url")
                sys.exit(1)
            middleware = create_eunomia_middleware(
                use_remote_eunomia=args.eunomia_remote_url
            )  # Assuming param; adjust if different
            mcp.add_middleware(middleware)

    mcp.add_middleware(
        ErrorHandlingMiddleware(include_traceback=True, transform_errors=True)
    )
    mcp.add_middleware(
        RateLimitingMiddleware(max_requests_per_second=10.0, burst_capacity=20)
    )
    mcp.add_middleware(TimingMiddleware())
    mcp.add_middleware(LoggingMiddleware())

    if args.transport == "stdio":
        mcp.run(transport="stdio")
    elif args.transport == "http":
        mcp.run(transport="http", host=args.host, port=args.port)
    elif args.transport == "sse":
        mcp.run(transport="sse", host=args.host, port=args.port)
    else:
        logger = logging.getLogger("ServiceNow")
        logger.error("Transport not supported")
        sys.exit(1)


if __name__ == "__main__":
    servicenow_api_mcp()
