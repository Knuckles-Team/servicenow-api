"""Native epistemic-graph typed-node ingestion — Wire-First coverage.

Exercises the real ``ingest_incidents`` / ``ingest_changes`` / ``ingest_cmdb`` /
``ingest_kb_articles`` / ``ingest_attachment`` seam with a fake engine client + a fake
media store (no engine required), asserting the txn add_node/commit + edge calls and the
ServiceNow record → :Incident / :Change / :ConfigurationItem / :Person / :Document mapping.
CONCEPT:AU-KG.ingest.enterprise-source-extractor.
"""

from __future__ import annotations

from typing import Any

import msgpack
import pytest
from agent_utilities.knowledge_graph.memory.native_ingest import NativeIngestError
from agent_utilities.security.brain_context import ActorContext, use_actor
from agent_utilities.models.company_brain import ActorType
from agent_utilities.knowledge_graph.core.session import GraphSession, use_session

from servicenow_api.kg_ingest import (
    ingest_attachment,
    ingest_changes,
    ingest_cmdb,
    ingest_entities,
    ingest_incidents,
    ingest_kb_articles,
)


@pytest.fixture(autouse=True)
def _governed_session():
    actor = ActorContext(
        actor_id="subject:opaque:synthetic",
        actor_type=ActorType.AUTOMATED_SERVICE,
        roles=(),
        tenant_id="tenant:opaque:synthetic",
        authenticated=True,
    )
    session = GraphSession(
        actor=actor,
        tenant=actor.tenant_id,
        scopes=frozenset({"kg:write"}),
        graph="graph:opaque:synthetic",
        policy_version="policy:opaque:synthetic",
        audience="epistemic-graph",
    )
    with use_actor(actor), use_session(session):
        yield


class _FakeNodes:
    def __init__(self) -> None:
        self.values: dict[str, dict[str, Any]] = {}

    def properties(self, node_id: str) -> dict[str, Any] | None:
        return self.values.get(node_id)

    def list(self) -> list[tuple[str, dict[str, Any]]]:
        return list(self.values.items())


class _FakeChanges:
    def __init__(self, nodes: _FakeNodes) -> None:
        self.nodes = nodes
        self.edges: list[tuple[str, str, dict[str, Any]]] = []
        self.applied: list[dict[str, Any]] = []
        self.records: dict[str, dict[str, Any]] = {}
        self.versions: dict[str, dict[str, Any]] = {}

    def get(self, envelope_id: str) -> dict[str, Any] | None:
        return self.records.get(envelope_id)

    def content_version(self, object_id: str) -> dict[str, Any] | None:
        return self.versions.get(object_id)

    def cursor(self, _source: str, _partition: str = "") -> None:
        return None

    def apply(self, envelope: dict[str, Any]) -> dict[str, Any]:
        self.applied.append(envelope)
        mutation = envelope["mutation"]
        for operation in mutation["operations"]:
            method = operation["method"]
            params = method["params"]
            properties = msgpack.unpackb(params["properties_msgpack"], raw=False)
            if method["method"] == "AddNode":
                self.nodes.values[params["node_id"]] = properties
            elif method["method"] == "AddEdge":
                self.edges.append(
                    (params["source_id"], params["target_id"], properties)
                )
        version = envelope["content_version"]
        self.versions[version["object_id"]] = version
        self.records[envelope["envelope_id"]] = envelope
        return {
            "batch_id": mutation["batch_id"],
            "replayed": False,
            "projection_pending": False,
        }


class _FakeRdf:
    def validate_shacl(self, _shapes: str, _data_graph: str) -> dict[str, Any]:
        return {"conforms": True, "results": []}


class _FakeClient:
    def __init__(self) -> None:
        self.nodes = _FakeNodes()
        self.changes = _FakeChanges(self.nodes)
        self.rdf = _FakeRdf()

    @staticmethod
    def supports(operation: str) -> bool:
        return operation == "ApplyChangeEnvelope"


class _Stored:
    asset_id = "asset-1"
    digest = "deadbeef"


class _FakeMediaStore:
    def __init__(self):
        self.calls = []

    def store_media(self, data, **kwargs):
        self.calls.append((data, kwargs))
        return _Stored()


def test_ingest_entities_writes_nodes_and_edges():
    c = _FakeClient()
    res = ingest_entities(
        [
            {"id": "a", "node_type": "Incident", "number": "INC1"},
            {"id": "b", "node_type": "ConfigurationItem"},
        ],
        [{"source": "a", "target": "b", "relationship": "affects"}],
        client=c,
    )
    assert res == {"nodes": 2, "edges": 1}
    assert len(c.changes.applied) == 1
    assert set(c.nodes.values) == {"a", "b"}
    # provenance is stamped
    assert c.nodes.values["a"]["source"] == "servicenow-api"
    assert c.nodes.values["a"]["domain"] == "servicenow"
    assert c.changes.edges == [("a", "b", {"relationship": "affects"})]


def test_ingest_incidents_maps_incident_ci_and_person():
    c = _FakeClient()
    res = ingest_incidents(
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
        client=c,
    )
    assert res == {"nodes": 3, "edges": 2}
    inc = c.nodes.values["servicenow:incident:s1"]
    assert inc["node_type"] == "Incident"
    assert inc["number"] == "INC0010001"
    assert inc["shortDescription"] == "DB down"
    # ReferenceField unwrapped to its display value
    assert inc["state"] == "In Progress"
    assert inc["priority"] == "1 - Critical"
    assert inc["externalToolId"] == "s1"
    assert c.nodes.values["servicenow:ci:ci9"]["node_type"] == "ConfigurationItem"
    assert c.nodes.values["servicenow:person:u7"]["node_type"] == "Person"
    assert c.nodes.values["servicenow:person:u7"]["name"] == "Ada Lovelace"
    assert (
        "servicenow:incident:s1",
        "servicenow:ci:ci9",
        {"relationship": "affects"},
    ) in c.changes.edges
    assert (
        "servicenow:incident:s1",
        "servicenow:person:u7",
        {"relationship": "assignedTo"},
    ) in c.changes.edges


def test_ingest_changes_maps_change():
    c = _FakeClient()
    res = ingest_changes(
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
        client=c,
    )
    assert res == {"nodes": 2, "edges": 1}
    chg = c.nodes.values["servicenow:change:c1"]
    assert chg["node_type"] == "Change"
    assert chg["number"] == "CHG0005000"
    assert chg["risk"] == "Moderate"
    assert c.changes.edges == [
        ("servicenow:change:c1", "servicenow:ci:ci9", {"relationship": "affects"})
    ]


def test_ingest_cmdb_maps_configuration_items():
    c = _FakeClient()
    res = ingest_cmdb(
        [
            {
                "sys_id": "ci9",
                "name": "prod-db-01",
                "sys_class_name": "cmdb_ci_db_mysql_instance",
                "operational_status": "1",
            }
        ],
        client=c,
    )
    assert res == {"nodes": 1, "edges": 0}
    ci = c.nodes.values["servicenow:ci:ci9"]
    assert ci["node_type"] == "ConfigurationItem"
    assert ci["name"] == "prod-db-01"
    assert ci["sys_class_name"] == "cmdb_ci_db_mysql_instance"
    assert ci["externalToolId"] == "ci9"


def test_ingest_kb_articles_maps_documents():
    c = _FakeClient()
    res = ingest_kb_articles(
        [
            {
                "sys_id": "kb1",
                "number": "KB0001000",
                "short_description": "How to reset a password",
                "content": "Step 1: ...",
                "link": "https://sn/kb1",
            }
        ],
        client=c,
    )
    assert res == {"nodes": 1, "edges": 0}
    doc = c.nodes.values["servicenow:kb:kb1"]
    assert doc["node_type"] == "Document"
    assert doc["subtype"] == "KnowledgeArticle"
    assert doc["text"] == "Step 1: ..."
    # native_ingest's governed PII scrubber redacts uri-shaped values.
    assert doc["source_uri"] == "[REDACTED_LOCATION]"
    assert doc["title"] == "How to reset a password"


def test_ingest_attachment_stores_blob():
    store = _FakeMediaStore()
    res = ingest_attachment(
        b"file-bytes",
        "evidence.log",
        mime_type="text/plain",
        incident_id="servicenow:incident:s1",
        media_store=store,
    )
    assert res == {"asset_id": "asset-1", "digest": "deadbeef", "size_bytes": 10}
    assert len(store.calls) == 1
    data, kwargs = store.calls[0]
    assert data == b"file-bytes"
    assert kwargs["source"] == "servicenow-api"
    assert kwargs["name"] == "evidence.log"
    assert kwargs["extra"]["incident_id"] == "servicenow:incident:s1"


def test_ingest_attachment_rejects_empty_bytes():
    with pytest.raises(NativeIngestError, match="non-empty bytes"):
        ingest_attachment(b"", "empty", media_store=_FakeMediaStore())


def test_ingest_attachment_propagates_store_failure():
    class _FailingStore:
        def store_media(self, *_args, **_kwargs):
            raise RuntimeError("unavailable")

    with pytest.raises(NativeIngestError, match="transaction failed"):
        ingest_attachment(b"data", "evidence", media_store=_FailingStore())


def test_retired_structural_alias_is_rejected():
    with pytest.raises(NativeIngestError, match="canonical node_type"):
        ingest_entities([{"id": "a", "type": "Incident"}], client=_FakeClient())


def test_empty_native_ingest_is_rejected():
    with pytest.raises(NativeIngestError, match="at least one entity"):
        ingest_entities([], client=_FakeClient())
