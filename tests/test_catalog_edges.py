"""Owner, steward and CMDB edges declared on the ingest sources (CONN-SERVICENOW-API-CONNECTOR-CONTENT-R007)."""

from __future__ import annotations

from pathlib import Path

import pytest
from scion_sdk.ingest import load_declaration
from scion_sdk.ingest.source_sync import _edges  # noqa: PLC2701

import servicenow_api


def declared_sources():
    return load_declaration("servicenow_api")


ONTOLOGY = Path(servicenow_api.__file__).parent / "ontology" / "servicenow.ttl"


def _domain_and_range(name: str) -> tuple[str, str]:
    block = ONTOLOGY.read_text(encoding="utf-8").split(
        f"\n:{name} a owl:ObjectProperty"
    )[1]
    block = block.split(" .\n")[0]
    domain = block.split("rdfs:domain :")[1].split()[0]
    target = block.split("rdfs:range :")[1].split()[0]
    return domain, target


@pytest.mark.spec("CONN-SERVICENOW-API-CONNECTOR-CONTENT-R007")
def test_every_declared_edge_is_an_ontology_property_of_its_record_type() -> None:
    declaration = declared_sources()
    seen = set()
    for source in declaration.sources:
        for edge in source.edges:
            domain, target = _domain_and_range(edge.relationship)
            assert domain == source.record_type, edge.relationship
            assert target == edge.target_type, edge.relationship
            assert edge.target_type in declaration.schema_mappings
            seen.add((source.source_id, edge.relationship))
    assert {
        ("incidents", "assignedToGroup"),
        ("incidents", "assignedTo"),
        ("incidents", "impactsConfigurationItem"),
        ("cmdb-cis", "ciOwnedBy"),
        ("cmdb-cis", "managedByGroup"),
        ("cmdb-cis", "supportedByGroup"),
        ("cmdb-ci-relationships", "relationshipParent"),
        ("cmdb-ci-relationships", "relationshipChild"),
        ("change-requests", "touches"),
    } <= seen


@pytest.mark.spec("CONN-SERVICENOW-API-CONNECTOR-CONTENT-R007")
def test_incident_references_become_owner_group_and_ci_edges() -> None:
    source = declared_sources().source("incidents")
    # Reference fields are requested without display values or links, so they
    # arrive as {"value": sys_id} and the edges read the referenced id.
    assert source.arguments["sysparm_display_value"] == "false"
    assert source.arguments["sysparm_exclude_reference_link"] is True
    record = {
        "sys_id": "inc-1",
        "assignment_group": {"value": "g1"},
        "assigned_to": {"value": "u1"},
        "cmdb_ci": {"value": "ci1"},
    }
    edges = {
        (r.relationship, str(r.target)) for _, r in _edges("inc-1", record, source)
    }
    assert ("assignedToGroup", "AssignmentGroup:g1") in edges
    assert ("assignedTo", "Person:u1") in edges
    assert any(
        rel == "impactsConfigurationItem" and "ci1" in t and "cmdb-cis" in t
        for rel, t in edges
    )


@pytest.mark.spec("CONN-SERVICENOW-API-CONNECTOR-CONTENT-R007")
def test_change_and_knowledge_sources_read_their_tables_through_the_table_tool() -> (
    None
):
    """G13: `servicenow_get_change_requests` overran the MCP stream-size limit with
    or without a limit argument, and `servicenow_get_knowledge_articles` was refused
    by the instance; both syncs ended failed with 0 records. Both sources now read
    their table through `servicenow_get_table`, passing only arguments the table
    tool's model accepts (as cmdb-cis does)."""
    from scion_sdk.ingest.source_sync import _records  # noqa: PLC2701

    from servicenow_api.servicenow_models import TableModel

    declaration = declared_sources()
    change = declaration.source("change-requests")
    assert change.tools == ("servicenow_get_table",)
    assert change.arguments["table"] == "change_request"
    assert change.records_path == "result"
    TableModel(**change.arguments)  # every declared argument is accepted
    fields = change.arguments["sysparm_fields"].split(",")
    assert {"sys_id", "cmdb_ci", "sys_updated_on"} <= set(fields)
    knowledge = declaration.source("servicenow-knowledge")
    assert knowledge.tools == ("servicenow_get_table",)
    assert knowledge.arguments["table"] == "kb_knowledge"
    assert knowledge.records_path == "result"
    TableModel(**knowledge.arguments)  # every declared argument is accepted
    page = {"result": [{"sys_id": "kb1", "number": "KB0001"}]}
    assert [r["sys_id"] for r in _records(page, knowledge)] == ["kb1"]
