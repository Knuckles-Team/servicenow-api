#!/usr/bin/python
# coding: utf-8

import os
import getopt
import sys
import logging
from typing import Optional, List, Dict, Any
from servicenow_api import Api

from fastmcp import FastMCP

mcp = FastMCP("ServiceNow")


def to_boolean(string):
    # Normalize the string: strip whitespace and convert to lowercase
    normalized = str(string).strip().lower()

    # Define valid true/false values
    true_values = {"t", "true", "y", "yes", "1"}
    false_values = {"f", "false", "n", "no", "0"}

    if normalized in true_values:
        return True
    elif normalized in false_values:
        return False
    else:
        raise ValueError(f"Cannot convert '{string}' to boolean")


environment_servicenow_instance = os.environ.get("SERVICENOW_INSTANCE", None)
environment_username = os.environ.get("USERNAME", None)
environment_password = os.environ.get("PASSWORD", None)
environment_client_id = os.environ.get("CLIENT_ID", None)
environment_client_secret = os.environ.get("CLIENT_SECRET", None)
environment_verify = os.environ.get("VERIFY", True)

if environment_verify:
    environment_verify = to_boolean(environment_verify)


# Application Service Tools
@mcp.tool()
def get_application(
    application_id: str = None,
    servicenow_instance: str = environment_servicenow_instance,
    username: str = environment_username,
    password: str = environment_password,
    client_id: Optional[str] = environment_client_id,
    client_secret: Optional[str] = environment_client_secret,
    verify: Optional[bool] = environment_verify,
) -> dict:
    """
    Get information about a ServiceNow application.

    This tool retrieves details about a specific application from a ServiceNow instance.
    Authentication can be provided via basic auth (username and password) or OAuth (client_id and client_secret).
    At least one authentication method must be configured in the Api client, but validation is handled by the underlying Api.

    Args:
        application_id (str): The unique identifier of the application to retrieve.
        servicenow_instance (str): The URL of the ServiceNow instance (e.g., https://yourinstance.servicenow.com).
            Will read SERVICENOW_INSTANCE environment variable if none is provided in the function.
        username (Optional[str], optional): Username for basic authentication. Defaults to None.
            Will read USERNAME environment variable if none is provided in the function.
        password (Optional[str], optional): Password for basic authentication. Defaults to None.
            Will read PASSWORD environment variable if none is provided in the function.
        client_id (Optional[str], optional): Client ID for OAuth authentication. Defaults to None.
            Will read CLIENT_ID environment variable if none is provided in the function.
        client_secret (Optional[str], optional): Client secret for OAuth authentication. Defaults to None.
            Will read CLIENT_SECRET environment variable if none is provided in the function.
        verify (Optional[bool], optional): Whether to verify SSL certificates. Defaults to False.
            Will read VERIFY environment variable if none is provided in the function.

    Returns:
        dict: The JSON response containing information about the application.

    Raises:
        MissingParameterError: If required parameters like application_id are not provided (handled by the Api).
        ValidationError: If invalid parameters are passed to the Api.
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
@mcp.tool()
def get_cmdb(
    cmdb_id: str,
    servicenow_instance: str = environment_servicenow_instance,
    username: str = environment_username,
    password: str = environment_password,
    client_id: Optional[str] = environment_client_id,
    client_secret: Optional[str] = environment_client_secret,
    verify: Optional[bool] = environment_verify,
) -> dict:
    """
    Get Configuration Management Database (CMDB) information from a ServiceNow instance.

    This tool retrieves details about a specific CMDB record from a ServiceNow instance.
    Authentication can be provided via basic auth (username and password) or OAuth (client_id and client_secret).
    At least one authentication method must be configured in the Api client, but validation is handled by the underlying Api.

    Args:
        cmdb_id (str): The unique identifier of the CMDB record to retrieve.
        servicenow_instance (str): The URL of the ServiceNow instance (e.g., https://yourinstance.servicenow.com).
            Will read SERVICENOW_INSTANCE environment variable if none is provided in the function.
        username (Optional[str], optional): Username for basic authentication. Defaults to None.
            Will read USERNAME environment variable if none is provided in the function.
        password (Optional[str], optional): Password for basic authentication. Defaults to None.
            Will read PASSWORD environment variable if none is provided in the function.
        client_id (Optional[str], optional): Client ID for OAuth authentication. Defaults to None.
            Will read CLIENT_ID environment variable if none is provided in the function.
        client_secret (Optional[str], optional): Client secret for OAuth authentication. Defaults to None.
            Will read CLIENT_SECRET environment variable if none is provided in the function.
        verify (Optional[bool], optional): Whether to verify SSL certificates. Defaults to False.
            Will read VERIFY environment variable if none is provided in the function.

    Returns:
        dict: The JSON response containing information about the CMDB record.

    Raises:
        ParameterError: If required parameters like cmdb_id are not provided or invalid (handled by the Api).
        ValidationError: If invalid parameters are passed to the Api.
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
@mcp.tool()
def batch_install_result(
    result_id: str,
    servicenow_instance: str = environment_servicenow_instance,
    username: str = environment_username,
    password: str = environment_password,
    client_id: Optional[str] = environment_client_id,
    client_secret: Optional[str] = environment_client_secret,
    verify: Optional[bool] = environment_verify,
) -> dict:
    """
    Get the result of a batch installation from a ServiceNow instance.

    This tool retrieves details about a batch installation result using the provided result ID.
    Authentication can be provided via basic auth (username and password) or OAuth (client_id and client_secret).
    At least one authentication method must be configured in the Api client, but validation is handled by the underlying Api.

    Args:
        result_id (str): The ID associated with the batch installation result.
        servicenow_instance (str): The URL of the ServiceNow instance (e.g., https://yourinstance.servicenow.com).
            Will read SERVICENOW_INSTANCE environment variable if none is provided in the function.
        username (Optional[str], optional): Username for basic authentication. Defaults to None.
            Will read USERNAME environment variable if none is provided in the function.
        password (Optional[str], optional): Password for basic authentication. Defaults to None.
            Will read PASSWORD environment variable if none is provided in the function.
        client_id (Optional[str], optional): Client ID for OAuth authentication. Defaults to None.
            Will read CLIENT_ID environment variable if none is provided in the function.
        client_secret (Optional[str], optional): Client secret for OAuth authentication. Defaults to None.
            Will read CLIENT_SECRET environment variable if none is provided in the function.
        verify (Optional[bool], optional): Whether to verify SSL certificates. Defaults to False.
            Will read VERIFY environment variable if none is provided in the function.

    Returns:
        dict: The JSON response containing batch installation result.

    Raises:
        MissingParameterError: If result_id is not provided (handled by the Api).
        ValidationError: If invalid parameters are passed to the Api.
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


@mcp.tool()
def instance_scan_progress(
    progress_id: str,
    servicenow_instance: str = environment_servicenow_instance,
    username: str = environment_username,
    password: str = environment_password,
    client_id: Optional[str] = environment_client_id,
    client_secret: Optional[str] = environment_client_secret,
    verify: Optional[bool] = environment_verify,
) -> dict:
    """
    Get progress information for an instance scan from a ServiceNow instance.

    This tool retrieves details about the progress of an instance scan using the provided progress ID.
    Authentication can be provided via basic auth (username and password) or OAuth (client_id and client_secret).
    At least one authentication method must be configured in the Api client, but validation is handled by the underlying Api.

    Args:
        progress_id (str): The ID associated with the instance scan progress.
        servicenow_instance (str): The URL of the ServiceNow instance (e.g., https://yourinstance.servicenow.com).
            Will read SERVICENOW_INSTANCE environment variable if none is provided in the function.
        username (Optional[str], optional): Username for basic authentication. Defaults to None.
            Will read USERNAME environment variable if none is provided in the function.
        password (Optional[str], optional): Password for basic authentication. Defaults to None.
            Will read PASSWORD environment variable if none is provided in the function.
        client_id (Optional[str], optional): Client ID for OAuth authentication. Defaults to None.
            Will read CLIENT_ID environment variable if none is provided in the function.
        client_secret (Optional[str], optional): Client secret for OAuth authentication. Defaults to None.
            Will read CLIENT_SECRET environment variable if none is provided in the function.
        verify (Optional[bool], optional): Whether to verify SSL certificates. Defaults to False.
            Will read VERIFY environment variable if none is provided in the function.

    Returns:
        dict: The JSON response containing instance scan progress.

    Raises:
        MissingParameterError: If progress_id is not provided (handled by the Api).
        ValidationError: If invalid parameters are passed to the Api.
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


@mcp.tool()
def progress(
    progress_id: str,
    servicenow_instance: str = environment_servicenow_instance,
    username: str = environment_username,
    password: str = environment_password,
    client_id: Optional[str] = environment_client_id,
    client_secret: Optional[str] = environment_client_secret,
    verify: Optional[bool] = environment_verify,
) -> dict:
    """
    Get progress information from a ServiceNow instance.

    This tool retrieves progress details using the provided progress ID.
    Authentication can be provided via basic auth (username and password) or OAuth (client_id and client_secret).
    At least one authentication method must be configured in the Api client, but validation is handled by the underlying Api.

    Args:
        progress_id (str): The ID associated with the progress.
        servicenow_instance (str): The URL of the ServiceNow instance (e.g., https://yourinstance.servicenow.com).
            Will read SERVICENOW_INSTANCE environment variable if none is provided in the function.
        username (Optional[str], optional): Username for basic authentication. Defaults to None.
            Will read USERNAME environment variable if none is provided in the function.
        password (Optional[str], optional): Password for basic authentication. Defaults to None.
            Will read PASSWORD environment variable if none is provided in the function.
        client_id (Optional[str], optional): Client ID for OAuth authentication. Defaults to None.
            Will read CLIENT_ID environment variable if none is provided in the function.
        client_secret (Optional[str], optional): Client secret for OAuth authentication. Defaults to None.
            Will read CLIENT_SECRET environment variable if none is provided in the function.
        verify (Optional[bool], optional): Whether to verify SSL certificates. Defaults to False.
            Will read VERIFY environment variable if none is provided in the function.

    Returns:
        dict: The JSON response containing progress information.

    Raises:
        MissingParameterError: If progress_id is not provided (handled by the Api).
        ValidationError: If invalid parameters are passed to the Api.
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


@mcp.tool()
def batch_install(
    name: str,
    packages: str,
    servicenow_instance: str = environment_servicenow_instance,
    notes: Optional[str] = None,
    username: str = environment_username,
    password: str = environment_password,
    client_id: Optional[str] = environment_client_id,
    client_secret: Optional[str] = environment_client_secret,
    verify: Optional[bool] = environment_verify,
) -> dict:
    """
    Initiate a batch installation on a ServiceNow instance.

    This tool starts a batch installation with the provided parameters.
    Authentication can be provided via basic auth (username and password) or OAuth (client_id and client_secret).
    At least one authentication method must be configured in the Api client, but validation is handled by the underlying Api.

    Args:
        name (str): The name of the batch installation.
        packages (str): The packages to be installed in the batch.\
        notes (Optional[str], optional): Additional notes for the batch installation. Defaults to None.
        servicenow_instance (str): The URL of the ServiceNow instance (e.g., https://yourinstance.servicenow.com).
            Will read SERVICENOW_INSTANCE environment variable if none is provided in the function.
        username (Optional[str], optional): Username for basic authentication. Defaults to None.
            Will read USERNAME environment variable if none is provided in the function.
        password (Optional[str], optional): Password for basic authentication. Defaults to None.
            Will read PASSWORD environment variable if none is provided in the function.
        client_id (Optional[str], optional): Client ID for OAuth authentication. Defaults to None.
            Will read CLIENT_ID environment variable if none is provided in the function.
        client_secret (Optional[str], optional): Client secret for OAuth authentication. Defaults to None.
            Will read CLIENT_SECRET environment variable if none is provided in the function.
        verify (Optional[bool], optional): Whether to verify SSL certificates. Defaults to False.
            Will read VERIFY environment variable if none is provided in the function.

    Returns:
        dict: The JSON response containing information about the batch installation.

    Raises:
        MissingParameterError: If name or packages are not provided (handled by the Api).
        ParameterError: If notes is not a string (handled by the Api).
        ValidationError: If invalid parameters are passed to the Api.
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


@mcp.tool()
def batch_rollback(
    rollback_id: str,
    servicenow_instance: str = environment_servicenow_instance,
    username: str = environment_username,
    password: str = environment_password,
    client_id: Optional[str] = environment_client_id,
    client_secret: Optional[str] = environment_client_secret,
    verify: Optional[bool] = environment_verify,
) -> dict:
    """
    Rollback a batch installation on a ServiceNow instance.

    This tool initiates a rollback of a batch installation using the provided rollback ID.
    Authentication can be provided via basic auth (username and password) or OAuth (client_id and client_secret).
    At least one authentication method must be configured in the Api client, but validation is handled by the underlying Api.

    Args:
        rollback_id (str): The ID associated with the batch rollback.
        servicenow_instance (str): The URL of the ServiceNow instance (e.g., https://yourinstance.servicenow.com).
            Will read SERVICENOW_INSTANCE environment variable if none is provided in the function.
        username (Optional[str], optional): Username for basic authentication. Defaults to None.
            Will read USERNAME environment variable if none is provided in the function.
        password (Optional[str], optional): Password for basic authentication. Defaults to None.
            Will read PASSWORD environment variable if none is provided in the function.
        client_id (Optional[str], optional): Client ID for OAuth authentication. Defaults to None.
            Will read CLIENT_ID environment variable if none is provided in the function.
        client_secret (Optional[str], optional): Client secret for OAuth authentication. Defaults to None.
            Will read CLIENT_SECRET environment variable if none is provided in the function.
        verify (Optional[bool], optional): Whether to verify SSL certificates. Defaults to False.
            Will read VERIFY environment variable if none is provided in the function.

    Returns:
        dict: The JSON response containing information about the batch rollback.

    Raises:
        MissingParameterError: If rollback_id is not provided (handled by the Api).
        ValidationError: If invalid parameters are passed to the Api.
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


@mcp.tool()
def app_repo_install(
    app_sys_id: str,
    scope: str,
    servicenow_instance: str = environment_servicenow_instance,
    auto_upgrade_base_app: Optional[bool] = None,
    base_app_version: Optional[str] = None,
    version: Optional[str] = None,
    username: str = environment_username,
    password: str = environment_password,
    client_id: Optional[str] = environment_client_id,
    client_secret: Optional[str] = environment_client_secret,
    verify: Optional[bool] = environment_verify,
) -> dict:
    """
    Install an application from the repository on a ServiceNow instance.

    This tool initiates the installation of an application from the repository using the provided parameters.
    Authentication can be provided via basic auth (username and password) or OAuth (client_id and client_secret).
    At least one authentication method must be configured in the Api client, but validation is handled by the underlying Api.

    Args:
        app_sys_id (str): The sys_id of the application to be installed.
        scope (str): The scope of the application.
        auto_upgrade_base_app (Optional[bool], optional): Flag indicating whether to auto-upgrade the base app. Defaults to None.
        base_app_version (Optional[str], optional): The version of the base app. Defaults to None.
        version (Optional[str], optional): The version of the application to be installed. Defaults to None.
        servicenow_instance (str): The URL of the ServiceNow instance (e.g., https://yourinstance.servicenow.com).
            Will read SERVICENOW_INSTANCE environment variable if none is provided in the function.
        username (Optional[str], optional): Username for basic authentication. Defaults to None.
            Will read USERNAME environment variable if none is provided in the function.
        password (Optional[str], optional): Password for basic authentication. Defaults to None.
            Will read PASSWORD environment variable if none is provided in the function.
        client_id (Optional[str], optional): Client ID for OAuth authentication. Defaults to None.
            Will read CLIENT_ID environment variable if none is provided in the function.
        client_secret (Optional[str], optional): Client secret for OAuth authentication. Defaults to None.
            Will read CLIENT_SECRET environment variable if none is provided in the function.
        verify (Optional[bool], optional): Whether to verify SSL certificates. Defaults to False.
            Will read VERIFY environment variable if none is provided in the function.

    Returns:
        dict: The JSON response containing information about the installation.

    Raises:
        MissingParameterError: If app_sys_id or scope is not provided (handled by the Api).
        ParameterError: If auto_upgrade_base_app is not a boolean (handled by the Api).
        ValidationError: If invalid parameters are passed to the Api.
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


@mcp.tool()
def app_repo_publish(
    app_sys_id: str,
    scope: str,
    servicenow_instance: str = environment_servicenow_instance,
    dev_notes: Optional[str] = None,
    version: Optional[str] = None,
    username: str = environment_username,
    password: str = environment_password,
    client_id: Optional[str] = environment_client_id,
    client_secret: Optional[str] = environment_client_secret,
    verify: Optional[bool] = environment_verify,
) -> dict:
    """
    Publish an application to the repository on a ServiceNow instance.

    This tool publishes an application to the repository using the provided parameters.
    Authentication can be provided via basic auth (username and password) or OAuth (client_id and client_secret).
    At least one authentication method must be configured in the Api client, but validation is handled by the underlying Api.

    Args:
        app_sys_id (str): The sys_id of the application to be published.
        scope (str): The scope of the application.
        dev_notes (Optional[str], optional): Development notes for the published version. Defaults to None.
        version (Optional[str], optional): The version of the application to be published. Defaults to None.
        servicenow_instance (str): The URL of the ServiceNow instance (e.g., https://yourinstance.servicenow.com).
            Will read SERVICENOW_INSTANCE environment variable if none is provided in the function.
        username (Optional[str], optional): Username for basic authentication. Defaults to None.
            Will read USERNAME environment variable if none is provided in the function.
        password (Optional[str], optional): Password for basic authentication. Defaults to None.
            Will read PASSWORD environment variable if none is provided in the function.
        client_id (Optional[str], optional): Client ID for OAuth authentication. Defaults to None.
            Will read CLIENT_ID environment variable if none is provided in the function.
        client_secret (Optional[str], optional): Client secret for OAuth authentication. Defaults to None.
            Will read CLIENT_SECRET environment variable if none is provided in the function.
        verify (Optional[bool], optional): Whether to verify SSL certificates. Defaults to False.
            Will read VERIFY environment variable if none is provided in the function.

    Returns:
        dict: The JSON response containing information about the publication.

    Raises:
        MissingParameterError: If app_sys_id or scope is not provided (handled by the Api).
        ValidationError: If invalid parameters are passed to the Api.
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


@mcp.tool()
def app_repo_rollback(
    app_sys_id: str,
    scope: str,
    version: str,
    servicenow_instance: str = environment_servicenow_instance,
    username: str = environment_username,
    password: str = environment_password,
    client_id: Optional[str] = environment_client_id,
    client_secret: Optional[str] = environment_client_secret,
    verify: Optional[bool] = environment_verify,
) -> dict:
    """
    Rollback an application in the repository on a ServiceNow instance.

    This tool initiates a rollback of an application in the repository using the provided parameters.
    Authentication can be provided via basic auth (username and password) or OAuth (client_id and client_secret).
    At least one authentication method must be configured in the Api client, but validation is handled by the underlying Api.

    Args:
        app_sys_id (str): The sys_id of the application to be rolled back.
        scope (str): The scope of the application.
        version (str): The version of the application to be rolled back.
        servicenow_instance (str): The URL of the ServiceNow instance (e.g., https://yourinstance.servicenow.com).
            Will read SERVICENOW_INSTANCE environment variable if none is provided in the function.
        username (Optional[str], optional): Username for basic authentication. Defaults to None.
            Will read USERNAME environment variable if none is provided in the function.
        password (Optional[str], optional): Password for basic authentication. Defaults to None.
            Will read PASSWORD environment variable if none is provided in the function.
        client_id (Optional[str], optional): Client ID for OAuth authentication. Defaults to None.
            Will read CLIENT_ID environment variable if none is provided in the function.
        client_secret (Optional[str], optional): Client secret for OAuth authentication. Defaults to None.
            Will read CLIENT_SECRET environment variable if none is provided in the function.
        verify (Optional[bool], optional): Whether to verify SSL certificates. Defaults to False.
            Will read VERIFY environment variable if none is provided in the function.

    Returns:
        dict: The JSON response containing information about the rollback.

    Raises:
        MissingParameterError: If app_sys_id, scope, or version is not provided (handled by the Api).
        ValidationError: If invalid parameters are passed to the Api.
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


@mcp.tool()
def full_scan(
    servicenow_instance: str = environment_servicenow_instance,
    username: str = environment_username,
    password: str = environment_password,
    client_id: Optional[str] = environment_client_id,
    client_secret: Optional[str] = environment_client_secret,
    verify: Optional[bool] = environment_verify,
) -> dict:
    """
    Initiate a full instance scan on a ServiceNow instance.

    This tool starts a full instance scan.
    Authentication can be provided via basic auth (username and password) or OAuth (client_id and client_secret).
    At least one authentication method must be configured in the Api client, but validation is handled by the underlying Api.

    Args:
        servicenow_instance (str): The URL of the ServiceNow instance (e.g., https://yourinstance.servicenow.com).
            Will read SERVICENOW_INSTANCE environment variable if none is provided in the function.
        username (Optional[str], optional): Username for basic authentication. Defaults to None.
            Will read USERNAME environment variable if none is provided in the function.
        password (Optional[str], optional): Password for basic authentication. Defaults to None.
            Will read PASSWORD environment variable if none is provided in the function.
        client_id (Optional[str], optional): Client ID for OAuth authentication. Defaults to None.
            Will read CLIENT_ID environment variable if none is provided in the function.
        client_secret (Optional[str], optional): Client secret for OAuth authentication. Defaults to None.
            Will read CLIENT_SECRET environment variable if none is provided in the function.
        verify (Optional[bool], optional): Whether to verify SSL certificates. Defaults to False.
            Will read VERIFY environment variable if none is provided in the function.

    Returns:
        dict: The JSON response containing information about the full scan.

    Raises:
        ValidationError: If invalid parameters are passed to the Api.
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


@mcp.tool()
def point_scan(
    target_sys_id: str,
    target_table: str,
    servicenow_instance: str = environment_servicenow_instance,
    username: str = environment_username,
    password: str = environment_password,
    client_id: Optional[str] = environment_client_id,
    client_secret: Optional[str] = environment_client_secret,
    verify: Optional[bool] = environment_verify,
) -> dict:
    """
    Initiate a point instance scan on a ServiceNow instance.

    This tool starts a point instance scan using the provided parameters.
    Authentication can be provided via basic auth (username and password) or OAuth (client_id and client_secret).
    At least one authentication method must be configured in the Api client, but validation is handled by the underlying Api.

    Args:
        target_sys_id (str): The sys_id of the target instance.
        target_table (str): The table of the target instance.
        servicenow_instance (str): The URL of the ServiceNow instance (e.g., https://yourinstance.servicenow.com).
            Will read SERVICENOW_INSTANCE environment variable if none is provided in the function.
        username (Optional[str], optional): Username for basic authentication. Defaults to None.
            Will read USERNAME environment variable if none is provided in the function.
        password (Optional[str], optional): Password for basic authentication. Defaults to None.
            Will read PASSWORD environment variable if none is provided in the function.
        client_id (Optional[str], optional): Client ID for OAuth authentication. Defaults to None.
            Will read CLIENT_ID environment variable if none is provided in the function.
        client_secret (Optional[str], optional): Client secret for OAuth authentication. Defaults to None.
            Will read CLIENT_SECRET environment variable if none is provided in the function.
        verify (Optional[bool], optional): Whether to verify SSL certificates. Defaults to False.
            Will read VERIFY environment variable if none is provided in the function.

    Returns:
        dict: The JSON response containing information about the point scan.

    Raises:
        MissingParameterError: If target_sys_id or target_table is not provided (handled by the Api).
        ValidationError: If invalid parameters are passed to the Api.
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


@mcp.tool()
def combo_suite_scan(
    combo_sys_id: str,
    servicenow_instance: str = environment_servicenow_instance,
    username: str = environment_username,
    password: str = environment_password,
    client_id: Optional[str] = environment_client_id,
    client_secret: Optional[str] = environment_client_secret,
    verify: Optional[bool] = environment_verify,
) -> dict:
    """
    Initiate a suite scan for a combo on a ServiceNow instance.

    This tool starts a suite scan for a combo using the provided combo_sys_id.
    Authentication can be provided via basic auth (username and password) or OAuth (client_id and client_secret).
    At least one authentication method must be configured in the Api client, but validation is handled by the underlying Api.

    Args:
        combo_sys_id (str): The sys_id of the combo to be scanned.
        servicenow_instance (str): The URL of the ServiceNow instance (e.g., https://yourinstance.servicenow.com).
            Will read SERVICENOW_INSTANCE environment variable if none is provided in the function.
        username (Optional[str], optional): Username for basic authentication. Defaults to None.
            Will read USERNAME environment variable if none is provided in the function.
        password (Optional[str], optional): Password for basic authentication. Defaults to None.
            Will read PASSWORD environment variable if none is provided in the function.
        client_id (Optional[str], optional): Client ID for OAuth authentication. Defaults to None.
            Will read CLIENT_ID environment variable if none is provided in the function.
        client_secret (Optional[str], optional): Client secret for OAuth authentication. Defaults to None.
            Will read CLIENT_SECRET environment variable if none is provided in the function.
        verify (Optional[bool], optional): Whether to verify SSL certificates. Defaults to False.
            Will read VERIFY environment variable if none is provided in the function.

    Returns:
        dict: The JSON response containing information about the combo suite scan.

    Raises:
        MissingParameterError: If combo_sys_id is not provided (handled by the Api).
        ValidationError: If invalid parameters are passed to the Api.
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


@mcp.tool()
def suite_scan(
    suite_sys_id: str,
    sys_ids: List[str],
    servicenow_instance: str = environment_servicenow_instance,
    scan_type: str = "scoped_apps",
    username: str = environment_username,
    password: str = environment_password,
    client_id: Optional[str] = environment_client_id,
    client_secret: Optional[str] = environment_client_secret,
    verify: Optional[bool] = environment_verify,
) -> dict:
    """
    Initiate a suite scan on a ServiceNow instance.

    This tool starts a suite scan using the provided suite_sys_id and sys_ids.
    Authentication can be provided via basic auth (username and password) or OAuth (client_id and client_secret).
    At least one authentication method must be configured in the Api client, but validation is handled by the underlying Api.

    Args:
        suite_sys_id (str): The sys_id of the suite to be scanned.
        sys_ids (List[str]): List of sys_ids representing app_scope_sys_ids for the suite scan.
        scan_type (str, optional): Type of scan to be performed. Defaults to "scoped_apps".
        servicenow_instance (str): The URL of the ServiceNow instance (e.g., https://yourinstance.servicenow.com).
            Will read SERVICENOW_INSTANCE environment variable if none is provided in the function.
        username (Optional[str], optional): Username for basic authentication. Defaults to None.
            Will read USERNAME environment variable if none is provided in the function.
        password (Optional[str], optional): Password for basic authentication. Defaults to None.
            Will read PASSWORD environment variable if none is provided in the function.
        client_id (Optional[str], optional): Client ID for OAuth authentication. Defaults to None.
            Will read CLIENT_ID environment variable if none is provided in the function.
        client_secret (Optional[str], optional): Client secret for OAuth authentication. Defaults to None.
            Will read CLIENT_SECRET environment variable if none is provided in the function.
        verify (Optional[bool], optional): Whether to verify SSL certificates. Defaults to False.
            Will read VERIFY environment variable if none is provided in the function.

    Returns:
        dict: The JSON response containing information about the suite scan.

    Raises:
        MissingParameterError: If suite_sys_id or sys_ids is not provided (handled by the Api).
        ParameterError: If JSON serialization fails (handled by the Api).
        ValidationError: If invalid parameters are passed to the Api.
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
@mcp.tool()
def activate_plugin(
    plugin_id: str,
    servicenow_instance: str = environment_servicenow_instance,
    username: str = environment_username,
    password: str = environment_password,
    client_id: Optional[str] = environment_client_id,
    client_secret: Optional[str] = environment_client_secret,
    verify: Optional[bool] = environment_verify,
) -> dict:
    """
    Activate a plugin on a ServiceNow instance.

    This tool activates a plugin using the provided plugin ID.
    Authentication can be provided via basic auth (username and password) or OAuth (client_id and client_secret).
    At least one authentication method must be configured in the Api client, but validation is handled by the underlying Api.

    Args:
        plugin_id (str): The ID of the plugin to be activated.
        servicenow_instance (str): The URL of the ServiceNow instance (e.g., https://yourinstance.servicenow.com).
            Will read SERVICENOW_INSTANCE environment variable if none is provided in the function.
        username (Optional[str], optional): Username for basic authentication. Defaults to None.
            Will read USERNAME environment variable if none is provided in the function.
        password (Optional[str], optional): Password for basic authentication. Defaults to None.
            Will read PASSWORD environment variable if none is provided in the function.
        client_id (Optional[str], optional): Client ID for OAuth authentication. Defaults to None.
            Will read CLIENT_ID environment variable if none is provided in the function.
        client_secret (Optional[str], optional): Client secret for OAuth authentication. Defaults to None.
            Will read CLIENT_SECRET environment variable if none is provided in the function.
        verify (Optional[bool], optional): Whether to verify SSL certificates. Defaults to False.
            Will read VERIFY environment variable if none is provided in the function.

    Returns:
        dict: The JSON response containing information about the activation.

    Raises:
        MissingParameterError: If plugin_id is not provided (handled by the Api).
        ValidationError: If invalid parameters are passed to the Api.
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


@mcp.tool()
def rollback_plugin(
    plugin_id: str,
    servicenow_instance: str = environment_servicenow_instance,
    username: str = environment_username,
    password: str = environment_password,
    client_id: Optional[str] = environment_client_id,
    client_secret: Optional[str] = environment_client_secret,
    verify: Optional[bool] = environment_verify,
) -> dict:
    """
    Rollback a plugin on a ServiceNow instance.

    This tool initiates a rollback of a plugin using the provided plugin ID.
    Authentication can be provided via basic auth (username and password) or OAuth (client_id and client_secret).
    At least one authentication method must be configured in the Api client, but validation is handled by the underlying Api.

    Args:
        plugin_id (str): The ID of the plugin to be rolled back.
        servicenow_instance (str): The URL of the ServiceNow instance (e.g., https://yourinstance.servicenow.com).
            Will read SERVICENOW_INSTANCE environment variable if none is provided in the function.
        username (Optional[str], optional): Username for basic authentication. Defaults to None.
            Will read USERNAME environment variable if none is provided in the function.
        password (Optional[str], optional): Password for basic authentication. Defaults to None.
            Will read PASSWORD environment variable if none is provided in the function.
        client_id (Optional[str], optional): Client ID for OAuth authentication. Defaults to None.
            Will read CLIENT_ID environment variable if none is provided in the function.
        client_secret (Optional[str], optional): Client secret for OAuth authentication. Defaults to None.
            Will read CLIENT_SECRET environment variable if none is provided in the function.
        verify (Optional[bool], optional): Whether to verify SSL certificates. Defaults to False.
            Will read VERIFY environment variable if none is provided in the function.

    Returns:
        dict: The JSON response containing information about the rollback.

    Raises:
        MissingParameterError: If plugin_id is not provided (handled by the Api).
        ValidationError: If invalid parameters are passed to the Api.
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


@mcp.tool()
def apply_remote_source_control_changes(
    app_sys_id: str,
    scope: str,
    branch_name: str,
    servicenow_instance: str = environment_servicenow_instance,
    auto_upgrade_base_app: Optional[bool] = None,
    username: str = environment_username,
    password: str = environment_password,
    client_id: Optional[str] = environment_client_id,
    client_secret: Optional[str] = environment_client_secret,
    verify: Optional[bool] = environment_verify,
) -> dict:
    """
    Apply remote source control changes on a ServiceNow instance.

    This tool applies changes from a specified branch for an application.
    Authentication can be provided via basic auth (username and password) or OAuth (client_id and client_secret).
    At least one authentication method must be configured in the Api client, but validation is handled by the underlying Api.

    Args:
        app_sys_id (str): The sys_id of the application for which changes should be applied.
        scope (str): The scope of the changes.
        branch_name (str): The name of the branch containing the changes.
        auto_upgrade_base_app (Optional[bool], optional): Flag indicating whether to auto-upgrade the base app. Defaults to None.
        servicenow_instance (str): The URL of the ServiceNow instance (e.g., https://yourinstance.servicenow.com).
            Will read SERVICENOW_INSTANCE environment variable if none is provided in the function.
        username (Optional[str], optional): Username for basic authentication. Defaults to None.
            Will read USERNAME environment variable if none is provided in the function.
        password (Optional[str], optional): Password for basic authentication. Defaults to None.
            Will read PASSWORD environment variable if none is provided in the function.
        client_id (Optional[str], optional): Client ID for OAuth authentication. Defaults to None.
            Will read CLIENT_ID environment variable if none is provided in the function.
        client_secret (Optional[str], optional): Client secret for OAuth authentication. Defaults to None.
            Will read CLIENT_SECRET environment variable if none is provided in the function.
        verify (Optional[bool], optional): Whether to verify SSL certificates. Defaults to False.
            Will read VERIFY environment variable if none is provided in the function.

    Returns:
        dict: The JSON response containing information about the applied changes.

    Raises:
        MissingParameterError: If app_sys_id or scope is not provided (handled by the Api).
        ParameterError: If auto_upgrade_base_app is not a boolean (handled by the Api).
        ValidationError: If invalid parameters are passed to the Api.
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


@mcp.tool()
def import_repository(
    repo_url: str,
    servicenow_instance: str = environment_servicenow_instance,
    credential_sys_id: Optional[str] = None,
    mid_server_sys_id: Optional[str] = None,
    branch_name: Optional[str] = None,
    auto_upgrade_base_app: Optional[bool] = None,
    username: str = environment_username,
    password: str = environment_password,
    client_id: Optional[str] = environment_client_id,
    client_secret: Optional[str] = environment_client_secret,
    verify: Optional[bool] = environment_verify,
) -> dict:
    """
    Import a repository on a ServiceNow instance.

    This tool imports a repository using the provided parameters.
    Authentication can be provided via basic auth (username and password) or OAuth (client_id and client_secret).
    At least one authentication method must be configured in the Api client, but validation is handled by the underlying Api.

    Args:
        repo_url (str): The URL of the repository to be imported.\
        credential_sys_id (Optional[str], optional): The sys_id of the credential to be used for the import. Defaults to None.
        mid_server_sys_id (Optional[str], optional): The sys_id of the MID Server to be used for the import. Defaults to None.
        branch_name (Optional[str], optional): The name of the branch to be imported. Defaults to None.
        auto_upgrade_base_app (Optional[bool], optional): Flag indicating whether to auto-upgrade the base app. Defaults to None.
        servicenow_instance (str): The URL of the ServiceNow instance (e.g., https://yourinstance.servicenow.com).
            Will read SERVICENOW_INSTANCE environment variable if none is provided in the function.
        username (Optional[str], optional): Username for basic authentication. Defaults to None.
            Will read USERNAME environment variable if none is provided in the function.
        password (Optional[str], optional): Password for basic authentication. Defaults to None.
            Will read PASSWORD environment variable if none is provided in the function.
        client_id (Optional[str], optional): Client ID for OAuth authentication. Defaults to None.
            Will read CLIENT_ID environment variable if none is provided in the function.
        client_secret (Optional[str], optional): Client secret for OAuth authentication. Defaults to None.
            Will read CLIENT_SECRET environment variable if none is provided in the function.
        verify (Optional[bool], optional): Whether to verify SSL certificates. Defaults to False.
            Will read VERIFY environment variable if none is provided in the function.

    Returns:
        dict: The JSON response containing information about the repository import.

    Raises:
        MissingParameterError: If repo_url is not provided (handled by the Api).
        ParameterError: If auto_upgrade_base_app is not a boolean (handled by the Api).
        ValidationError: If invalid parameters are passed to the Api.
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


@mcp.tool()
def run_test_suite(
    test_suite_sys_id: str,
    test_suite_name: str,
    servicenow_instance: str = environment_servicenow_instance,
    browser_name: Optional[str] = None,
    browser_version: Optional[str] = None,
    os_name: Optional[str] = None,
    os_version: Optional[str] = None,
    username: str = environment_username,
    password: str = environment_password,
    client_id: Optional[str] = environment_client_id,
    client_secret: Optional[str] = environment_client_secret,
    verify: Optional[bool] = environment_verify,
) -> dict:
    """
    Run a test suite on a ServiceNow instance.

    This tool initiates a test suite run using the provided parameters.
    Authentication can be provided via basic auth (username and password) or OAuth (client_id and client_secret).
    At least one authentication method must be configured in the Api client, but validation is handled by the underlying Api.

    Args:
        test_suite_sys_id (str): The sys_id of the test suite to be run.
        test_suite_name (str): The name of the test suite to be run.\
        browser_name (Optional[str], optional): The name of the browser for the test run. Defaults to None.
        browser_version (Optional[str], optional): The version of the browser for the test run. Defaults to None.
        os_name (Optional[str], optional): The name of the operating system for the test run. Defaults to None.
        os_version (Optional[str], optional): The version of the operating system for the test run. Defaults to None.
        servicenow_instance (str): The URL of the ServiceNow instance (e.g., https://yourinstance.servicenow.com).
            Will read SERVICENOW_INSTANCE environment variable if none is provided in the function.
        username (Optional[str], optional): Username for basic authentication. Defaults to None.
            Will read USERNAME environment variable if none is provided in the function.
        password (Optional[str], optional): Password for basic authentication. Defaults to None.
            Will read PASSWORD environment variable if none is provided in the function.
        client_id (Optional[str], optional): Client ID for OAuth authentication. Defaults to None.
            Will read CLIENT_ID environment variable if none is provided in the function.
        client_secret (Optional[str], optional): Client secret for OAuth authentication. Defaults to None.
            Will read CLIENT_SECRET environment variable if none is provided in the function.
        verify (Optional[bool], optional): Whether to verify SSL certificates. Defaults to False.
            Will read VERIFY environment variable if none is provided in the function.

    Returns:
        dict: The JSON response containing information about the test run.

    Raises:
        MissingParameterError: If test_suite_sys_id or test_suite_name is not provided (handled by the Api).
        ParameterError: If browser_name is not a valid string (handled by the Api).
        ValidationError: If invalid parameters are passed to the Api.
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


@mcp.tool()
def update_set_create(
    update_set_name: str,
    scope: str,
    sys_id: str,
    servicenow_instance: str = environment_servicenow_instance,
    description: Optional[str] = None,
    username: str = environment_username,
    password: str = environment_password,
    client_id: Optional[str] = environment_client_id,
    client_secret: Optional[str] = environment_client_secret,
    verify: Optional[bool] = environment_verify,
) -> dict:
    """
    Create a new update set on a ServiceNow instance.

    This tool creates a new update set and inserts it into the Update Sets table.
    Authentication can be provided via basic auth (username and password) or OAuth (client_id and client_secret).
    At least one authentication method must be configured in the Api client, but validation is handled by the underlying Api.

    Args:
        update_set_name (str): Name to give the update set.
        scope (str): The scope name of the application in which to create the new update set.
        sys_id (str): Sys_id of the application in which to create the new update set.\
        description (Optional[str], optional): Description of the update set. Defaults to None.
        servicenow_instance (str): The URL of the ServiceNow instance (e.g., https://yourinstance.servicenow.com).
            Will read SERVICENOW_INSTANCE environment variable if none is provided in the function.
        username (Optional[str], optional): Username for basic authentication. Defaults to None.
            Will read USERNAME environment variable if none is provided in the function.
        password (Optional[str], optional): Password for basic authentication. Defaults to None.
            Will read PASSWORD environment variable if none is provided in the function.
        client_id (Optional[str], optional): Client ID for OAuth authentication. Defaults to None.
            Will read CLIENT_ID environment variable if none is provided in the function.
        client_secret (Optional[str], optional): Client secret for OAuth authentication. Defaults to None.
            Will read CLIENT_SECRET environment variable if none is provided in the function.
        verify (Optional[bool], optional): Whether to verify SSL certificates. Defaults to False.
            Will read VERIFY environment variable if none is provided in the function.

    Returns:
        dict: The JSON response containing information about the created update set.

    Raises:
        MissingParameterError: If update_set_name is not provided or both sys_id and scope are not provided (handled by the Api).
        ValidationError: If invalid parameters are passed to the Api.
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


@mcp.tool()
def update_set_retrieve(
    update_set_id: str,
    servicenow_instance: str = environment_servicenow_instance,
    update_source_id: Optional[str] = None,
    update_source_instance_id: Optional[str] = None,
    auto_preview: Optional[bool] = None,
    cleanup_retrieved: Optional[bool] = None,
    username: str = environment_username,
    password: str = environment_password,
    client_id: Optional[str] = environment_client_id,
    client_secret: Optional[str] = environment_client_secret,
    verify: Optional[bool] = environment_verify,
) -> dict:
    """
    Retrieve an update set on a ServiceNow instance.

    This tool retrieves an update set and optionally removes the existing retrieved update set from the instance.
    Authentication can be provided via basic auth (username and password) or OAuth (client_id and client_secret).
    At least one authentication method must be configured in the Api client, but validation is handled by the underlying Api.

    Args:
        update_set_id (str): Sys_id of the update set on the source instance from where the update set was retrieved.\
        update_source_id (Optional[str], optional): Sys_id of the remote instance record. Defaults to None.
        update_source_instance_id (Optional[str], optional): Instance ID of the remote instance. Defaults to None.
        auto_preview (Optional[bool], optional): Flag that indicates whether to automatically preview the update set after retrieval. Defaults to None.
        cleanup_retrieved (Optional[bool], optional): Flag that indicates whether to remove the existing retrieved update set from the instance. Defaults to None.
        servicenow_instance (str): The URL of the ServiceNow instance (e.g., https://yourinstance.servicenow.com).
            Will read SERVICENOW_INSTANCE environment variable if none is provided in the function.
        username (Optional[str], optional): Username for basic authentication. Defaults to None.
            Will read USERNAME environment variable if none is provided in the function.
        password (Optional[str], optional): Password for basic authentication. Defaults to None.
            Will read PASSWORD environment variable if none is provided in the function.
        client_id (Optional[str], optional): Client ID for OAuth authentication. Defaults to None.
            Will read CLIENT_ID environment variable if none is provided in the function.
        client_secret (Optional[str], optional): Client secret for OAuth authentication. Defaults to None.
            Will read CLIENT_SECRET environment variable if none is provided in the function.
        verify (Optional[bool], optional): Whether to verify SSL certificates. Defaults to False.
            Will read VERIFY environment variable if none is provided in the function.
    Returns:
        dict: The JSON response containing progress information about the retrieval.

    Raises:
        MissingParameterError: If update_set_id is not provided (handled by the Api).
        ValidationError: If invalid parameters are passed to the Api.
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


@mcp.tool()
def update_set_preview(
    remote_update_set_id: str,
    servicenow_instance: str = environment_servicenow_instance,
    username: str = environment_username,
    password: str = environment_password,
    client_id: Optional[str] = environment_client_id,
    client_secret: Optional[str] = environment_client_secret,
    verify: Optional[bool] = environment_verify,
) -> dict:
    """
    Preview an update set on a ServiceNow instance.

    This tool previews an update set to check for conflicts and retrieve progress information.
    Authentication can be provided via basic auth (username and password) or OAuth (client_id and client_secret).
    At least one authentication method must be configured in the Api client, but validation is handled by the underlying Api.

    Args:
        remote_update_set_id (str): Sys_id of the update set to preview.
        servicenow_instance (str): The URL of the ServiceNow instance (e.g., https://yourinstance.servicenow.com).
            Will read SERVICENOW_INSTANCE environment variable if none is provided in the function.
        username (Optional[str], optional): Username for basic authentication. Defaults to None.
            Will read USERNAME environment variable if none is provided in the function.
        password (Optional[str], optional): Password for basic authentication. Defaults to None.
            Will read PASSWORD environment variable if none is provided in the function.
        client_id (Optional[str], optional): Client ID for OAuth authentication. Defaults to None.
            Will read CLIENT_ID environment variable if none is provided in the function.
        client_secret (Optional[str], optional): Client secret for OAuth authentication. Defaults to None.
            Will read CLIENT_SECRET environment variable if none is provided in the function.
        verify (Optional[bool], optional): Whether to verify SSL certificates. Defaults to False.
            Will read VERIFY environment variable if none is provided in the function.

    Returns:
        dict: The JSON response containing progress information about the preview.

    Raises:
        MissingParameterError: If remote_update_set_id is not provided (handled by the Api).
        ValidationError: If invalid parameters are passed to the Api.
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


@mcp.tool()
def update_set_commit(
    remote_update_set_id: str,
    servicenow_instance: str = environment_servicenow_instance,
    force_commit: Optional[str] = None,
    username: str = environment_username,
    password: str = environment_password,
    client_id: Optional[str] = environment_client_id,
    client_secret: Optional[str] = environment_client_secret,
    verify: Optional[bool] = environment_verify,
) -> dict:
    """
    Commit an update set on a ServiceNow instance.

    This tool commits an update set with the provided sys_id.
    Authentication can be provided via basic auth (username and password) or OAuth (client_id and client_secret).
    At least one authentication method must be configured in the Api client, but validation is handled by the underlying Api.

    Args:
        remote_update_set_id (str): Sys_id of the update set to commit.
        servicenow_instance (str): The URL of the ServiceNow instance (e.g., https://yourinstance.servicenow.com).
        force_commit (Optional[str], optional): Flag that indicates whether to force commit the update set. Defaults to None.
        servicenow_instance (str): The URL of the ServiceNow instance (e.g., https://yourinstance.servicenow.com).
            Will read SERVICENOW_INSTANCE environment variable if none is provided in the function.
        username (Optional[str], optional): Username for basic authentication. Defaults to None.
            Will read USERNAME environment variable if none is provided in the function.
        password (Optional[str], optional): Password for basic authentication. Defaults to None.
            Will read PASSWORD environment variable if none is provided in the function.
        client_id (Optional[str], optional): Client ID for OAuth authentication. Defaults to None.
            Will read CLIENT_ID environment variable if none is provided in the function.
        client_secret (Optional[str], optional): Client secret for OAuth authentication. Defaults to None.
            Will read CLIENT_SECRET environment variable if none is provided in the function.
        verify (Optional[bool], optional): Whether to verify SSL certificates. Defaults to False.
            Will read VERIFY environment variable if none is provided in the function.

    Returns:
        dict: The JSON response containing progress information about the commit.

    Raises:
        MissingParameterError: If remote_update_set_id is not provided (handled by the Api).
        ValidationError: If invalid parameters are passed to the Api.
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


@mcp.tool()
def update_set_commit_multiple(
    remote_update_set_ids: List[str],
    servicenow_instance: str = environment_servicenow_instance,
    force_commit: Optional[str] = None,
    username: str = environment_username,
    password: str = environment_password,
    client_id: Optional[str] = environment_client_id,
    client_secret: Optional[str] = environment_client_secret,
    verify: Optional[bool] = environment_verify,
) -> dict:
    """
    Commit multiple update sets on a ServiceNow instance.

    This tool commits multiple update sets in a single request according to the order provided.
    Authentication can be provided via basic auth (username and password) or OAuth (client_id and client_secret).
    At least one authentication method must be configured in the Api client, but validation is handled by the underlying Api.

    Args:
        remote_update_set_ids (List[str]): List of sys_ids associated with update sets to commit. Sys_ids are committed in the order given.
        servicenow_instance (str): The URL of the ServiceNow instance (e.g., https://yourinstance.servicenow.com).
        force_commit (Optional[str], optional): Flag that indicates whether to force commit the update sets. Defaults to None.
        servicenow_instance (str): The URL of the ServiceNow instance (e.g., https://yourinstance.servicenow.com).
            Will read SERVICENOW_INSTANCE environment variable if none is provided in the function.
        username (Optional[str], optional): Username for basic authentication. Defaults to None.
            Will read USERNAME environment variable if none is provided in the function.
        password (Optional[str], optional): Password for basic authentication. Defaults to None.
            Will read PASSWORD environment variable if none is provided in the function.
        client_id (Optional[str], optional): Client ID for OAuth authentication. Defaults to None.
            Will read CLIENT_ID environment variable if none is provided in the function.
        client_secret (Optional[str], optional): Client secret for OAuth authentication. Defaults to None.
            Will read CLIENT_SECRET environment variable if none is provided in the function.
        verify (Optional[bool], optional): Whether to verify SSL certificates. Defaults to False.
            Will read VERIFY environment variable if none is provided in the function.

    Returns:
        dict: The JSON response containing progress information about the multiple commits.

    Raises:
        MissingParameterError: If remote_update_set_ids is not provided (handled by the Api).
        ValidationError: If invalid parameters are passed to the Api.
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


@mcp.tool()
def update_set_back_out(
    update_set_id: str,
    servicenow_instance: str = environment_servicenow_instance,
    rollback_installs: Optional[bool] = None,
    username: str = environment_username,
    password: str = environment_password,
    client_id: Optional[str] = environment_client_id,
    client_secret: Optional[str] = environment_client_secret,
    verify: Optional[bool] = environment_verify,
) -> dict:
    """
    Back out an update set installation on a ServiceNow instance.

    This tool backs out an installation operation for an update set with the provided sys_id.
    Authentication can be provided via basic auth (username and password) or OAuth (client_id and client_secret).
    At least one authentication method must be configured in the Api client, but validation is handled by the underlying Api.

    Args:
        update_set_id (str): Sys_id of the update set.
        servicenow_instance (str): The URL of the ServiceNow instance (e.g., https://yourinstance.servicenow.com).
        rollback_installs (Optional[bool], optional): Flag that indicates whether to rollback the batch installation performed during the update set commit. Defaults to None.
        servicenow_instance (str): The URL of the ServiceNow instance (e.g., https://yourinstance.servicenow.com).
            Will read SERVICENOW_INSTANCE environment variable if none is provided in the function.
        username (Optional[str], optional): Username for basic authentication. Defaults to None.
            Will read USERNAME environment variable if none is provided in the function.
        password (Optional[str], optional): Password for basic authentication. Defaults to None.
            Will read PASSWORD environment variable if none is provided in the function.
        client_id (Optional[str], optional): Client ID for OAuth authentication. Defaults to None.
            Will read CLIENT_ID environment variable if none is provided in the function.
        client_secret (Optional[str], optional): Client secret for OAuth authentication. Defaults to None.
            Will read CLIENT_SECRET environment variable if none is provided in the function.
        verify (Optional[bool], optional): Whether to verify SSL certificates. Defaults to False.
            Will read VERIFY environment variable if none is provided in the function.

    Returns:
        dict: The JSON response containing progress information about the back out.

    Raises:
        MissingParameterError: If update_set_id is not provided (handled by the Api).
        ValidationError: If invalid parameters are passed to the Api.
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
@mcp.tool()
def get_change_requests(
    servicenow_instance: str = environment_servicenow_instance,
    order: Optional[str] = None,
    name_value_pairs: Optional[Dict[str, str]] = None,
    sysparm_query: Optional[str] = None,
    text_search: Optional[str] = None,
    change_type: Optional[str] = None,
    sysparm_offset: Optional[int] = None,
    sysparm_limit: Optional[int] = None,
    username: str = environment_username,
    password: str = environment_password,
    client_id: Optional[str] = environment_client_id,
    client_secret: Optional[str] = environment_client_secret,
    verify: Optional[bool] = environment_verify,
) -> dict:
    """
    Retrieve change requests from a ServiceNow instance.

    This tool retrieves change requests based on specified parameters, with support for pagination.
    Authentication can be provided via basic auth (username and password) or OAuth (client_id and client_secret).
    At least one authentication method must be configured in the Api client, but validation is handled by the underlying Api.

    Args:
        servicenow_instance (str): The URL of the ServiceNow instance (e.g., https://yourinstance.servicenow.com).
        order (Optional[str], optional): Ordering parameter for sorting results. Defaults to None.
        name_value_pairs (Optional[Dict[str, str]], optional): Additional name-value pairs for filtering. Defaults to None.
        sysparm_query (Optional[str], optional): Query parameter for filtering results. Defaults to None.
        text_search (Optional[str], optional): Text search parameter for searching results. Defaults to None.
        change_type (Optional[str], optional): Type of change (emergency, normal, standard, model). Defaults to None.
        sysparm_offset (Optional[int], optional): Offset for pagination. Defaults to None.
        sysparm_limit (Optional[int], optional): Limit for pagination. Defaults to None.
        servicenow_instance (str): The URL of the ServiceNow instance (e.g., https://yourinstance.servicenow.com).
            Will read SERVICENOW_INSTANCE environment variable if none is provided in the function.
        username (Optional[str], optional): Username for basic authentication. Defaults to None.
            Will read USERNAME environment variable if none is provided in the function.
        password (Optional[str], optional): Password for basic authentication. Defaults to None.
            Will read PASSWORD environment variable if none is provided in the function.
        client_id (Optional[str], optional): Client ID for OAuth authentication. Defaults to None.
            Will read CLIENT_ID environment variable if none is provided in the function.
        client_secret (Optional[str], optional): Client secret for OAuth authentication. Defaults to None.
            Will read CLIENT_SECRET environment variable if none is provided in the function.
        verify (Optional[bool], optional): Whether to verify SSL certificates. Defaults to False.
            Will read VERIFY environment variable if none is provided in the function.

    Returns:
        dict: The JSON response containing information about change requests.

    Raises:
        ParameterError: If invalid parameters or responses are encountered (handled by the Api).
        ParameterError: If change_type is specified but not valid (handled by the Api).
        ParameterError: If JSON serialization or deserialization fails (handled by the Api).
        ParameterError: If unexpected response format is encountered (handled by the Api).
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


@mcp.tool()
def get_change_request_nextstate(
    change_request_sys_id: str,
    servicenow_instance: str = environment_servicenow_instance,
    username: str = environment_username,
    password: str = environment_password,
    client_id: Optional[str] = environment_client_id,
    client_secret: Optional[str] = environment_client_secret,
    verify: Optional[bool] = environment_verify,
) -> dict:
    """
    Retrieve the next state of a specific change request from a ServiceNow instance.

    This tool retrieves the next state of a change request using the provided sys_id.
    Authentication can be provided via basic auth (username and password) or OAuth (client_id and client_secret).
    At least one authentication method must be configured in the Api client, but validation is handled by the underlying Api.

    Args:
        change_request_sys_id (str): Sys ID of the change request.
        servicenow_instance (str): The URL of the ServiceNow instance (e.g., https://yourinstance.servicenow.com).
            Will read SERVICENOW_INSTANCE environment variable if none is provided in the function.
        username (Optional[str], optional): Username for basic authentication. Defaults to None.
            Will read USERNAME environment variable if none is provided in the function.
        password (Optional[str], optional): Password for basic authentication. Defaults to None.
            Will read PASSWORD environment variable if none is provided in the function.
        client_id (Optional[str], optional): Client ID for OAuth authentication. Defaults to None.
            Will read CLIENT_ID environment variable if none is provided in the function.
        client_secret (Optional[str], optional): Client secret for OAuth authentication. Defaults to None.
            Will read CLIENT_SECRET environment variable if none is provided in the function.
        verify (Optional[bool], optional): Whether to verify SSL certificates. Defaults to False.
            Will read VERIFY environment variable if none is provided in the function.

    Returns:
        dict: The JSON response containing information about the next state.

    Raises:
        MissingParameterError: If change_request_sys_id is not provided (handled by the Api).
        ParameterError: If invalid parameters or responses are encountered (handled by the Api).
        ParameterError: If JSON deserialization fails (handled by the Api).
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


@mcp.tool()
def get_change_request_schedule(
    cmdb_ci_sys_id: str,
    servicenow_instance: str = environment_servicenow_instance,
    username: str = environment_username,
    password: str = environment_password,
    client_id: Optional[str] = environment_client_id,
    client_secret: Optional[str] = environment_client_secret,
    verify: Optional[bool] = environment_verify,
) -> dict:
    """
    Retrieve the schedule of a change request from a ServiceNow instance.

    This tool retrieves the schedule of a change request based on the provided CI sys_id.
    Authentication can be provided via basic auth (username and password) or OAuth (client_id and client_secret).
    At least one authentication method must be configured in the Api client, but validation is handled by the underlying Api.

    Args:
        cmdb_ci_sys_id (str): Sys ID of the CI (Configuration Item).
        servicenow_instance (str): The URL of the ServiceNow instance (e.g., https://yourinstance.servicenow.com).
            Will read SERVICENOW_INSTANCE environment variable if none is provided in the function.
        username (Optional[str], optional): Username for basic authentication. Defaults to None.
            Will read USERNAME environment variable if none is provided in the function.
        password (Optional[str], optional): Password for basic authentication. Defaults to None.
            Will read PASSWORD environment variable if none is provided in the function.
        client_id (Optional[str], optional): Client ID for OAuth authentication. Defaults to None.
            Will read CLIENT_ID environment variable if none is provided in the function.
        client_secret (Optional[str], optional): Client secret for OAuth authentication. Defaults to None.
            Will read CLIENT_SECRET environment variable if none is provided in the function.
        verify (Optional[bool], optional): Whether to verify SSL certificates. Defaults to False.
            Will read VERIFY environment variable if none is provided in the function.

    Returns:
        dict: The JSON response containing information about the change request schedule.

    Raises:
        MissingParameterError: If cmdb_ci_sys_id is not provided (handled by the Api).
        ParameterError: If invalid parameters or responses are encountered (handled by the Api).
        ParameterError: If JSON deserialization fails (handled by the Api).
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


@mcp.tool()
def get_change_request_tasks(
    change_request_sys_id: str,
    servicenow_instance: str = environment_servicenow_instance,
    order: Optional[str] = None,
    name_value_pairs: Optional[Dict[str, str]] = None,
    sysparm_query: Optional[str] = None,
    text_search: Optional[str] = None,
    sysparm_offset: Optional[int] = None,
    sysparm_limit: Optional[int] = None,
    username: str = environment_username,
    password: str = environment_password,
    client_id: Optional[str] = environment_client_id,
    client_secret: Optional[str] = environment_client_secret,
    verify: Optional[bool] = environment_verify,
) -> dict:
    """
    Retrieve tasks associated with a specific change request from a ServiceNow instance.

    This tool retrieves tasks for a change request based on the provided sys_id, with support for pagination.
    Authentication can be provided via basic auth (username and password) or OAuth (client_id and client_secret).
    At least one authentication method must be configured in the Api client, but validation is handled by the underlying Api.

    Args:
        change_request_sys_id (str): Sys ID of the change request.
        servicenow_instance (str): The URL of the ServiceNow instance (e.g., https://yourinstance.servicenow.com).
        order (Optional[str], optional): Ordering parameter for sorting results. Defaults to None.
        name_value_pairs (Optional[Dict[str, str]], optional): Additional name-value pairs for filtering. Defaults to None.
        sysparm_query (Optional[str], optional): Query parameter for filtering results. Defaults to None.
        text_search (Optional[str], optional): Text search parameter for searching results. Defaults to None.
        sysparm_offset (Optional[int], optional): Offset for pagination. Defaults to None.
        sysparm_limit (Optional[int], optional): Limit for pagination. Defaults to None.
        servicenow_instance (str): The URL of the ServiceNow instance (e.g., https://yourinstance.servicenow.com).
            Will read SERVICENOW_INSTANCE environment variable if none is provided in the function.
        username (Optional[str], optional): Username for basic authentication. Defaults to None.
            Will read USERNAME environment variable if none is provided in the function.
        password (Optional[str], optional): Password for basic authentication. Defaults to None.
            Will read PASSWORD environment variable if none is provided in the function.
        client_id (Optional[str], optional): Client ID for OAuth authentication. Defaults to None.
            Will read CLIENT_ID environment variable if none is provided in the function.
        client_secret (Optional[str], optional): Client secret for OAuth authentication. Defaults to None.
            Will read CLIENT_SECRET environment variable if none is provided in the function.
        verify (Optional[bool], optional): Whether to verify SSL certificates. Defaults to False.
            Will read VERIFY environment variable if none is provided in the function.

    Returns:
        dict: The JSON response containing information about change request tasks.

    Raises:
        MissingParameterError: If change_request_sys_id is not provided (handled by the Api).
        ParameterError: If invalid parameters or responses are encountered (handled by the Api).
        ParameterError: If JSON deserialization fails (handled by the Api).
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


@mcp.tool()
def get_change_request(
    change_request_sys_id: str,
    servicenow_instance: str = environment_servicenow_instance,
    change_type: Optional[str] = None,
    username: str = environment_username,
    password: str = environment_password,
    client_id: Optional[str] = environment_client_id,
    client_secret: Optional[str] = environment_client_secret,
    verify: Optional[bool] = environment_verify,
) -> dict:
    """
    Retrieve details of a specific change request from a ServiceNow instance.

    This tool retrieves details of a change request based on the provided sys_id and optional change type.
    Authentication can be provided via basic auth (username and password) or OAuth (client_id and client_secret).
    At least one authentication method must be configured in the Api client, but validation is handled by the underlying Api.

    Args:
        change_request_sys_id (str): Sys ID of the change request.
        servicenow_instance (str): The URL of the ServiceNow instance (e.g., https://yourinstance.servicenow.com).
        change_type (Optional[str], optional): Type of change (emergency, normal, standard). Defaults to None.
        servicenow_instance (str): The URL of the ServiceNow instance (e.g., https://yourinstance.servicenow.com).
            Will read SERVICENOW_INSTANCE environment variable if none is provided in the function.
        username (Optional[str], optional): Username for basic authentication. Defaults to None.
            Will read USERNAME environment variable if none is provided in the function.
        password (Optional[str], optional): Password for basic authentication. Defaults to None.
            Will read PASSWORD environment variable if none is provided in the function.
        client_id (Optional[str], optional): Client ID for OAuth authentication. Defaults to None.
            Will read CLIENT_ID environment variable if none is provided in the function.
        client_secret (Optional[str], optional): Client secret for OAuth authentication. Defaults to None.
            Will read CLIENT_SECRET environment variable if none is provided in the function.
        verify (Optional[bool], optional): Whether to verify SSL certificates. Defaults to False.
            Will read VERIFY environment variable if none is provided in the function.

    Returns:
        dict: The JSON response containing information about the change request.

    Raises:
        MissingParameterError: If change_request_sys_id is not provided (handled by the Api).
        ParameterError: If invalid parameters or responses are encountered (handled by the Api).
        ParameterError: If change_type is specified but not valid (handled by the Api).
        ParameterError: If JSON deserialization fails (handled by the Api).
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


@mcp.tool()
def get_change_request_ci(
    change_request_sys_id: str,
    servicenow_instance: str = environment_servicenow_instance,
    username: str = environment_username,
    password: str = environment_password,
    client_id: Optional[str] = environment_client_id,
    client_secret: Optional[str] = environment_client_secret,
    verify: Optional[bool] = environment_verify,
) -> dict:
    """
    Retrieve the configuration item (CI) associated with a change request from a ServiceNow instance.

    This tool retrieves the CI associated with a change request based on the provided sys_id.
    Authentication can be provided via basic auth (username and password) or OAuth (client_id and client_secret).
    At least one authentication method must be configured in the Api client, but validation is handled by the underlying Api.

    Args:
        change_request_sys_id (str): Sys ID of the change request.
        servicenow_instance (str): The URL of the ServiceNow instance (e.g., https://yourinstance.servicenow.com).
            Will read SERVICENOW_INSTANCE environment variable if none is provided in the function.
        username (Optional[str], optional): Username for basic authentication. Defaults to None.
            Will read USERNAME environment variable if none is provided in the function.
        password (Optional[str], optional): Password for basic authentication. Defaults to None.
            Will read PASSWORD environment variable if none is provided in the function.
        client_id (Optional[str], optional): Client ID for OAuth authentication. Defaults to None.
            Will read CLIENT_ID environment variable if none is provided in the function.
        client_secret (Optional[str], optional): Client secret for OAuth authentication. Defaults to None.
            Will read CLIENT_SECRET environment variable if none is provided in the function.
        verify (Optional[bool], optional): Whether to verify SSL certificates. Defaults to False.
            Will read VERIFY environment variable if none is provided in the function.

    Returns:
        dict: The JSON response containing information about the associated CI.

    Raises:
        MissingParameterError: If change_request_sys_id is not provided (handled by the Api).
        ParameterError: If invalid parameters or responses are encountered (handled by the Api).
        ParameterError: If JSON deserialization fails (handled by the Api).
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


@mcp.tool()
def get_change_request_conflict(
    change_request_sys_id: str,
    servicenow_instance: str = environment_servicenow_instance,
    username: str = environment_username,
    password: str = environment_password,
    client_id: Optional[str] = environment_client_id,
    client_secret: Optional[str] = environment_client_secret,
    verify: Optional[bool] = environment_verify,
) -> dict:
    """
    Retrieve conflict information associated with a change request from a ServiceNow instance.

    This tool retrieves conflict information for a change request based on the provided sys_id.
    Authentication can be provided via basic auth (username and password) or OAuth (client_id and client_secret).
    At least one authentication method must be configured in the Api client, but validation is handled by the underlying Api.

    Args:
        change_request_sys_id (str): Sys ID of the change request.
        servicenow_instance (str): The URL of the ServiceNow instance (e.g., https://yourinstance.servicenow.com).
            Will read SERVICENOW_INSTANCE environment variable if none is provided in the function.
        username (Optional[str], optional): Username for basic authentication. Defaults to None.
            Will read USERNAME environment variable if none is provided in the function.
        password (Optional[str], optional): Password for basic authentication. Defaults to None.
            Will read PASSWORD environment variable if none is provided in the function.
        client_id (Optional[str], optional): Client ID for OAuth authentication. Defaults to None.
            Will read CLIENT_ID environment variable if none is provided in the function.
        client_secret (Optional[str], optional): Client secret for OAuth authentication. Defaults to None.
            Will read CLIENT_SECRET environment variable if none is provided in the function.
        verify (Optional[bool], optional): Whether to verify SSL certificates. Defaults to False.
            Will read VERIFY environment variable if none is provided in the function.

    Returns:
        dict: The JSON response containing information about the conflicts.

    Raises:
        MissingParameterError: If change_request_sys_id is not provided (handled by the Api).
        ParameterError: If invalid parameters or responses are encountered (handled by the Api).
        ParameterError: If JSON deserialization fails (handled by the Api).
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


@mcp.tool()
def get_standard_change_request_templates(
    servicenow_instance: str = environment_servicenow_instance,
    order: Optional[str] = None,
    name_value_pairs: Optional[Dict[str, str]] = None,
    sysparm_query: Optional[str] = None,
    text_search: Optional[str] = None,
    sysparm_offset: Optional[int] = None,
    sysparm_limit: Optional[int] = None,
    username: str = environment_username,
    password: str = environment_password,
    client_id: Optional[str] = environment_client_id,
    client_secret: Optional[str] = environment_client_secret,
    verify: Optional[bool] = environment_verify,
) -> dict:
    """
    Retrieve standard change request templates from a ServiceNow instance.

    This tool retrieves standard change request templates based on specified parameters, with support for pagination.
    Authentication can be provided via basic auth (username and password) or OAuth (client_id and client_secret).
    At least one authentication method must be configured in the Api client, but validation is handled by the underlying Api.

    Args:
        servicenow_instance (str): The URL of the ServiceNow instance (e.g., https://yourinstance.servicenow.com).
        order (Optional[str], optional): Ordering parameter for sorting results. Defaults to None.
        name_value_pairs (Optional[Dict[str, str]], optional): Additional name-value pairs for filtering. Defaults to None.
        sysparm_query (Optional[str], optional): Query parameter for filtering results. Defaults to None.
        text_search (Optional[str], optional): Text search parameter for searching results. Defaults to None.
        sysparm_offset (Optional[int], optional): Offset for pagination. Defaults to None.
        sysparm_limit (Optional[int], optional): Limit for pagination. Defaults to None.
        servicenow_instance (str): The URL of the ServiceNow instance (e.g., https://yourinstance.servicenow.com).
            Will read SERVICENOW_INSTANCE environment variable if none is provided in the function.
        username (Optional[str], optional): Username for basic authentication. Defaults to None.
            Will read USERNAME environment variable if none is provided in the function.
        password (Optional[str], optional): Password for basic authentication. Defaults to None.
            Will read PASSWORD environment variable if none is provided in the function.
        client_id (Optional[str], optional): Client ID for OAuth authentication. Defaults to None.
            Will read CLIENT_ID environment variable if none is provided in the function.
        client_secret (Optional[str], optional): Client secret for OAuth authentication. Defaults to None.
            Will read CLIENT_SECRET environment variable if none is provided in the function.
        verify (Optional[bool], optional): Whether to verify SSL certificates. Defaults to False.
            Will read VERIFY environment variable if none is provided in the function.

    Returns:
        dict: The JSON response containing information about standard change request templates.

    Raises:
        ParameterError: If invalid parameters or responses are encountered (handled by the Api).
        ParameterError: If JSON deserialization fails (handled by the Api).
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


@mcp.tool()
def get_change_request_models(
    servicenow_instance: str = environment_servicenow_instance,
    order: Optional[str] = None,
    name_value_pairs: Optional[Dict[str, str]] = None,
    sysparm_query: Optional[str] = None,
    text_search: Optional[str] = None,
    change_type: Optional[str] = None,
    sysparm_offset: Optional[int] = None,
    sysparm_limit: Optional[int] = None,
    username: str = environment_username,
    password: str = environment_password,
    client_id: Optional[str] = environment_client_id,
    client_secret: Optional[str] = environment_client_secret,
    verify: Optional[bool] = environment_verify,
) -> dict:
    """
    Retrieve change request models from a ServiceNow instance.

    This tool retrieves change request models based on specified parameters, with support for pagination.
    Authentication can be provided via basic auth (username and password) or OAuth (client_id and client_secret).
    At least one authentication method must be configured in the Api client, but validation is handled by the underlying Api.

    Args:
        servicenow_instance (str): The URL of the ServiceNow instance (e.g., https://yourinstance.servicenow.com).
        order (Optional[str], optional): Ordering parameter for sorting results. Defaults to None.
        name_value_pairs (Optional[Dict[str, str]], optional): Additional name-value pairs for filtering. Defaults to None.
        sysparm_query (Optional[str], optional): Query parameter for filtering results. Defaults to None.
        text_search (Optional[str], optional): Text search parameter for searching results. Defaults to None.
        change_type (Optional[str], optional): Type of change (emergency, normal, standard, model). Defaults to None.
        sysparm_offset (Optional[int], optional): Offset for pagination. Defaults to None.
        sysparm_limit (Optional[int], optional): Limit for pagination. Defaults to None.
        servicenow_instance (str): The URL of the ServiceNow instance (e.g., https://yourinstance.servicenow.com).
            Will read SERVICENOW_INSTANCE environment variable if none is provided in the function.
        username (Optional[str], optional): Username for basic authentication. Defaults to None.
            Will read USERNAME environment variable if none is provided in the function.
        password (Optional[str], optional): Password for basic authentication. Defaults to None.
            Will read PASSWORD environment variable if none is provided in the function.
        client_id (Optional[str], optional): Client ID for OAuth authentication. Defaults to None.
            Will read CLIENT_ID environment variable if none is provided in the function.
        client_secret (Optional[str], optional): Client secret for OAuth authentication. Defaults to None.
            Will read CLIENT_SECRET environment variable if none is provided in the function.
        verify (Optional[bool], optional): Whether to verify SSL certificates. Defaults to False.
            Will read VERIFY environment variable if none is provided in the function.

    Returns:
        dict: The JSON response containing information about change request models.

    Raises:
        ParameterError: If invalid parameters or responses are encountered (handled by the Api).
        ParameterError: If JSON deserialization fails (handled by the Api).
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


@mcp.tool()
def get_standard_change_request_model(
    model_sys_id: str,
    servicenow_instance: str = environment_servicenow_instance,
    username: str = environment_username,
    password: str = environment_password,
    client_id: Optional[str] = environment_client_id,
    client_secret: Optional[str] = environment_client_secret,
    verify: Optional[bool] = environment_verify,
) -> dict:
    """
    Retrieve details of a standard change request model from a ServiceNow instance.

    This tool retrieves details of a standard change request model based on the provided sys_id.
    Authentication can be provided via basic auth (username and password) or OAuth (client_id and client_secret).
    At least one authentication method must be configured in the Api client, but validation is handled by the underlying Api.

    Args:
        model_sys_id (str): Sys ID of the standard change request model.
        servicenow_instance (str): The URL of the ServiceNow instance (e.g., https://yourinstance.servicenow.com).
            Will read SERVICENOW_INSTANCE environment variable if none is provided in the function.
        username (Optional[str], optional): Username for basic authentication. Defaults to None.
            Will read USERNAME environment variable if none is provided in the function.
        password (Optional[str], optional): Password for basic authentication. Defaults to None.
            Will read PASSWORD environment variable if none is provided in the function.
        client_id (Optional[str], optional): Client ID for OAuth authentication. Defaults to None.
            Will read CLIENT_ID environment variable if none is provided in the function.
        client_secret (Optional[str], optional): Client secret for OAuth authentication. Defaults to None.
            Will read CLIENT_SECRET environment variable if none is provided in the function.
        verify (Optional[bool], optional): Whether to verify SSL certificates. Defaults to False.
            Will read VERIFY environment variable if none is provided in the function.

    Returns:
        dict: The JSON response containing information about the standard change request model.

    Raises:
        MissingParameterError: If model_sys_id is not provided (handled by the Api).
        ParameterError: If invalid parameters or responses are encountered (handled by the Api).
        ParameterError: If JSON deserialization fails (handled by the Api).
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


# Change Management Tools (Continued)
@mcp.tool()
def get_standard_change_request_template(
    template_sys_id: str,
    servicenow_instance: str = environment_servicenow_instance,
    username: str = environment_username,
    password: str = environment_password,
    client_id: Optional[str] = environment_client_id,
    client_secret: Optional[str] = environment_client_secret,
    verify: Optional[bool] = environment_verify,
) -> dict:
    """
    Retrieve details of a standard change request template from a ServiceNow instance.

    This tool retrieves details of a standard change request template based on the provided sys_id.
    Authentication can be provided via basic auth (username and password) or OAuth (client_id and client_secret).
    At least one authentication method must be configured in the Api client, but validation is handled by the underlying Api.

    Args:
        template_sys_id (str): Sys ID of the standard change request template.
        servicenow_instance (str): The URL of the ServiceNow instance (e.g., https://yourinstance.servicenow.com).
            Will read SERVICENOW_INSTANCE environment variable if none is provided in the function.
        username (Optional[str], optional): Username for basic authentication. Defaults to None.
            Will read USERNAME environment variable if none is provided in the function.
        password (Optional[str], optional): Password for basic authentication. Defaults to None.
            Will read PASSWORD environment variable if none is provided in the function.
        client_id (Optional[str], optional): Client ID for OAuth authentication. Defaults to None.
            Will read CLIENT_ID environment variable if none is provided in the function.
        client_secret (Optional[str], optional): Client secret for OAuth authentication. Defaults to None.
            Will read CLIENT_SECRET environment variable if none is provided in the function.
        verify (Optional[bool], optional): Whether to verify SSL certificates. Defaults to False.
            Will read VERIFY environment variable if none is provided in the function.

    Returns:
        dict: The JSON response containing information about the standard change request template.

    Raises:
        MissingParameterError: If template_sys_id is not provided (handled by the Api).
        ParameterError: If invalid parameters or responses are encountered (handled by the Api).
        ParameterError: If JSON deserialization fails (handled by the Api).
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


@mcp.tool()
def get_change_request_worker(
    worker_sys_id: str,
    servicenow_instance: str = environment_servicenow_instance,
    username: str = environment_username,
    password: str = environment_password,
    client_id: Optional[str] = environment_client_id,
    client_secret: Optional[str] = environment_client_secret,
    verify: Optional[bool] = environment_verify,
) -> dict:
    """
    Retrieve details of a change request worker from a ServiceNow instance.

    This tool retrieves details of a change request worker based on the provided sys_id.
    Authentication can be provided via basic auth (username and password) or OAuth (client_id and client_secret).
    At least one authentication method must be configured in the Api client, but validation is handled by the underlying Api.

    Args:
        worker_sys_id (str): Sys ID of the change request worker.
        servicenow_instance (str): The URL of the ServiceNow instance (e.g., https://yourinstance.servicenow.com).
            Will read SERVICENOW_INSTANCE environment variable if none is provided in the function.
        username (Optional[str], optional): Username for basic authentication. Defaults to None.
            Will read USERNAME environment variable if none is provided in the function.
        password (Optional[str], optional): Password for basic authentication. Defaults to None.
            Will read PASSWORD environment variable if none is provided in the function.
        client_id (Optional[str], optional): Client ID for OAuth authentication. Defaults to None.
            Will read CLIENT_ID environment variable if none is provided in the function.
        client_secret (Optional[str], optional): Client secret for OAuth authentication. Defaults to None.
            Will read CLIENT_SECRET environment variable if none is provided in the function.
        verify (Optional[bool], optional): Whether to verify SSL certificates. Defaults to False.
            Will read VERIFY environment variable if none is provided in the function.

    Returns:
        dict: The JSON response containing information about the change request worker.

    Raises:
        MissingParameterError: If worker_sys_id is not provided (handled by the Api).
        ParameterError: If invalid parameters or responses are encountered (handled by the Api).
        ParameterError: If JSON deserialization fails (handled by the Api).
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


@mcp.tool()
def create_change_request(
    name_value_pairs: Dict[str, str],
    servicenow_instance: str = environment_servicenow_instance,
    change_type: Optional[str] = None,
    standard_change_template_id: Optional[str] = None,
    username: str = environment_username,
    password: str = environment_password,
    client_id: Optional[str] = environment_client_id,
    client_secret: Optional[str] = environment_client_secret,
    verify: Optional[bool] = environment_verify,
) -> dict:
    """
    Create a new change request on a ServiceNow instance.

    This tool creates a new change request with the provided details.
    Authentication can be provided via basic auth (username and password) or OAuth (client_id and client_secret).
    At least one authentication method must be configured in the Api client, but validation is handled by the underlying Api.

    Args:
        name_value_pairs (Dict[str, str]): Name-value pairs providing details for the new change request.
        servicenow_instance (str): The URL of the ServiceNow instance (e.g., https://yourinstance.servicenow.com).
        change_type (Optional[str], optional): Type of change (emergency, normal, standard). Defaults to None.
        standard_change_template_id (Optional[str], optional): Sys ID of the standard change request template (if applicable). Defaults to None.
        servicenow_instance (str): The URL of the ServiceNow instance (e.g., https://yourinstance.servicenow.com).
            Will read SERVICENOW_INSTANCE environment variable if none is provided in the function.
        username (Optional[str], optional): Username for basic authentication. Defaults to None.
            Will read USERNAME environment variable if none is provided in the function.
        password (Optional[str], optional): Password for basic authentication. Defaults to None.
            Will read PASSWORD environment variable if none is provided in the function.
        client_id (Optional[str], optional): Client ID for OAuth authentication. Defaults to None.
            Will read CLIENT_ID environment variable if none is provided in the function.
        client_secret (Optional[str], optional): Client secret for OAuth authentication. Defaults to None.
            Will read CLIENT_SECRET environment variable if none is provided in the function.
        verify (Optional[bool], optional): Whether to verify SSL certificates. Defaults to False.
            Will read VERIFY environment variable if none is provided in the function.

    Returns:
        dict: The JSON response containing information about the created change request.

    Raises:
        MissingParameterError: If name_value_pairs is not provided (handled by the Api).
        ParameterError: If invalid parameters or responses are encountered (handled by the Api).
        ParameterError: If change_type is specified but not valid (handled by the Api).
        ParameterError: If JSON serialization or deserialization fails (handled by the Api).
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


@mcp.tool()
def create_change_request_task(
    change_request_sys_id: str,
    data: Dict[str, str],
    servicenow_instance: str = environment_servicenow_instance,
    username: str = environment_username,
    password: str = environment_password,
    client_id: Optional[str] = environment_client_id,
    client_secret: Optional[str] = environment_client_secret,
    verify: Optional[bool] = environment_verify,
) -> dict:
    """
    Create a new task associated with a change request on a ServiceNow instance.

    This tool creates a new task for a change request with the provided details.
    Authentication can be provided via basic auth (username and password) or OAuth (client_id and client_secret).
    At least one authentication method must be configured in the Api client, but validation is handled by the underlying Api.

    Args:
        change_request_sys_id (str): Sys ID of the change request.
        data (Dict[str, str]): Name-value pairs providing details for the new task.
        servicenow_instance (str): The URL of the ServiceNow instance (e.g., https://yourinstance.servicenow.com).
            Will read SERVICENOW_INSTANCE environment variable if none is provided in the function.
        username (Optional[str], optional): Username for basic authentication. Defaults to None.
            Will read USERNAME environment variable if none is provided in the function.
        password (Optional[str], optional): Password for basic authentication. Defaults to None.
            Will read PASSWORD environment variable if none is provided in the function.
        client_id (Optional[str], optional): Client ID for OAuth authentication. Defaults to None.
            Will read CLIENT_ID environment variable if none is provided in the function.
        client_secret (Optional[str], optional): Client secret for OAuth authentication. Defaults to None.
            Will read CLIENT_SECRET environment variable if none is provided in the function.
        verify (Optional[bool], optional): Whether to verify SSL certificates. Defaults to False.
            Will read VERIFY environment variable if none is provided in the function.

    Returns:
        dict: The JSON response containing information about the created task.

    Raises:
        MissingParameterError: If change_request_sys_id or data is not provided (handled by the Api).
        ParameterError: If invalid parameters or responses are encountered (handled by the Api).
        ParameterError: If JSON serialization or deserialization fails (handled by the Api).
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


@mcp.tool()
def create_change_request_ci_association(
    change_request_sys_id: str,
    cmdb_ci_sys_ids: List[str],
    association_type: str,
    servicenow_instance: str = environment_servicenow_instance,
    refresh_impacted_services: Optional[bool] = None,
    username: str = environment_username,
    password: str = environment_password,
    client_id: Optional[str] = environment_client_id,
    client_secret: Optional[str] = environment_client_secret,
    verify: Optional[bool] = environment_verify,
) -> dict:
    """
    Create associations between a change request and configuration items (CIs) on a ServiceNow instance.

    This tool creates associations between a change request and specified CIs.
    Authentication can be provided via basic auth (username and password) or OAuth (client_id and client_secret).
    At least one authentication method must be configured in the Api client, but validation is handled by the underlying Api.

    Args:
        change_request_sys_id (str): Sys ID of the change request.
        cmdb_ci_sys_ids (List[str]): List of Sys IDs of CIs to associate with the change request.
        association_type (str): Type of association (affected, impacted, offering).
        servicenow_instance (str): The URL of the ServiceNow instance (e.g., https://yourinstance.servicenow.com).
        refresh_impacted_services (Optional[bool], optional): Flag to refresh impacted services (applicable for 'affected' association). Defaults to None.
        servicenow_instance (str): The URL of the ServiceNow instance (e.g., https://yourinstance.servicenow.com).
            Will read SERVICENOW_INSTANCE environment variable if none is provided in the function.
        username (Optional[str], optional): Username for basic authentication. Defaults to None.
            Will read USERNAME environment variable if none is provided in the function.
        password (Optional[str], optional): Password for basic authentication. Defaults to None.
            Will read PASSWORD environment variable if none is provided in the function.
        client_id (Optional[str], optional): Client ID for OAuth authentication. Defaults to None.
            Will read CLIENT_ID environment variable if none is provided in the function.
        client_secret (Optional[str], optional): Client secret for OAuth authentication. Defaults to None.
            Will read CLIENT_SECRET environment variable if none is provided in the function.
        verify (Optional[bool], optional): Whether to verify SSL certificates. Defaults to False.
            Will read VERIFY environment variable if none is provided in the function.

    Returns:
        dict: The JSON response containing information about the created associations.

    Raises:
        MissingParameterError: If change_request_sys_id, cmdb_ci_sys_ids, or association_type is not provided (handled by the Api).
        ParameterError: If invalid parameters or responses are encountered (handled by the Api).
        ParameterError: If association_type is not valid (handled by the Api).
        ParameterError: If JSON serialization or deserialization fails (handled by the Api).
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


@mcp.tool()
def calculate_standard_change_request_risk(
    change_request_sys_id: str,
    servicenow_instance: str = environment_servicenow_instance,
    username: str = environment_username,
    password: str = environment_password,
    client_id: Optional[str] = environment_client_id,
    client_secret: Optional[str] = environment_client_secret,
    verify: Optional[bool] = environment_verify,
) -> dict:
    """
    Calculate and update the risk of a standard change request on a ServiceNow instance.

    This tool calculates and updates the risk for a standard change request based on the provided sys_id.
    Authentication can be provided via basic auth (username and password) or OAuth (client_id and client_secret).
    At least one authentication method must be configured in the Api client, but validation is handled by the underlying Api.

    Args:
        change_request_sys_id (str): Sys ID of the standard change request.
        servicenow_instance (str): The URL of the ServiceNow instance (e.g., https://yourinstance.servicenow.com).
            Will read SERVICENOW_INSTANCE environment variable if none is provided in the function.
        username (Optional[str], optional): Username for basic authentication. Defaults to None.
            Will read USERNAME environment variable if none is provided in the function.
        password (Optional[str], optional): Password for basic authentication. Defaults to None.
            Will read PASSWORD environment variable if none is provided in the function.
        client_id (Optional[str], optional): Client ID for OAuth authentication. Defaults to None.
            Will read CLIENT_ID environment variable if none is provided in the function.
        client_secret (Optional[str], optional): Client secret for OAuth authentication. Defaults to None.
            Will read CLIENT_SECRET environment variable if none is provided in the function.
        verify (Optional[bool], optional): Whether to verify SSL certificates. Defaults to False.
            Will read VERIFY environment variable if none is provided in the function.

    Returns:
        dict: The JSON response containing information about the calculated risk.

    Raises:
        MissingParameterError: If change_request_sys_id is not provided (handled by the Api).
        ParameterError: If invalid parameters or responses are encountered (handled by the Api).
        ParameterError: If JSON deserialization fails (handled by the Api).
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


@mcp.tool()
def check_change_request_conflict(
    change_request_sys_id: str,
    servicenow_instance: str = environment_servicenow_instance,
    username: str = environment_username,
    password: str = environment_password,
    client_id: Optional[str] = environment_client_id,
    client_secret: Optional[str] = environment_client_secret,
    verify: Optional[bool] = environment_verify,
) -> dict:
    """
    Check for conflicts in a change request on a ServiceNow instance.

    This tool checks for conflicts in a change request based on the provided sys_id.
    Authentication can be provided via basic auth (username and password) or OAuth (client_id and client_secret).
    At least one authentication method must be configured in the Api client, but validation is handled by the underlying Api.

    Args:
        change_request_sys_id (str): Sys ID of the change request.
        servicenow_instance (str): The URL of the ServiceNow instance (e.g., https://yourinstance.servicenow.com).
            Will read SERVICENOW_INSTANCE environment variable if none is provided in the function.
        username (Optional[str], optional): Username for basic authentication. Defaults to None.
            Will read USERNAME environment variable if none is provided in the function.
        password (Optional[str], optional): Password for basic authentication. Defaults to None.
            Will read PASSWORD environment variable if none is provided in the function.
        client_id (Optional[str], optional): Client ID for OAuth authentication. Defaults to None.
            Will read CLIENT_ID environment variable if none is provided in the function.
        client_secret (Optional[str], optional): Client secret for OAuth authentication. Defaults to None.
            Will read CLIENT_SECRET environment variable if none is provided in the function.
        verify (Optional[bool], optional): Whether to verify SSL certificates. Defaults to False.
            Will read VERIFY environment variable if none is provided in the function.

    Returns:
        dict: The JSON response containing information about conflicts.

    Raises:
        MissingParameterError: If change_request_sys_id is not provided (handled by the Api).
        ParameterError: If invalid parameters or responses are encountered (handled by the Api).
        ParameterError: If JSON deserialization fails (handled by the Api).
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


@mcp.tool()
def refresh_change_request_impacted_services(
    change_request_sys_id: str,
    servicenow_instance: str = environment_servicenow_instance,
    username: str = environment_username,
    password: str = environment_password,
    client_id: Optional[str] = environment_client_id,
    client_secret: Optional[str] = environment_client_secret,
    verify: Optional[bool] = environment_verify,
) -> dict:
    """
    Refresh impacted services for a change request on a ServiceNow instance.

    This tool refreshes impacted services for a change request based on the provided sys_id.
    Authentication can be provided via basic auth (username and password) or OAuth (client_id and client_secret).
    At least one authentication method must be configured in the Api client, but validation is handled by the underlying Api.

    Args:
        change_request_sys_id (str): Sys ID of the change request.
        servicenow_instance (str): The URL of the ServiceNow instance (e.g., https://yourinstance.servicenow.com).
            Will read SERVICENOW_INSTANCE environment variable if none is provided in the function.
        username (Optional[str], optional): Username for basic authentication. Defaults to None.
            Will read USERNAME environment variable if none is provided in the function.
        password (Optional[str], optional): Password for basic authentication. Defaults to None.
            Will read PASSWORD environment variable if none is provided in the function.
        client_id (Optional[str], optional): Client ID for OAuth authentication. Defaults to None.
            Will read CLIENT_ID environment variable if none is provided in the function.
        client_secret (Optional[str], optional): Client secret for OAuth authentication. Defaults to None.
            Will read CLIENT_SECRET environment variable if none is provided in the function.
        verify (Optional[bool], optional): Whether to verify SSL certificates. Defaults to False.
            Will read VERIFY environment variable if none is provided in the function.

    Returns:
        dict: The JSON response containing information about the refreshed impacted services.

    Raises:
        MissingParameterError: If change_request_sys_id is not provided (handled by the Api).
        ParameterError: If invalid parameters or responses are encountered (handled by the Api).
        ParameterError: If JSON deserialization fails (handled by the Api).
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


@mcp.tool()
def approve_change_request(
    change_request_sys_id: str,
    state: str,
    servicenow_instance: str = environment_servicenow_instance,
    username: str = environment_username,
    password: str = environment_password,
    client_id: Optional[str] = environment_client_id,
    client_secret: Optional[str] = environment_client_secret,
    verify: Optional[bool] = environment_verify,
) -> dict:
    """
    Approve or reject a change request on a ServiceNow instance.

    This tool approves or rejects a change request based on the provided sys_id and state.
    Authentication can be provided via basic auth (username and password) or OAuth (client_id and client_secret).
    At least one authentication method must be configured in the Api client, but validation is handled by the underlying Api.

    Args:
        change_request_sys_id (str): Sys ID of the change request.
        state (str): State to set the change request to (approved or rejected).
        servicenow_instance (str): The URL of the ServiceNow instance (e.g., https://yourinstance.servicenow.com).
            Will read SERVICENOW_INSTANCE environment variable if none is provided in the function.
        username (Optional[str], optional): Username for basic authentication. Defaults to None.
            Will read USERNAME environment variable if none is provided in the function.
        password (Optional[str], optional): Password for basic authentication. Defaults to None.
            Will read PASSWORD environment variable if none is provided in the function.
        client_id (Optional[str], optional): Client ID for OAuth authentication. Defaults to None.
            Will read CLIENT_ID environment variable if none is provided in the function.
        client_secret (Optional[str], optional): Client secret for OAuth authentication. Defaults to None.
            Will read CLIENT_SECRET environment variable if none is provided in the function.
        verify (Optional[bool], optional): Whether to verify SSL certificates. Defaults to False.
            Will read VERIFY environment variable if none is provided in the function.

    Returns:
        dict: The JSON response containing information about the approval/rejection.

    Raises:
        MissingParameterError: If change_request_sys_id or state is not provided (handled by the Api).
        ParameterError: If invalid parameters or responses are encountered (handled by the Api).
        ParameterError: If state is not valid (handled by the Api).
        ParameterError: If JSON serialization or deserialization fails (handled by the Api).
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


@mcp.tool()
def update_change_request(
    change_request_sys_id: str,
    name_value_pairs: Dict[str, str],
    servicenow_instance: str = environment_servicenow_instance,
    change_type: Optional[str] = None,
    username: str = environment_username,
    password: str = environment_password,
    client_id: Optional[str] = environment_client_id,
    client_secret: Optional[str] = environment_client_secret,
    verify: Optional[bool] = environment_verify,
) -> dict:
    """
    Update details of a change request on a ServiceNow instance.

    This tool updates a change request with the provided details and optional change type.
    Authentication can be provided via basic auth (username and password) or OAuth (client_id and client_secret).
    At least one authentication method must be configured in the Api client, but validation is handled by the underlying Api.

    Args:
        change_request_sys_id (str): Sys ID of the change request.
        name_value_pairs (Dict[str, str]): New name-value pairs providing updated details for the change request.
        servicenow_instance (str): The URL of the ServiceNow instance (e.g., https://yourinstance.servicenow.com).
        change_type (Optional[str], optional): Type of change (emergency, normal, standard, model). Defaults to None.
        servicenow_instance (str): The URL of the ServiceNow instance (e.g., https://yourinstance.servicenow.com).
            Will read SERVICENOW_INSTANCE environment variable if none is provided in the function.
        username (Optional[str], optional): Username for basic authentication. Defaults to None.
            Will read USERNAME environment variable if none is provided in the function.
        password (Optional[str], optional): Password for basic authentication. Defaults to None.
            Will read PASSWORD environment variable if none is provided in the function.
        client_id (Optional[str], optional): Client ID for OAuth authentication. Defaults to None.
            Will read CLIENT_ID environment variable if none is provided in the function.
        client_secret (Optional[str], optional): Client secret for OAuth authentication. Defaults to None.
            Will read CLIENT_SECRET environment variable if none is provided in the function.
        verify (Optional[bool], optional): Whether to verify SSL certificates. Defaults to False.
            Will read VERIFY environment variable if none is provided in the function.

    Returns:
        dict: The JSON response containing information about the updated change request.

    Raises:
        MissingParameterError: If change_request_sys_id or name_value_pairs is not provided (handled by the Api).
        ParameterError: If invalid parameters or responses are encountered (handled by the Api).
        ParameterError: If change_type is specified but not valid (handled by the Api).
        ParameterError: If JSON serialization or deserialization fails (handled by the Api).
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


@mcp.tool()
def update_change_request_first_available(
    change_request_sys_id: str,
    servicenow_instance: str = environment_servicenow_instance,
    username: str = environment_username,
    password: str = environment_password,
    client_id: Optional[str] = environment_client_id,
    client_secret: Optional[str] = environment_client_secret,
    verify: Optional[bool] = environment_verify,
) -> dict:
    """
    Update the schedule of a change request to the first available slot on a ServiceNow instance.

    This tool updates the schedule of a change request based on the provided sys_id.
    Authentication can be provided via basic auth (username and password) or OAuth (client_id and client_secret).
    At least one authentication method must be configured in the Api client, but validation is handled by the underlying Api.

    Args:
        change_request_sys_id (str): Sys ID of the change request.
        servicenow_instance (str): The URL of the ServiceNow instance (e.g., https://yourinstance.servicenow.com).
            Will read SERVICENOW_INSTANCE environment variable if none is provided in the function.
        username (Optional[str], optional): Username for basic authentication. Defaults to None.
            Will read USERNAME environment variable if none is provided in the function.
        password (Optional[str], optional): Password for basic authentication. Defaults to None.
            Will read PASSWORD environment variable if none is provided in the function.
        client_id (Optional[str], optional): Client ID for OAuth authentication. Defaults to None.
            Will read CLIENT_ID environment variable if none is provided in the function.
        client_secret (Optional[str], optional): Client secret for OAuth authentication. Defaults to None.
            Will read CLIENT_SECRET environment variable if none is provided in the function.
        verify (Optional[bool], optional): Whether to verify SSL certificates. Defaults to False.
            Will read VERIFY environment variable if none is provided in the function.

    Returns:
        dict: The JSON response containing information about the updated schedule.

    Raises:
        MissingParameterError: If change_request_sys_id is not provided (handled by the Api).
        ParameterError: If invalid parameters or responses are encountered (handled by the Api).
        ParameterError: If JSON deserialization fails (handled by the Api).
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


@mcp.tool()
def update_change_request_task(
    change_request_sys_id: str,
    change_request_task_sys_id: str,
    name_value_pairs: Dict[str, str],
    servicenow_instance: str = environment_servicenow_instance,
    username: str = environment_username,
    password: str = environment_password,
    client_id: Optional[str] = environment_client_id,
    client_secret: Optional[str] = environment_client_secret,
    verify: Optional[bool] = environment_verify,
) -> dict:
    """
    Update details of a task associated with a change request on a ServiceNow instance.

    This tool updates a change request task with the provided details.
    Authentication can be provided via basic auth (username and password) or OAuth (client_id and client_secret).
    At least one authentication method must be configured in the Api client, but validation is handled by the underlying Api.

    Args:
        change_request_sys_id (str): Sys ID of the change request.
        change_request_task_sys_id (str): Sys ID of the change request task.
        name_value_pairs (Dict[str, str]): New name-value pairs providing updated details for the task.
        servicenow_instance (str): The URL of the ServiceNow instance (e.g., https://yourinstance.servicenow.com).
            Will read SERVICENOW_INSTANCE environment variable if none is provided in the function.
        username (Optional[str], optional): Username for basic authentication. Defaults to None.
            Will read USERNAME environment variable if none is provided in the function.
        password (Optional[str], optional): Password for basic authentication. Defaults to None.
            Will read PASSWORD environment variable if none is provided in the function.
        client_id (Optional[str], optional): Client ID for OAuth authentication. Defaults to None.
            Will read CLIENT_ID environment variable if none is provided in the function.
        client_secret (Optional[str], optional): Client secret for OAuth authentication. Defaults to None.
            Will read CLIENT_SECRET environment variable if none is provided in the function.
        verify (Optional[bool], optional): Whether to verify SSL certificates. Defaults to False.
            Will read VERIFY environment variable if none is provided in the function.

    Returns:
        dict: The JSON response containing information about the updated task.

    Raises:
        MissingParameterError: If change_request_sys_id, change_request_task_sys_id, or name_value_pairs is not provided (handled by the Api).
        ParameterError: If invalid parameters or responses are encountered (handled by the Api).
        ParameterError: If JSON serialization or deserialization fails (handled by the Api).
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


@mcp.tool()
def delete_change_request(
    change_request_sys_id: str,
    servicenow_instance: str = environment_servicenow_instance,
    change_type: Optional[str] = None,
    username: str = environment_username,
    password: str = environment_password,
    client_id: Optional[str] = environment_client_id,
    client_secret: Optional[str] = environment_client_secret,
    verify: Optional[bool] = environment_verify,
) -> dict:
    """
    Delete a change request from a ServiceNow instance.

    This tool deletes a change request based on the provided sys_id and optional change type.
    Authentication can be provided via basic auth (username and password) or OAuth (client_id and client_secret).
    At least one authentication method must be configured in the Api client, but validation is handled by the underlying Api.

    Args:
        change_request_sys_id (str): Sys ID of the change request.
        servicenow_instance (str): The URL of the ServiceNow instance (e.g., https://yourinstance.servicenow.com).
        change_type (Optional[str], optional): Type of change (emergency, normal, standard). Defaults to None.
        servicenow_instance (str): The URL of the ServiceNow instance (e.g., https://yourinstance.servicenow.com).
            Will read SERVICENOW_INSTANCE environment variable if none is provided in the function.
        username (Optional[str], optional): Username for basic authentication. Defaults to None.
            Will read USERNAME environment variable if none is provided in the function.
        password (Optional[str], optional): Password for basic authentication. Defaults to None.
            Will read PASSWORD environment variable if none is provided in the function.
        client_id (Optional[str], optional): Client ID for OAuth authentication. Defaults to None.
            Will read CLIENT_ID environment variable if none is provided in the function.
        client_secret (Optional[str], optional): Client secret for OAuth authentication. Defaults to None.
            Will read CLIENT_SECRET environment variable if none is provided in the function.
        verify (Optional[bool], optional): Whether to verify SSL certificates. Defaults to False.
            Will read VERIFY environment variable if none is provided in the function.

    Returns:
        dict: The JSON response containing information about the deleted change request.

    Raises:
        MissingParameterError: If change_request_sys_id is not provided (handled by the Api).
        ParameterError: If invalid parameters or responses are encountered (handled by the Api).
        ParameterError: If JSON deserialization fails (handled by the Api).
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


@mcp.tool()
def delete_change_request_task(
    change_request_sys_id: str,
    task_sys_id: str,
    servicenow_instance: str = environment_servicenow_instance,
    username: str = environment_username,
    password: str = environment_password,
    client_id: Optional[str] = environment_client_id,
    client_secret: Optional[str] = environment_client_secret,
    verify: Optional[bool] = environment_verify,
) -> dict:
    """
    Delete a task associated with a change request on a ServiceNow instance.

    This tool deletes a task associated with a change request based on the provided sys_ids.
    Authentication can be provided via basic auth (username and password) or OAuth (client_id and client_secret).
    At least one authentication method must be configured in the Api client, but validation is handled by the underlying Api.

    Args:
        change_request_sys_id (str): Sys ID of the change request.
        task_sys_id (str): Sys ID of the task associated with the change request.
        servicenow_instance (str): The URL of the ServiceNow instance (e.g., https://yourinstance.servicenow.com).
            Will read SERVICENOW_INSTANCE environment variable if none is provided in the function.
        username (Optional[str], optional): Username for basic authentication. Defaults to None.
            Will read USERNAME environment variable if none is provided in the function.
        password (Optional[str], optional): Password for basic authentication. Defaults to None.
            Will read PASSWORD environment variable if none is provided in the function.
        client_id (Optional[str], optional): Client ID for OAuth authentication. Defaults to None.
            Will read CLIENT_ID environment variable if none is provided in the function.
        client_secret (Optional[str], optional): Client secret for OAuth authentication. Defaults to None.
            Will read CLIENT_SECRET environment variable if none is provided in the function.
        verify (Optional[bool], optional): Whether to verify SSL certificates. Defaults to False.
            Will read VERIFY environment variable if none is provided in the function.

    Returns:
        dict: The JSON response containing information about the deleted task.

    Raises:
        MissingParameterError: If change_request_sys_id or task_sys_id is not provided (handled by the Api).
        ParameterError: If invalid parameters or responses are encountered (handled by the Api).
        ParameterError: If JSON deserialization fails (handled by the Api).
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


@mcp.tool()
def delete_change_request_conflict_scan(
    change_request_sys_id: str,
    task_sys_id: str,
    servicenow_instance: str = environment_servicenow_instance,
    username: str = environment_username,
    password: str = environment_password,
    client_id: Optional[str] = environment_client_id,
    client_secret: Optional[str] = environment_client_secret,
    verify: Optional[bool] = environment_verify,
) -> dict:
    """
    Delete conflict scan information associated with a change request on a ServiceNow instance.

    This tool deletes conflict scan information for a change request based on the provided sys_ids.
    Authentication can be provided via basic auth (username and password) or OAuth (client_id and client_secret).
    At least one authentication method must be configured in the Api client, but validation is handled by the underlying Api.

    Args:
        change_request_sys_id (str): Sys ID of the change request.
        task_sys_id (str): Sys ID of the task associated with the change request.
        servicenow_instance (str): The URL of the ServiceNow instance (e.g., https://yourinstance.servicenow.com).
            Will read SERVICENOW_INSTANCE environment variable if none is provided in the function.
        username (Optional[str], optional): Username for basic authentication. Defaults to None.
            Will read USERNAME environment variable if none is provided in the function.
        password (Optional[str], optional): Password for basic authentication. Defaults to None.
            Will read PASSWORD environment variable if none is provided in the function.
        client_id (Optional[str], optional): Client ID for OAuth authentication. Defaults to None.
            Will read CLIENT_ID environment variable if none is provided in the function.
        client_secret (Optional[str], optional): Client secret for OAuth authentication. Defaults to None.
            Will read CLIENT_SECRET environment variable if none is provided in the function.
        verify (Optional[bool], optional): Whether to verify SSL certificates. Defaults to False.
            Will read VERIFY environment variable if none is provided in the function.

    Returns:
        dict: The JSON response containing information about the deleted conflict scan.

    Raises:
        MissingParameterError: If change_request_sys_id or task_sys_id is not provided (handled by the Api).
        ParameterError: If invalid parameters or responses are encountered (handled by the Api).
        ParameterError: If JSON deserialization fails (handled by the Api).
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
@mcp.tool()
def get_import_set(
    table: str,
    import_set_sys_id: str,
    servicenow_instance: str = environment_servicenow_instance,
    username: str = environment_username,
    password: str = environment_password,
    client_id: Optional[str] = environment_client_id,
    client_secret: Optional[str] = environment_client_secret,
    verify: Optional[bool] = environment_verify,
) -> dict:
    """
    Get details of a specific import set record from a ServiceNow instance.

    This tool retrieves details of an import set record based on the provided table and sys_id.
    Authentication can be provided via basic auth (username and password) or OAuth (client_id and client_secret).
    At least one authentication method must be configured in the Api client, but validation is handled by the underlying Api.

    Args:
        table (str): The name of the table associated with the import set.
        import_set_sys_id (str): The sys_id of the import set record.
        servicenow_instance (str): The URL of the ServiceNow instance (e.g., https://yourinstance.servicenow.com).
            Will read SERVICENOW_INSTANCE environment variable if none is provided in the function.
        username (Optional[str], optional): Username for basic authentication. Defaults to None.
            Will read USERNAME environment variable if none is provided in the function.
        password (Optional[str], optional): Password for basic authentication. Defaults to None.
            Will read PASSWORD environment variable if none is provided in the function.
        client_id (Optional[str], optional): Client ID for OAuth authentication. Defaults to None.
            Will read CLIENT_ID environment variable if none is provided in the function.
        client_secret (Optional[str], optional): Client secret for OAuth authentication. Defaults to None.
            Will read CLIENT_SECRET environment variable if none is provided in the function.
        verify (Optional[bool], optional): Whether to verify SSL certificates. Defaults to False.
            Will read VERIFY environment variable if none is provided in the function.

    Returns:
        dict: The JSON response containing information about the import set record.

    Raises:
        ParameterError: If import_set_sys_id or table is not provided (handled by the Api).
        ParameterError: If invalid parameters or responses are encountered (handled by the Api).
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


@mcp.tool()
def insert_import_set(
    table: str,
    data: Dict[str, str],
    servicenow_instance: str = environment_servicenow_instance,
    username: str = environment_username,
    password: str = environment_password,
    client_id: Optional[str] = environment_client_id,
    client_secret: Optional[str] = environment_client_secret,
    verify: Optional[bool] = environment_verify,
) -> dict:
    """
    Insert a new record into the specified import set on a ServiceNow instance.

    This tool inserts a new record into the specified import set with the provided data.
    Authentication can be provided via basic auth (username and password) or OAuth (client_id and client_secret).
    At least one authentication method must be configured in the Api client, but validation is handled by the underlying Api.

    Args:
        table (str): The name of the table associated with the import set.
        data (Dict[str, str]): Dictionary containing the field values for the new import set record.
        servicenow_instance (str): The URL of the ServiceNow instance (e.g., https://yourinstance.servicenow.com).
            Will read SERVICENOW_INSTANCE environment variable if none is provided in the function.
        username (Optional[str], optional): Username for basic authentication. Defaults to None.
            Will read USERNAME environment variable if none is provided in the function.
        password (Optional[str], optional): Password for basic authentication. Defaults to None.
            Will read PASSWORD environment variable if none is provided in the function.
        client_id (Optional[str], optional): Client ID for OAuth authentication. Defaults to None.
            Will read CLIENT_ID environment variable if none is provided in the function.
        client_secret (Optional[str], optional): Client secret for OAuth authentication. Defaults to None.
            Will read CLIENT_SECRET environment variable if none is provided in the function.
        verify (Optional[bool], optional): Whether to verify SSL certificates. Defaults to False.
            Will read VERIFY environment variable if none is provided in the function.

    Returns:
        dict: The JSON response containing information about the inserted import set record.

    Raises:
        ParameterError: If data or table is not provided (handled by the Api).
        ParameterError: If JSON serialization fails (handled by the Api).
        ParameterError: If invalid parameters or responses are encountered (handled by the Api).
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


@mcp.tool()
def insert_multiple_import_sets(
    table: str,
    data: Dict[str, str],
    servicenow_instance: str = environment_servicenow_instance,
    username: str = environment_username,
    password: str = environment_password,
    client_id: Optional[str] = environment_client_id,
    client_secret: Optional[str] = environment_client_secret,
    verify: Optional[bool] = environment_verify,
) -> dict:
    """
    Insert multiple records into the specified import set on a ServiceNow instance.

    This tool inserts multiple records into the specified import set with the provided data.
    Authentication can be provided via basic auth (username and password) or OAuth (client_id and client_secret).
    At least one authentication method must be configured in the Api client, but validation is handled by the underlying Api.

    Args:
        table (str): The name of the table associated with the import set.
        data (Dict[str, str]): Dictionary containing the field values for multiple new import set records.
        servicenow_instance (str): The URL of the ServiceNow instance (e.g., https://yourinstance.servicenow.com).
            Will read SERVICENOW_INSTANCE environment variable if none is provided in the function.
        username (Optional[str], optional): Username for basic authentication. Defaults to None.
            Will read USERNAME environment variable if none is provided in the function.
        password (Optional[str], optional): Password for basic authentication. Defaults to None.
            Will read PASSWORD environment variable if none is provided in the function.
        client_id (Optional[str], optional): Client ID for OAuth authentication. Defaults to None.
            Will read CLIENT_ID environment variable if none is provided in the function.
        client_secret (Optional[str], optional): Client secret for OAuth authentication. Defaults to None.
            Will read CLIENT_SECRET environment variable if none is provided in the function.
        verify (Optional[bool], optional): Whether to verify SSL certificates. Defaults to False.
            Will read VERIFY environment variable if none is provided in the function.

    Returns:
        dict: The JSON response containing information about the inserted import set records.

    Raises:
        ParameterError: If data or table is not provided (handled by the Api).
        ParameterError: If JSON serialization fails (handled by the Api).
        ParameterError: If invalid parameters or responses are encountered (handled by the Api).
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
@mcp.tool()
def get_incident(
    incident_id: str,
    servicenow_instance: str = environment_servicenow_instance,
    username: str = environment_username,
    password: str = environment_password,
    client_id: Optional[str] = environment_client_id,
    client_secret: Optional[str] = environment_client_secret,
    verify: Optional[bool] = environment_verify,
) -> dict:
    """
    Retrieve details of a specific incident record from a ServiceNow instance.

    This tool retrieves details of an incident record based on the provided incident_id.
    Authentication can be provided via basic auth (username and password) or OAuth (client_id and client_secret).
    At least one authentication method must be configured in the Api client, but validation is handled by the underlying Api.

    Args:
        incident_id (str): The sys_id of the incident record.
        servicenow_instance (str): The URL of the ServiceNow instance (e.g., https://yourinstance.servicenow.com).
            Will read SERVICENOW_INSTANCE environment variable if none is provided in the function.
        username (Optional[str], optional): Username for basic authentication. Defaults to None.
            Will read USERNAME environment variable if none is provided in the function.
        password (Optional[str], optional): Password for basic authentication. Defaults to None.
            Will read PASSWORD environment variable if none is provided in the function.
        client_id (Optional[str], optional): Client ID for OAuth authentication. Defaults to None.
            Will read CLIENT_ID environment variable if none is provided in the function.
        client_secret (Optional[str], optional): Client secret for OAuth authentication. Defaults to None.
            Will read CLIENT_SECRET environment variable if none is provided in the function.
        verify (Optional[bool], optional): Whether to verify SSL certificates. Defaults to False.
            Will read VERIFY environment variable if none is provided in the function.

    Returns:
        dict: The JSON response containing information about the incident record.

    Raises:
        MissingParameterError: If incident_id is not provided (handled by the Api).
        ParameterError: If invalid parameters or responses are encountered (handled by the Api).
    """
    client = Api(
        url=servicenow_instance,
        username=username,
        password=password,
        client_id=client_id,
        client_secret=client_secret,
        verify=verify,
    )
    response = client.get_incident(incident_id=incident_id)
    return response.result


@mcp.tool()
def create_incident(
    data: Dict[str, str],
    servicenow_instance: str = environment_servicenow_instance,
    username: str = environment_username,
    password: str = environment_password,
    client_id: Optional[str] = environment_client_id,
    client_secret: Optional[str] = environment_client_secret,
    verify: Optional[bool] = environment_verify,
) -> dict:
    """
    Create a new incident record on a ServiceNow instance.

    This tool creates a new incident record with the provided data.
    Authentication can be provided via basic auth (username and password) or OAuth (client_id and client_secret).
    At least one authentication method must be configured in the Api client, but validation is handled by the underlying Api.

    Args:
        data (Dict[str, str]): Dictionary containing the field values for the new incident record.
        servicenow_instance (str): The URL of the ServiceNow instance (e.g., https://yourinstance.servicenow.com).
            Will read SERVICENOW_INSTANCE environment variable if none is provided in the function.
        username (Optional[str], optional): Username for basic authentication. Defaults to None.
            Will read USERNAME environment variable if none is provided in the function.
        password (Optional[str], optional): Password for basic authentication. Defaults to None.
            Will read PASSWORD environment variable if none is provided in the function.
        client_id (Optional[str], optional): Client ID for OAuth authentication. Defaults to None.
            Will read CLIENT_ID environment variable if none is provided in the function.
        client_secret (Optional[str], optional): Client secret for OAuth authentication. Defaults to None.
            Will read CLIENT_SECRET environment variable if none is provided in the function.
        verify (Optional[bool], optional): Whether to verify SSL certificates. Defaults to False.
            Will read VERIFY environment variable if none is provided in the function.

    Returns:
        dict: The JSON response containing information about the created incident record.

    Raises:
        MissingParameterError: If data is not provided (handled by the Api).
        ParameterError: If JSON serialization fails (handled by the Api).
        ParameterError: If invalid parameters or responses are encountered (handled by the Api).
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
@mcp.tool()
def get_knowledge_articles(
    servicenow_instance: str = environment_servicenow_instance,
    filter: Optional[str] = None,
    sysparm_fields: Optional[str] = None,
    sysparm_limit: Optional[int] = None,
    sysparm_offset: Optional[int] = None,
    sysparm_query: Optional[str] = None,
    sysparm_query_category: Optional[str] = None,
    kb: Optional[str] = None,
    language: Optional[str] = None,
    username: str = environment_username,
    password: str = environment_password,
    client_id: Optional[str] = environment_client_id,
    client_secret: Optional[str] = environment_client_secret,
    verify: Optional[bool] = environment_verify,
) -> dict:
    """
    Get all Knowledge Base articles from a ServiceNow instance.

    This tool retrieves Knowledge Base articles based on specified parameters.
    Authentication can be provided via basic auth (username and password) or OAuth (client_id and client_secret).
    At least one authentication method must be configured in the Api client, but validation is handled by the underlying Api.

    Args:
        filter (Optional[str], optional): Encoded query to filter the result set (e.g., =, !=, ^, ^OR, LIKE, STARTSWITH, ENDSWITH). Defaults to None.
        sysparm_fields (Optional[str], optional): Comma-separated list of field names to include in the response. Defaults to None.
        sysparm_limit (Optional[int], optional): Maximum number of records to return. Defaults to None.
        sysparm_offset (Optional[int], optional): Number of records to skip before starting the retrieval. Defaults to None.
        sysparm_query (Optional[str], optional): Encoded query string for filtering records. Defaults to None.
        sysparm_query_category (Optional[str], optional): Category to which the query belongs. Defaults to None.
        kb (Optional[str], optional): Comma-separated list of knowledge base sys_ids to restrict results to. Defaults to None.
        language (Optional[str], optional): Comma-separated languages in ISO 639-1 format or 'all' to search all valid languages. Defaults to None.
        servicenow_instance (str): The URL of the ServiceNow instance (e.g., https://yourinstance.servicenow.com).
            Will read SERVICENOW_INSTANCE environment variable if none is provided in the function.
        username (Optional[str], optional): Username for basic authentication. Defaults to None.
            Will read USERNAME environment variable if none is provided in the function.
        password (Optional[str], optional): Password for basic authentication. Defaults to None.
            Will read PASSWORD environment variable if none is provided in the function.
        client_id (Optional[str], optional): Client ID for OAuth authentication. Defaults to None.
            Will read CLIENT_ID environment variable if none is provided in the function.
        client_secret (Optional[str], optional): Client secret for OAuth authentication. Defaults to None.
            Will read CLIENT_SECRET environment variable if none is provided in the function.
        verify (Optional[bool], optional): Whether to verify SSL certificates. Defaults to False.
            Will read VERIFY environment variable if none is provided in the function.

    Returns:
        dict: The JSON response containing information about the retrieved records.

    Raises:
        MissingParameterError: If required parameters are not provided (handled by the Api).
        ParameterError: If input parameters are invalid (handled by the Api).
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


@mcp.tool()
def get_knowledge_article(
    article_sys_id: str,
    servicenow_instance: str = environment_servicenow_instance,
    filter: Optional[str] = None,
    sysparm_fields: Optional[str] = None,
    sysparm_limit: Optional[int] = None,
    sysparm_search_id: Optional[str] = None,
    sysparm_search_rank: Optional[str] = None,
    sysparm_update_view: Optional[bool] = None,
    sysparm_offset: Optional[int] = None,
    sysparm_query: Optional[str] = None,
    sysparm_query_category: Optional[str] = None,
    kb: Optional[str] = None,
    language: Optional[str] = None,
    username: str = environment_username,
    password: str = environment_password,
    client_id: Optional[str] = environment_client_id,
    client_secret: Optional[str] = environment_client_secret,
    verify: Optional[bool] = environment_verify,
) -> dict:
    """
    Get a specific Knowledge Base article from a ServiceNow instance.

    This tool retrieves a Knowledge Base article based on the provided article_sys_id and optional parameters.
    Authentication can be provided via basic auth (username and password) or OAuth (client_id and client_secret).
    At least one authentication method must be configured in the Api client, but validation is handled by the underlying Api.

    Args:
        article_sys_id (str): The sys_id of the Knowledge Base article.
        filter (Optional[str], optional): Encoded query to filter the result set (e.g., =, !=, ^, ^OR, LIKE, STARTSWITH, ENDSWITH). Defaults to None.
        sysparm_fields (Optional[str], optional): Comma-separated list of field names to include in the response. Defaults to None.
        sysparm_limit (Optional[int], optional): Maximum number of records to return. Defaults to None.
        sysparm_search_id (Optional[str], optional): Unique identifier of search that returned this article. Defaults to None.
        sysparm_search_rank (Optional[str], optional): Article search rank by click-rate. Defaults to None.
        sysparm_update_view (Optional[bool], optional): Update view count and record an entry in the Knowledge Use table. Defaults to None.
        sysparm_offset (Optional[int], optional): Number of records to skip before starting the retrieval. Defaults to None.
        sysparm_query (Optional[str], optional): Encoded query string for filtering records. Defaults to None.
        sysparm_query_category (Optional[str], optional): Category to which the query belongs. Defaults to None.
        kb (Optional[str], optional): Comma-separated list of knowledge base sys_ids to restrict results to. Defaults to None.
        language (Optional[str], optional): Comma-separated languages in ISO 639-1 format or 'all' to search all valid languages. Defaults to None.
        servicenow_instance (str): The URL of the ServiceNow instance (e.g., https://yourinstance.servicenow.com).
            Will read SERVICENOW_INSTANCE environment variable if none is provided in the function.
        username (Optional[str], optional): Username for basic authentication. Defaults to None.
            Will read USERNAME environment variable if none is provided in the function.
        password (Optional[str], optional): Password for basic authentication. Defaults to None.
            Will read PASSWORD environment variable if none is provided in the function.
        client_id (Optional[str], optional): Client ID for OAuth authentication. Defaults to None.
            Will read CLIENT_ID environment variable if none is provided in the function.
        client_secret (Optional[str], optional): Client secret for OAuth authentication. Defaults to None.
            Will read CLIENT_SECRET environment variable if none is provided in the function.
        verify (Optional[bool], optional): Whether to verify SSL certificates. Defaults to False.
            Will read VERIFY environment variable if none is provided in the function.

    Returns:
        dict: The JSON response containing information about the retrieved article.

    Raises:
        MissingParameterError: If article_sys_id is not provided (handled by the Api).
        ParameterError: If input parameters are invalid (handled by the Api).
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


@mcp.tool()
def get_knowledge_article_attachment(
    article_sys_id: str,
    attachment_sys_id: str,
    servicenow_instance: str = environment_servicenow_instance,
    username: str = environment_username,
    password: str = environment_password,
    client_id: Optional[str] = environment_client_id,
    client_secret: Optional[str] = environment_client_secret,
    verify: Optional[bool] = environment_verify,
) -> dict:
    """
    Get a Knowledge Base article attachment from a ServiceNow instance.

    This tool retrieves an attachment for a specific Knowledge Base article based on the provided sys_ids.
    Authentication can be provided via basic auth (username and password) or OAuth (client_id and client_secret).
    At least one authentication method must be configured in the Api client, but validation is handled by the underlying Api.

    Args:
        article_sys_id (str): The sys_id of the Knowledge Base article.
        attachment_sys_id (str): The sys_id of the attachment.
        servicenow_instance (str): The URL of the ServiceNow instance (e.g., https://yourinstance.servicenow.com).
            Will read SERVICENOW_INSTANCE environment variable if none is provided in the function.
        username (Optional[str], optional): Username for basic authentication. Defaults to None.
            Will read USERNAME environment variable if none is provided in the function.
        password (Optional[str], optional): Password for basic authentication. Defaults to None.
            Will read PASSWORD environment variable if none is provided in the function.
        client_id (Optional[str], optional): Client ID for OAuth authentication. Defaults to None.
            Will read CLIENT_ID environment variable if none is provided in the function.
        client_secret (Optional[str], optional): Client secret for OAuth authentication. Defaults to None.
            Will read CLIENT_SECRET environment variable if none is provided in the function.
        verify (Optional[bool], optional): Whether to verify SSL certificates. Defaults to False.
            Will read VERIFY environment variable if none is provided in the function.

    Returns:
        dict: The JSON response containing information about the retrieved attachment.

    Raises:
        MissingParameterError: If article_sys_id or attachment_sys_id is not provided (handled by the Api).
        ParameterError: If input parameters are invalid (handled by the Api).
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


@mcp.tool()
def get_featured_knowledge_article(
    servicenow_instance: str = environment_servicenow_instance,
    sysparm_fields: Optional[str] = None,
    sysparm_limit: Optional[int] = None,
    sysparm_offset: Optional[int] = None,
    kb: Optional[str] = None,
    language: Optional[str] = None,
    username: Optional[str] = None,
    password: Optional[str] = None,
    client_id: Optional[str] = None,
    client_secret: Optional[str] = None,
    verify: Optional[bool] = None,
) -> dict:
    """
    Get featured Knowledge Base articles from a ServiceNow instance.

    This tool retrieves featured Knowledge Base articles based on specified parameters.
    Authentication can be provided via basic auth (username and password) or OAuth (client_id and client_secret).
    At least one authentication method must be configured in the Api client, but validation is handled by the underlying Api.

    Args:
        servicenow_instance (str): The URL of the ServiceNow instance (e.g., https://yourinstance.servicenow.com).
        sysparm_fields (Optional[str], optional): Comma-separated list of field names to include in the response. Defaults to None.
        sysparm_limit (Optional[int], optional): Maximum number of records to return. Defaults to None.
        sysparm_offset (Optional[int], optional): Number of records to skip before starting the retrieval. Defaults to None.
        kb (Optional[str], optional): Comma-separated list of knowledge base sys_ids to restrict results to. Defaults to None.
        language (Optional[str], optional): Comma-separated languages in ISO 639-1 format or 'all' to search all valid languages. Defaults to None.
        username (Optional[str], optional): Username for basic authentication. Defaults to None.
        password (Optional[str], optional): Password for basic authentication. Defaults to None.
        client_id (Optional[str], optional): Client ID for OAuth authentication. Defaults to None.
        client_secret (Optional[str], optional): Client secret for OAuth authentication. Defaults to None.
        verify (Optional[bool], optional): Whether to verify SSL certificates. Defaults to None.

    Returns:
        dict: The JSON response containing information about the retrieved featured articles.

    Raises:
        MissingParameterError: If required parameters are not provided (handled by the Api).
        ParameterError: If input parameters are invalid (handled by the Api).
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


@mcp.tool()
def get_most_viewed_knowledge_articles(
    servicenow_instance: str = environment_servicenow_instance,
    sysparm_fields: Optional[str] = None,
    sysparm_limit: Optional[int] = None,
    sysparm_offset: Optional[int] = None,
    kb: Optional[str] = None,
    language: Optional[str] = None,
    username: str = environment_username,
    password: str = environment_password,
    client_id: Optional[str] = environment_client_id,
    client_secret: Optional[str] = environment_client_secret,
    verify: Optional[bool] = environment_verify,
) -> dict:
    """
    Get most viewed Knowledge Base articles from a ServiceNow instance.

    This tool retrieves the most viewed Knowledge Base articles based on specified parameters.
    Authentication can be provided via basic auth (username and password) or OAuth (client_id and client_secret).
    At least one authentication method must be configured in the Api client, but validation is handled by the underlying Api.

    Args:
        sysparm_fields (Optional[str], optional): Comma-separated list of field names to include in the response. Defaults to None.
        sysparm_limit (Optional[int], optional): Maximum number of records to return. Defaults to None.
        sysparm_offset (Optional[int], optional): Number of records to skip before starting the retrieval. Defaults to None.
        kb (Optional[str], optional): Comma-separated list of knowledge base sys_ids to restrict results to. Defaults to None.
        language (Optional[str], optional): Comma-separated languages in ISO 639-1 format or 'all' to search all valid languages. Defaults to None.
        servicenow_instance (str): The URL of the ServiceNow instance (e.g., https://yourinstance.servicenow.com).
            Will read SERVICENOW_INSTANCE environment variable if none is provided in the function.
        username (Optional[str], optional): Username for basic authentication. Defaults to None.
            Will read USERNAME environment variable if none is provided in the function.
        password (Optional[str], optional): Password for basic authentication. Defaults to None.
            Will read PASSWORD environment variable if none is provided in the function.
        client_id (Optional[str], optional): Client ID for OAuth authentication. Defaults to None.
            Will read CLIENT_ID environment variable if none is provided in the function.
        client_secret (Optional[str], optional): Client secret for OAuth authentication. Defaults to None.
            Will read CLIENT_SECRET environment variable if none is provided in the function.
        verify (Optional[bool], optional): Whether to verify SSL certificates. Defaults to False.
            Will read VERIFY environment variable if none is provided in the function.

    Returns:
        dict: The JSON response containing information about the most viewed articles.

    Raises:
        MissingParameterError: If required parameters are not provided (handled by the Api).
        ParameterError: If input parameters are invalid (handled by the Api).
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
@mcp.tool()
def delete_table_record(
    table: str,
    table_record_sys_id: str,
    servicenow_instance: str = environment_servicenow_instance,
    username: str = environment_username,
    password: str = environment_password,
    client_id: Optional[str] = environment_client_id,
    client_secret: Optional[str] = environment_client_secret,
    verify: Optional[bool] = environment_verify,
) -> dict:
    """
    Delete a record from the specified table on a ServiceNow instance.

    This tool deletes a record from the specified table based on the provided table name and record sys_id.
    Authentication can be provided via basic auth (username and password) or OAuth (client_id and client_secret).
    At least one authentication method must be configured in the Api client, but validation is handled by the underlying Api.

    Args:
        table (str): The name of the table.
        table_record_sys_id (str): The sys_id of the record to be deleted.
        servicenow_instance (str): The URL of the ServiceNow instance (e.g., https://yourinstance.servicenow.com).
            Will read SERVICENOW_INSTANCE environment variable if none is provided in the function.
        username (Optional[str], optional): Username for basic authentication. Defaults to None.
            Will read USERNAME environment variable if none is provided in the function.
        password (Optional[str], optional): Password for basic authentication. Defaults to None.
            Will read PASSWORD environment variable if none is provided in the function.
        client_id (Optional[str], optional): Client ID for OAuth authentication. Defaults to None.
            Will read CLIENT_ID environment variable if none is provided in the function.
        client_secret (Optional[str], optional): Client secret for OAuth authentication. Defaults to None.
            Will read CLIENT_SECRET environment variable if none is provided in the function.
        verify (Optional[bool], optional): Whether to verify SSL certificates. Defaults to False.
            Will read VERIFY environment variable if none is provided in the function.

    Returns:
        dict: The JSON response containing information about the deletion.

    Raises:
        MissingParameterError: If table or table_record_sys_id is not provided (handled by the Api).
        ParameterError: If invalid parameters or responses are encountered (handled by the Api).
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


@mcp.tool()
def get_table(
    table: str,
    servicenow_instance: str = environment_servicenow_instance,
    name_value_pairs: Optional[Dict[str, str]] = None,
    sysparm_display_value: Optional[str] = None,
    sysparm_exclude_reference_link: Optional[bool] = None,
    sysparm_fields: Optional[str] = None,
    sysparm_limit: Optional[int] = None,
    sysparm_no_count: Optional[bool] = None,
    sysparm_offset: Optional[int] = None,
    sysparm_query: Optional[str] = None,
    sysparm_query_category: Optional[str] = None,
    sysparm_query_no_domain: Optional[bool] = None,
    sysparm_suppress_pagination_header: Optional[bool] = None,
    sysparm_view: Optional[str] = None,
    username: str = environment_username,
    password: str = environment_password,
    client_id: Optional[str] = environment_client_id,
    client_secret: Optional[str] = environment_client_secret,
    verify: Optional[bool] = environment_verify,
) -> dict:
    """
    Get records from the specified table on a ServiceNow instance.

    This tool retrieves records from the specified table based on provided parameters.
    Authentication can be provided via basic auth (username and password) or OAuth (client_id and client_secret).
    At least one authentication method must be configured in the Api client, but validation is handled by the underlying Api.

    Args:
        table (str): The name of the table.
        name_value_pairs (Optional[Dict[str, str]], optional): Dictionary of name-value pairs for filtering records. Defaults to None.
        sysparm_display_value (Optional[str], optional): Display values for reference fields ('True', 'False', or 'all'). Defaults to None.
        sysparm_exclude_reference_link (Optional[bool], optional): Exclude reference links in the response. Defaults to None.
        sysparm_fields (Optional[str], optional): Comma-separated list of field names to include in the response. Defaults to None.
        sysparm_limit (Optional[int], optional): Maximum number of records to return. Defaults to None.
        sysparm_no_count (Optional[bool], optional): Do not include the total number of records in the response. Defaults to None.
        sysparm_offset (Optional[int], optional): Number of records to skip before starting the retrieval. Defaults to None.
        sysparm_query (Optional[str], optional): Encoded query string for filtering records. Defaults to None.
        sysparm_query_category (Optional[str], optional): Category to which the query belongs. Defaults to None.
        sysparm_query_no_domain (Optional[bool], optional): Exclude records based on domain separation. Defaults to None.
        sysparm_suppress_pagination_header (Optional[bool], optional): Suppress pagination headers in the response. Defaults to None.
        sysparm_view (Optional[str], optional): Display style ('desktop', 'mobile', or 'both'). Defaults to None.
        servicenow_instance (str): The URL of the ServiceNow instance (e.g., https://yourinstance.servicenow.com).
            Will read SERVICENOW_INSTANCE environment variable if none is provided in the function.
        username (Optional[str], optional): Username for basic authentication. Defaults to None.
            Will read USERNAME environment variable if none is provided in the function.
        password (Optional[str], optional): Password for basic authentication. Defaults to None.
            Will read PASSWORD environment variable if none is provided in the function.
        client_id (Optional[str], optional): Client ID for OAuth authentication. Defaults to None.
            Will read CLIENT_ID environment variable if none is provided in the function.
        client_secret (Optional[str], optional): Client secret for OAuth authentication. Defaults to None.
            Will read CLIENT_SECRET environment variable if none is provided in the function.
        verify (Optional[bool], optional): Whether to verify SSL certificates. Defaults to False.
            Will read VERIFY environment variable if none is provided in the function.

    Returns:
        dict: The JSON response containing information about the retrieved records.

    Raises:
        MissingParameterError: If table is not provided (handled by the Api).
        ParameterError: If input parameters are invalid (handled by the Api).
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


@mcp.tool()
def get_table_record(
    table: str,
    table_record_sys_id: str,
    servicenow_instance: str = environment_servicenow_instance,
    username: str = environment_username,
    password: str = environment_password,
    client_id: Optional[str] = environment_client_id,
    client_secret: Optional[str] = environment_client_secret,
    verify: Optional[bool] = environment_verify,
) -> dict:
    """
    Get a specific record from the specified table on a ServiceNow instance.

    This tool retrieves a specific record from the specified table based on the provided table name and record sys_id.
    Authentication can be provided via basic auth (username and password) or OAuth (client_id and client_secret).
    At least one authentication method must be configured in the Api client, but validation is handled by the underlying Api.

    Args:
        table (str): The name of the table.
        table_record_sys_id (str): The sys_id of the record to be retrieved.
        servicenow_instance (str): The URL of the ServiceNow instance (e.g., https://yourinstance.servicenow.com).
            Will read SERVICENOW_INSTANCE environment variable if none is provided in the function.
        username (Optional[str], optional): Username for basic authentication. Defaults to None.
            Will read USERNAME environment variable if none is provided in the function.
        password (Optional[str], optional): Password for basic authentication. Defaults to None.
            Will read PASSWORD environment variable if none is provided in the function.
        client_id (Optional[str], optional): Client ID for OAuth authentication. Defaults to None.
            Will read CLIENT_ID environment variable if none is provided in the function.
        client_secret (Optional[str], optional): Client secret for OAuth authentication. Defaults to None.
            Will read CLIENT_SECRET environment variable if none is provided in the function.
        verify (Optional[bool], optional): Whether to verify SSL certificates. Defaults to False.
            Will read VERIFY environment variable if none is provided in the function.

    Returns:
        dict: The JSON response containing information about the retrieved record.

    Raises:
        MissingParameterError: If table or table_record_sys_id is not provided (handled by the Api).
        ParameterError: If invalid parameters or responses are encountered (handled by the Api).
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


@mcp.tool()
def patch_table_record(
    table: str,
    table_record_sys_id: str,
    data: Dict[str, Any],
    servicenow_instance: str = environment_servicenow_instance,
    username: str = environment_username,
    password: str = environment_password,
    client_id: Optional[str] = environment_client_id,
    client_secret: Optional[str] = environment_client_secret,
    verify: Optional[bool] = environment_verify,
) -> dict:
    """
    Partially update a record in the specified table on a ServiceNow instance.

    This tool partially updates a record in the specified table with the provided data.
    Authentication can be provided via basic auth (username and password) or OAuth (client_id and client_secret).
    At least one authentication method must be configured in the Api client, but validation is handled by the underlying Api.

    Args:
        table (str): The name of the table.
        table_record_sys_id (str): The sys_id of the record to be updated.
        data (Dict[str, Any]): Dictionary containing the fields to be updated.
        servicenow_instance (str): The URL of the ServiceNow instance (e.g., https://yourinstance.servicenow.com).
            Will read SERVICENOW_INSTANCE environment variable if none is provided in the function.
        username (Optional[str], optional): Username for basic authentication. Defaults to None.
            Will read USERNAME environment variable if none is provided in the function.
        password (Optional[str], optional): Password for basic authentication. Defaults to None.
            Will read PASSWORD environment variable if none is provided in the function.
        client_id (Optional[str], optional): Client ID for OAuth authentication. Defaults to None.
            Will read CLIENT_ID environment variable if none is provided in the function.
        client_secret (Optional[str], optional): Client secret for OAuth authentication. Defaults to None.
            Will read CLIENT_SECRET environment variable if none is provided in the function.
        verify (Optional[bool], optional): Whether to verify SSL certificates. Defaults to False.
            Will read VERIFY environment variable if none is provided in the function.

    Returns:
        dict: The JSON response containing information about the update.

    Raises:
        MissingParameterError: If table, table_record_sys_id, or data is not provided (handled by the Api).
        ParameterError: If JSON serialization fails (handled by the Api).
        ParameterError: If invalid parameters or responses are encountered (handled by the Api).
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


@mcp.tool()
def update_table_record(
    table: str,
    table_record_sys_id: str,
    data: Dict[str, Any],
    servicenow_instance: str = environment_servicenow_instance,
    username: str = environment_username,
    password: str = environment_password,
    client_id: Optional[str] = environment_client_id,
    client_secret: Optional[str] = environment_client_secret,
    verify: Optional[bool] = environment_verify,
) -> dict:
    """
    Fully update a record in the specified table on a ServiceNow instance.

    This tool fully updates a record in the specified table with the provided data.
    Authentication can be provided via basic auth (username and password) or OAuth (client_id and client_secret).
    At least one authentication method must be configured in the Api client, but validation is handled by the underlying Api.

    Args:
        table (str): The name of the table.
        table_record_sys_id (str): The sys_id of the record to be updated.
        data (Dict[str, Any]): Dictionary containing the fields to be updated.
        servicenow_instance (str): The URL of the ServiceNow instance (e.g., https://yourinstance.servicenow.com).
            Will read SERVICENOW_INSTANCE environment variable if none is provided in the function.
        username (Optional[str], optional): Username for basic authentication. Defaults to None.
            Will read USERNAME environment variable if none is provided in the function.
        password (Optional[str], optional): Password for basic authentication. Defaults to None.
            Will read PASSWORD environment variable if none is provided in the function.
        client_id (Optional[str], optional): Client ID for OAuth authentication. Defaults to None.
            Will read CLIENT_ID environment variable if none is provided in the function.
        client_secret (Optional[str], optional): Client secret for OAuth authentication. Defaults to None.
            Will read CLIENT_SECRET environment variable if none is provided in the function.
        verify (Optional[bool], optional): Whether to verify SSL certificates. Defaults to False.
            Will read VERIFY environment variable if none is provided in the function.

    Returns:
        dict: The JSON response containing information about the update.

    Raises:
        MissingParameterError: If table, table_record_sys_id, or data is not provided (handled by the Api).
        ParameterError: If JSON serialization fails (handled by the Api).
        ParameterError: If invalid parameters or responses are encountered (handled by the Api).
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


@mcp.tool()
def add_table_record(
    table: str,
    data: Dict[str, Any],
    servicenow_instance: str = environment_servicenow_instance,
    username: str = environment_username,
    password: str = environment_password,
    client_id: Optional[str] = environment_client_id,
    client_secret: Optional[str] = environment_client_secret,
    verify: Optional[bool] = environment_verify,
) -> dict:
    """
    Add a new record to the specified table on a ServiceNow instance.

    This tool adds a new record to the specified table with the provided data.
    Authentication can be provided via basic auth (username and password) or OAuth (client_id and client_secret).
    At least one authentication method must be configured in the Api client, but validation is handled by the underlying Api.

    Args:
        table (str): The name of the table.
        data (Dict[str, Any]): Dictionary containing the field values for the new record.
        servicenow_instance (str): The URL of the ServiceNow instance (e.g., https://yourinstance.servicenow.com).
            Will read SERVICENOW_INSTANCE environment variable if none is provided in the function.
        username (Optional[str], optional): Username for basic authentication. Defaults to None.
            Will read USERNAME environment variable if none is provided in the function.
        password (Optional[str], optional): Password for basic authentication. Defaults to None.
            Will read PASSWORD environment variable if none is provided in the function.
        client_id (Optional[str], optional): Client ID for OAuth authentication. Defaults to None.
            Will read CLIENT_ID environment variable if none is provided in the function.
        client_secret (Optional[str], optional): Client secret for OAuth authentication. Defaults to None.
            Will read CLIENT_SECRET environment variable if none is provided in the function.
        verify (Optional[bool], optional): Whether to verify SSL certificates. Defaults to False.
            Will read VERIFY environment variable if none is provided in the function.

    Returns:
        dict: The JSON response containing information about the added record.

    Raises:
        MissingParameterError: If table or data is not provided (handled by the Api).
        ParameterError: If JSON serialization fails (handled by the Api).
        ParameterError: If invalid parameters or responses are encountered (handled by the Api).
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


# Custom API Tools
@mcp.tool()
def api_request(
    method: str,
    endpoint: str,
    servicenow_instance: str = environment_servicenow_instance,
    data: Optional[Dict[str, Any]] = None,
    json: Optional[Dict[str, Any]] = None,
    username: str = environment_username,
    password: str = environment_password,
    client_id: Optional[str] = environment_client_id,
    client_secret: Optional[str] = environment_client_secret,
    verify: Optional[bool] = environment_verify,
) -> dict:
    """
    Make a custom API request to a ServiceNow instance.

    This tool performs a custom API request using the specified HTTP method and endpoint.
    Authentication can be provided via basic auth (username and password) or OAuth (client_id and client_secret).
    At least one authentication method must be configured in the Api client, but validation is handled by the underlying Api.

    Args:
        method (str): The HTTP method to use ('GET', 'POST', 'PUT', 'DELETE').
        endpoint (str): The API endpoint to send the request to.
        data (Optional[Dict[str, Any]], optional): Data to include in the request body (for non-JSON payloads). Defaults to None.
        json (Optional[Dict[str, Any]], optional): JSON data to include in the request body. Defaults to None.
        servicenow_instance (str): The URL of the ServiceNow instance (e.g., https://yourinstance.servicenow.com).
            Will read SERVICENOW_INSTANCE environment variable if none is provided in the function.
        username (Optional[str], optional): Username for basic authentication. Defaults to None.
            Will read USERNAME environment variable if none is provided in the function.
        password (Optional[str], optional): Password for basic authentication. Defaults to None.
            Will read PASSWORD environment variable if none is provided in the function.
        client_id (Optional[str], optional): Client ID for OAuth authentication. Defaults to None.
            Will read CLIENT_ID environment variable if none is provided in the function.
        client_secret (Optional[str], optional): Client secret for OAuth authentication. Defaults to None.
            Will read CLIENT_SECRET environment variable if none is provided in the function.
        verify (Optional[bool], optional): Whether to verify SSL certificates. Defaults to False.
            Will read VERIFY environment variable if none is provided in the function.

    Returns:
        dict: The JSON response containing information about the request.

    Raises:
        ValueError: If an unsupported HTTP method is provided.
        ParameterError: If invalid parameters or responses are encountered (handled by the Api).
        ParameterError: If JSON serialization fails (handled by the Api).
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


def servicenow_api_mcp(argv):
    transport = "stdio"
    host = "0.0.0.0"
    port = 8000
    try:
        opts, args = getopt.getopt(
            argv,
            "ht:h:p:",
            ["help", "transport=", "host=", "port="],
        )
    except getopt.GetoptError:
        sys.exit(2)
    for opt, arg in opts:
        if opt in ("-h", "--help"):
            sys.exit()
        elif opt in ("-t", "--transport"):
            transport = arg
        elif opt in ("-h", "--host"):
            host = arg
        elif opt in ("-p", "--port"):
            try:
                port = int(arg)  # Attempt to convert port to integer
                if not (0 <= port <= 65535):  # Valid port range
                    print(f"Error: Port {arg} is out of valid range (0-65535).")
                    sys.exit(1)
            except ValueError:
                print(f"Error: Port {arg} is not a valid integer.")
                sys.exit(1)
    if transport == "stdio":
        mcp.run(transport="stdio")
    elif transport == "http":
        mcp.run(transport="http", host=host, port=port)
    else:
        logger = logging.getLogger("MediaDownloader")
        logger.error("Transport not supported")
        sys.exit(1)


def main():
    servicenow_api_mcp(sys.argv[1:])


if __name__ == "__main__":
    servicenow_api_mcp(sys.argv[1:])
