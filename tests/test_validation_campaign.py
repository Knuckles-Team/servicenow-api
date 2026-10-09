
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


# REMOVED (SDK-CONNECTOR-CONTROL-R009/R020 migration):
# test_campaign_catalogs_register_condensed_and_verbose_surfaces asserted that
# MCP_TOOL_MODE="verbose" registered a 1:1 tool per Api method alongside the
# intent-gated condensed tool. agent_connector_sdk.mcp.tool_surface.register_tool_surface
# has no mode parameter — it always registers only the condensed, GATED_TAG-tagged
# surface (agent-utilities#54's one condensed intent contract), so there is no
# verbose surface left to assert on.


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


# REMOVED (SDK-CONNECTOR-CONTROL-R009/R020 migration):
# test_verbose_client_catalog_hides_condensed_dispatch_tools asserted the same
# retired verbose 1:1 tool surface via a live FastMCP Client catalog; see the note
# above test_campaign_catalogs_register_condensed_and_verbose_surfaces.
