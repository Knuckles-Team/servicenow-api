from unittest.mock import MagicMock, patch

import pytest

from servicenow_api.validation_campaign import (
    build_campaign,
    governance_contract,
    source_preset_contract,
)


def test_source_presets_target_the_deployed_mcp_service():
    assert source_preset_contract() == []
    campaign = build_campaign()
    assert campaign["provider"] == "servicenow-api"
    assert campaign["deployed_mcp_service"] == "servicenow-mcp"


def test_deployed_service_alias_resolves_to_signed_provider():
    from servicenow_api.connectors import resolve_mcp_server

    assert resolve_mcp_server("servicenow-api") == "servicenow-api"
    assert resolve_mcp_server("servicenow-mcp") == "servicenow-api"
    with pytest.raises(ValueError, match="unknown ServiceNow MCP server identity"):
        resolve_mcp_server("servicenow-typo")


def test_governance_requires_fail_closed_materialization_contract():
    assert governance_contract() == []


def test_campaign_covers_every_packaged_skill_without_live_io():
    campaign = build_campaign()
    assert campaign["status"] == "ready"
    assert campaign["offline"] is True
    assert len(campaign["skills"]) == 21
    assert campaign["catalogs"] == {
        "condensed": "MCP_TOOL_MODE=intent",
        "verbose": "MCP_TOOL_MODE=verbose",
    }


@pytest.mark.asyncio
async def test_campaign_catalogs_register_condensed_and_verbose_surfaces(monkeypatch):
    """Catalog verification is local registration only; no client call is made."""
    from servicenow_api.mcp_server import get_mcp_instance

    client = MagicMock()
    monkeypatch.setenv("MCP_TOOL_MODE", "intent")
    with patch("servicenow_api.mcp_server.get_client", return_value=client):
        intent_mcp, *_ = get_mcp_instance()
        intent_names = {tool.name for tool in await intent_mcp.list_tools()}

    monkeypatch.setenv("MCP_TOOL_MODE", "verbose")
    with patch("servicenow_api.mcp_server.get_client", return_value=client):
        verbose_mcp, *_ = get_mcp_instance()
        verbose_names = {tool.name for tool in await verbose_mcp.list_tools()}

    assert "servicenow_incidents" in intent_names
    assert "servicenow_get_incidents" not in intent_names
    assert "servicenow_get_incidents" in verbose_names
    assert "servicenow_incidents" not in verbose_names


@pytest.mark.parametrize("server", ["servicenow-api", "servicenow-mcp"])
def test_source_preset_contract_resolves_known_provider_aliases(tmp_path, server):
    import json
    from pathlib import Path

    relative = Path("servicenow_api/connectors/mcp_source_presets.json")
    source = Path(__file__).resolve().parents[1] / relative
    presets = json.loads(source.read_text())
    for preset in presets.values():
        if isinstance(preset, dict):
            preset["server"] = server
    destination = tmp_path / relative
    destination.parent.mkdir(parents=True)
    destination.write_text(json.dumps(presets))
    assert source_preset_contract(tmp_path) == []


@pytest.mark.parametrize("server", ["servicenow-typo", "", None])
def test_source_preset_contract_rejects_unknown_provider_aliases(tmp_path, server):
    import json
    from pathlib import Path

    relative = Path("servicenow_api/connectors/mcp_source_presets.json")
    source = Path(__file__).resolve().parents[1] / relative
    presets = json.loads(source.read_text())
    presets["servicenow-incidents"]["server"] = server
    destination = tmp_path / relative
    destination.parent.mkdir(parents=True)
    destination.write_text(json.dumps(presets))
    assert source_preset_contract(tmp_path) == [
        "servicenow-incidents must resolve to servicenow-api"
    ]


@pytest.mark.asyncio
async def test_verbose_client_catalog_hides_condensed_dispatch_tools(monkeypatch):
    """Verify the public MCP catalog, not just the internal registry."""
    from fastmcp import Client

    from servicenow_api.mcp_server import get_mcp_instance

    monkeypatch.setenv("MCP_TOOL_MODE", "verbose")
    with patch("servicenow_api.mcp_server.get_client", return_value=MagicMock()):
        mcp, *_ = get_mcp_instance()
    async with Client(mcp) as client:
        names = {tool.name for tool in await client.list_tools()}
    assert "servicenow_get_incidents" in names
    assert "servicenow_incidents" not in names
