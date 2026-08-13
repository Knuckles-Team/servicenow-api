"""Release-admission and runtime configuration contracts for ServiceNow."""

from __future__ import annotations

import json
from pathlib import Path

from agent_utilities.knowledge_graph.ontology.connector_manifest_gate import (
    check_manifest_bytes,
)

REPOSITORY_ROOT = Path(__file__).resolve().parents[1]


def test_connector_manifest_passes_release_admission() -> None:
    """The provider's live manifest must pass GraphOS' fail-closed sync gate."""
    violations = check_manifest_bytes(
        REPOSITORY_ROOT / "connector_manifest.yml",
        require_signature=True,
        require_provider=True,
    )

    assert violations == []


def test_mcp_config_exposes_basic_auth_runtime_aliases() -> None:
    """Local MCP launch config matches the provider's documented auth names."""
    config = json.loads((REPOSITORY_ROOT / "mcp_config.json").read_text())
    env = config["mcpServers"]["servicenow-api"]["env"]

    assert env["SERVICENOW_INSTANCE"] == "https://instance.example.invalid"
    assert env["SERVICENOW_USERNAME"] == "your_servicenow_username_here"
    assert env["SERVICENOW_PASSWORD"] == "your_servicenow_password_here"
