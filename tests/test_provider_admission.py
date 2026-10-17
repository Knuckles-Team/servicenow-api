"""Release-admission and runtime configuration contracts for ServiceNow."""

from __future__ import annotations

import json
from pathlib import Path

from agent_connector_sdk.manifest.loader import (
    load_manifest,
    load_tool_presets,
    load_tool_schema_fingerprints,
)
from agent_connector_sdk.manifest.package_validation import validate_connector_package

REPOSITORY_ROOT = Path(__file__).resolve().parents[1]


def test_connector_manifest_passes_release_admission() -> None:
    """The provider's live manifest must pass GraphOS' fail-closed sync gate."""
    connectors = REPOSITORY_ROOT / "servicenow_api" / "connectors"
    violations = validate_connector_package(
        load_manifest(REPOSITORY_ROOT / "connector_manifest.yml"),
        load_tool_presets(connectors / "mcp_source_presets.json"),
        load_tool_schema_fingerprints(connectors / "tool_schema_fingerprints.json"),
    )

    assert violations == []


def test_mcp_config_exposes_basic_auth_runtime_aliases() -> None:
    """Local MCP launch config matches the provider's documented auth names."""
    config = json.loads((REPOSITORY_ROOT / "mcp_config.json").read_text())
    env = config["mcpServers"]["servicenow-api"]["env"]

    assert env["SERVICENOW_INSTANCE"] == "https://instance.example.invalid"
    assert env["SERVICENOW_USERNAME"] == "your_servicenow_username_here"
    assert env["SERVICENOW_PASSWORD"] == "your_servicenow_password_here"
