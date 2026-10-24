"""The packaged ingestible-source declaration (CONN-SERVICENOW-API-CONNECTOR-CONTENT-R003)."""

from __future__ import annotations

from pathlib import Path

import pytest
from agent_connector_sdk.ingest import load_declaration
from agent_connector_sdk.mcp.method_tools import operation_annotations, operation_verb
from agent_connector_sdk.mcp.tool_surface import operation_prefix

import servicenow_api
from servicenow_api.api.api_client_incident import ServiceNowApiIncident


@pytest.mark.spec("CONN-SERVICENOW-API-CONNECTOR-CONTENT-R003")
def test_declares_ingestible_sources() -> None:
    package_root = Path(servicenow_api.__file__).parent
    declaration = load_declaration("servicenow_api")
    assert declaration is not None
    assert declaration.connector == "servicenow-mcp"
    source = declaration.source("incidents")
    assert source is not None and source.record_type == "Incident"
    prefix = operation_prefix("servicenow-api")
    assert source.tools == (f"{prefix}_get_incidents",)
    # The engine admits a record only under the pack mapping of its type.
    assert source.record_type in load_declaration("servicenow_api").schema_mappings
    method = getattr(ServiceNowApiIncident, "get_incidents")
    annotations = operation_annotations("get_incidents", operation_verb(method))
    assert annotations.read_only_hint is True
