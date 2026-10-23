"""Release-admission and runtime configuration contracts for ServiceNow."""

from __future__ import annotations

import json
from pathlib import Path

REPOSITORY_ROOT = Path(__file__).resolve().parents[1]


def test_mcp_config_exposes_basic_auth_runtime_aliases() -> None:
    """Local MCP launch config matches the provider's documented auth names."""
    config = json.loads((REPOSITORY_ROOT / "mcp_config.json").read_text())
    env = config["mcpServers"]["servicenow-api"]["env"]

    assert env["SERVICENOW_INSTANCE"] == "https://instance.example.invalid"
    assert env["SERVICENOW_USERNAME"] == "your_servicenow_username_here"
    assert env["SERVICENOW_PASSWORD"] == "your_servicenow_password_here"
