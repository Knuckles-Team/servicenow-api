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
    assert len(campaign["skills"]) == 22
    assert campaign["catalogs"] == {
        "condensed": "MCP_TOOL_MODE=intent",
        "verbose": "MCP_TOOL_MODE=verbose",
    }


# REMOVED (SCION-CONNECTOR-CONTROL-R009/R020 migration):
# test_campaign_catalogs_register_condensed_and_verbose_surfaces asserted that
# MCP_TOOL_MODE="verbose" registered a 1:1 tool per Api method alongside the
# intent-gated condensed tool. scion_sdk.mcp.tool_surface.register_tool_surface
# has no mode parameter — it always registers only the condensed, GATED_TAG-tagged
# surface (scion-sdk#54's one condensed intent contract), so there is no
# verbose surface left to assert on.


# REMOVED (SCION-CONNECTOR-CONTROL-R009/R020 migration):
# test_verbose_client_catalog_hides_condensed_dispatch_tools asserted the same
# retired verbose 1:1 tool surface via a live FastMCP Client catalog; see the note
# above test_campaign_catalogs_register_condensed_and_verbose_surfaces.
