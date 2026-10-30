#!/usr/bin/env python

from scion_sdk.connector import Connector

from servicenow_api.api_client import Api
from servicenow_api.auth import get_client
from servicenow_api.mcp_server import register_prompts
from servicenow_api.sdk_client import ServiceNowSdkClient, get_sdk_client

connector = Connector(
    api=Api,
    get_client=get_client,
    tools="servicenow_api.mcp_server",
    instructions="ServiceNow MCP Server — Manage incidents, CMDB, workflows, CICD, and more in your ServiceNow instance.",
    verbose_targets=(
        {
            "client_cls": ServiceNowSdkClient,
            "get_client": get_sdk_client,
            "prefix": "servicenow_sdk",
        },
    ),
    extra_registrations=(register_prompts,),
)
