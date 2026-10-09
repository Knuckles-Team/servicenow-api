"""Native epistemic-graph typed-node ingestion — Wire-First coverage.

Exercises the real ``ingest_incidents`` / ``ingest_changes`` / ``ingest_cmdb`` /
``ingest_kb_articles`` / ``ingest_attachment`` seam with a fake transport one level
below ``agent_connector_sdk.ingest.KnowledgeIngest`` (no engine required), so the
SDK's own request-building/validation/privacy-guard contract runs unfaked,
asserting the ServiceNow record →
:Incident / :Change / :ConfigurationItem / :Person / :Document mapping.
CONCEPT:AU-KG.ingest.enterprise-source-extractor.
"""

from __future__ import annotations

from types import SimpleNamespace
from typing import Any

import pytest
from agent_connector_sdk.ingest import IngestError, KnowledgeIngest

from servicenow_api.kg_ingest import (
    ingest_attachment,
    ingest_changes,
    ingest_cmdb,
    ingest_entities,
    ingest_incidents,
    ingest_kb_articles,
)


class _FakeTransport:
    def __init__(self) -> None:
        self.requests: list[Any] = []
        self.blobs: list[bytes] = []

    async def source_status(self, connector: str, stream: str):
        return SimpleNamespace(accepted_checkpoint=None)

    async def submit(self, request):
        self.requests.append(request)
        return SimpleNamespace(
            affected_count=len(request.records),
            relationship_count=len(request.relationships),
        )

    async def store_blob(self, data: bytes) -> str:
        self.blobs.append(data)
        return "deadbeef"


class _FailingTransport(_FakeTransport):
    async def store_blob(self, data: bytes) -> str:
        raise RuntimeError("unavailable")


@pytest.fixture
def ingest():
    transport = _FakeTransport()
    return KnowledgeIngest(transport, loop=None), transport


def _by_id(request):
    return {record.record_id: record for record in request.records}


def _edge_types(request):
    return {
        (
            rel.source.record_id,
            rel.target.record_id,
            rel.relation_reference.rsplit("/relations/", 1)[-1],
        )
        for rel in request.relationships
    }


def _is_type(record, type_name: str) -> bool:
    return record.mapping_reference.endswith(f"/{type_name}")


async def test_ingest_entities_writes_nodes_and_edges(ingest):
    service, transport = ingest
    res = await ingest_entities(
        [
            {"id": "a", "node_type": "Incident", "number": "INC1"},
            {"id": "b", "node_type": "ConfigurationItem"},
        ],
        [{"source": "a", "target": "b", "relationship": "affects"}],
        ingest=service,
    )
    assert res == {"nodes": 2, "edges": 1}
    request = transport.requests[0]
    assert set(_by_id(request)) == {"a", "b"}
    assert _edge_types(request) == {("a", "b", "affects")}


async def test_ingest_incidents_maps_incident_ci_and_person(ingest):
    service, transport = ingest
    res = await ingest_incidents(
        [
            {
                "sys_id": "s1",
                "number": "INC0010001",
                "short_description": "DB down",
                "state": {"value": "2", "display_value": "In Progress"},
                "priority": {"value": "1", "display_value": "1 - Critical"},
                "cmdb_ci": {"value": "ci9", "display_value": "prod-db-01"},
                "assigned_to": {"value": "u7", "display_value": "Ada Lovelace"},
            }
        ],
        ingest=service,
    )
    assert res == {"nodes": 3, "edges": 2}
    request = transport.requests[0]
    by_id = _by_id(request)
    inc = by_id["servicenow:incident:s1"]
    assert _is_type(inc, "Incident")
    assert inc.payload["number"] == "INC0010001"
    assert inc.payload["shortDescription"] == "DB down"
    # ReferenceField unwrapped to its display value
    assert inc.payload["state"] == "In Progress"
    assert inc.payload["priority"] == "1 - Critical"
    assert inc.payload["externalToolId"] == "s1"
    assert _is_type(by_id["servicenow:ci:ci9"], "ConfigurationItem")
    assert _is_type(by_id["servicenow:person:u7"], "Person")
    assert by_id["servicenow:person:u7"].payload["name"] == "Ada Lovelace"
    edges = _edge_types(request)
    assert ("servicenow:incident:s1", "servicenow:ci:ci9", "affects") in edges
    assert ("servicenow:incident:s1", "servicenow:person:u7", "assignedTo") in edges


async def test_ingest_changes_maps_change(ingest):
    service, transport = ingest
    res = await ingest_changes(
        [
            {
                "sys_id": "c1",
                "number": "CHG0005000",
                "short_description": "Upgrade cluster",
                "state": "Assess",
                "risk": "Moderate",
                "cmdb_ci": {"value": "ci9", "display_value": "prod-db-01"},
            }
        ],
        ingest=service,
    )
    assert res == {"nodes": 2, "edges": 1}
    request = transport.requests[0]
    chg = _by_id(request)["servicenow:change:c1"]
    assert _is_type(chg, "Change")
    assert chg.payload["number"] == "CHG0005000"
    assert chg.payload["risk"] == "Moderate"
    assert _edge_types(request) == {
        ("servicenow:change:c1", "servicenow:ci:ci9", "affects")
    }


async def test_ingest_cmdb_maps_configuration_items(ingest):
    service, transport = ingest
    res = await ingest_cmdb(
        [
            {
                "sys_id": "ci9",
                "name": "prod-db-01",
                "sys_class_name": "cmdb_ci_db_mysql_instance",
                "operational_status": "1",
            }
        ],
        ingest=service,
    )
    assert res == {"nodes": 1, "edges": 0}
    ci = _by_id(transport.requests[0])["servicenow:ci:ci9"]
    assert _is_type(ci, "ConfigurationItem")
    assert ci.payload["name"] == "prod-db-01"
    assert ci.payload["sys_class_name"] == "cmdb_ci_db_mysql_instance"
    assert ci.payload["externalToolId"] == "ci9"


async def test_ingest_kb_articles_maps_documents(ingest):
    service, transport = ingest
    res = await ingest_kb_articles(
        [
            {
                "sys_id": "kb1",
                "number": "KB0001000",
                "short_description": "How to reset a password",
                "content": "Step 1: ...",
                "link": "https://sn/kb1",
            }
        ],
        ingest=service,
    )
    assert res == {"nodes": 1, "edges": 0}
    doc = _by_id(transport.requests[0])["servicenow:kb:kb1"]
    assert _is_type(doc, "Document")
    assert doc.payload["subtype"] == "KnowledgeArticle"
    assert doc.payload["text"] == "Step 1: ..."
    # the SDK's persistence privacy guard redacts uri-shaped values.
    assert doc.payload["source_uri"] == "[REDACTED_LOCATION]"
    assert doc.payload["title"] == "How to reset a password"


async def test_ingest_attachment_stores_blob(ingest):
    service, transport = ingest
    res = await ingest_attachment(
        b"file-bytes",
        "evidence.log",
        mime_type="text/plain",
        incident_id="servicenow:incident:s1",
        ingest=service,
    )
    assert res["size_bytes"] == 10
    assert res["asset_id"].startswith("servicenow:attachment:")
    assert transport.blobs == [b"file-bytes"]
    request = transport.requests[0]
    asset_record = _by_id(request)[res["asset_id"]]
    assert asset_record.payload["mime_type"] == "text/plain"
    assert asset_record.payload["name"] == "evidence.log"
    assert asset_record.payload["incident_id"] == "servicenow:incident:s1"


async def test_ingest_attachment_rejects_empty_bytes(ingest):
    service, _ = ingest
    with pytest.raises(IngestError, match="non-empty bytes"):
        await ingest_attachment(b"", "empty", ingest=service)


async def test_ingest_attachment_propagates_store_failure():
    service = KnowledgeIngest(_FailingTransport(), loop=None)
    with pytest.raises(IngestError):
        await ingest_attachment(b"data", "evidence", ingest=service)


async def test_retired_structural_alias_is_rejected(ingest):
    service, _ = ingest
    with pytest.raises(IngestError, match="node_type"):
        await ingest_entities([{"id": "a", "type": "Incident"}], ingest=service)


async def test_empty_native_ingest_is_rejected(ingest):
    service, _ = ingest
    with pytest.raises(IngestError, match="at least one entity"):
        await ingest_entities([], ingest=service)
