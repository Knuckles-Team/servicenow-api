"""Owner, steward and CMDB edges declared on the ingest sources (CONN-SERVICENOW-API-CONNECTOR-CONTENT-R007)."""

from __future__ import annotations

from pathlib import Path

import pytest
from agent_connector_sdk.ingest import load_declaration
from agent_connector_sdk.ingest.source_sync import _edges  # noqa: PLC2701

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
    record = {
        "sys_id": "inc-1",
        "assignment_group": {
            "link": "https://x/api/now/table/sys_user_group/g1",
            "value": "g1",
        },
        "assigned_to": {"link": "https://x/api/now/table/sys_user/u1", "value": "u1"},
        "cmdb_ci": {"link": "https://x/api/now/table/cmdb_ci/ci1", "value": "ci1"},
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
def test_change_and_knowledge_sources_call_their_tools_with_accepted_arguments() -> (
    None
):
    """G13: the change source passed sysparm_limit, which servicenow_get_change_requests
    does not accept, and the knowledge source read `result` where the Knowledge API
    nests the list at `result.articles`; both syncs ended failed with 0 records."""
    from agent_connector_sdk.ingest.source_sync import _records  # noqa: PLC2701

    declaration = declared_sources()
    change = declaration.source("change-requests")
    assert change.tools == ("servicenow_get_change_requests",)
    assert "sysparm_limit" not in change.arguments
    knowledge = declaration.source("servicenow-knowledge")
    page = {
        "result": {
            "meta": {"count": 1},
            "articles": [{"sys_id": "kb1", "number": "KB0001"}],
        }
    }
    assert [r["sys_id"] for r in _records(page, knowledge)] == ["kb1"]
