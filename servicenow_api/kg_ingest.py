"""Native epistemic-graph ingestion for ServiceNow records (typed graph nodes).

CONCEPT:AU-KG.ingest.enterprise-source-extractor. This is the ServiceNow twin of the
fleet's native ingestion seam: the connector natively pushes its ITSM data into the ONE
epistemic-graph knowledge graph, in every modality that applies (the "maximum ingestion"
bar):

* **typed nodes** — incidents/changes/CMDB items → OWL ``:Incident`` / ``:Change`` /
  ``:ConfigurationItem`` (+ ``:Person``) nodes with ``:affects`` / ``:assignedTo`` links
  (``ingest_incidents`` / ``ingest_changes`` / ``ingest_cmdb``)
* **documents** — knowledge-base articles → ``:Document`` nodes carrying the article
  text + ``source_uri`` (``ingest_kb_articles``); hub-side enrichment chunks/embeds them
* **blobs** — raw ticket attachments → ``:Blob`` + ``:MediaAsset`` via the ``MediaStore``
  (``ingest_attachment``)

The write path is the shared, one-and-only ``agent_utilities`` native-ingest primitive
(``ingest_entities`` / ``ingest_documents`` / ``media_store``) when it is importable; when
it is not yet present in the installed ``agent_utilities`` we fall back to a self-contained
copy of the same lightweight-engine-client txn dance. Either way everything is
dependency-/engine-guarded: with no KG stack or no reachable engine every entry point
**no-ops** (returns ``None``), so the connector runs with zero KG infrastructure. Node ids
follow ``servicenow:<class>:<sys_id>`` and each ``type`` matches a class the package's
``ontology`` (``servicenow.ttl``) federates.
"""

from __future__ import annotations

import logging
from typing import Any

logger = logging.getLogger("servicenow_api.kg")

_SOURCE = "servicenow-api"
_DOMAIN = "servicenow"
_DEFAULT_GRAPH = "__commons__"

# --- Prefer the shared native-ingest primitive; fall back to a local copy. ----------
try:  # pragma: no cover - import wiring
    from agent_utilities.knowledge_graph.memory.native_ingest import (
        ingest_documents as _shared_documents,
    )
    from agent_utilities.knowledge_graph.memory.native_ingest import (
        ingest_entities as _shared_entities,
    )
    from agent_utilities.knowledge_graph.memory.native_ingest import (
        media_store as _shared_media_store,
    )
except Exception as _e:  # noqa: BLE001 — shared primitive not yet in installed agent_utilities
    logger.debug("shared native_ingest unavailable (%s); using local fallback", _e)
    _shared_documents = None
    _shared_entities = None
    _shared_media_store = None


# --- Local fallback (mirrors agent_utilities.knowledge_graph.memory.native_ingest) ---


def _local_client() -> tuple[Any | None, str]:
    """Return ``(engine_client, graph_name)`` or ``(None, "")`` when unavailable."""
    try:
        from agent_utilities.knowledge_graph.core.graph_compute import (
            GraphComputeEngine,
        )
    except Exception as e:  # noqa: BLE001 — KG stack absent
        logger.debug("KG ingest unavailable (import): %s", e)
        return None, ""
    try:
        engine = GraphComputeEngine()
        client = getattr(engine, "_client", None)
        if client is None:
            return None, ""
        return client, (getattr(engine, "graph_name", None) or _DEFAULT_GRAPH)
    except Exception as e:  # noqa: BLE001 — engine unreachable
        logger.debug("KG ingest: engine unreachable: %s", e)
        return None, ""


def _local_write_nodes(
    client: Any,
    graph: str,
    nodes: list[dict[str, Any]],
    relationships: list[dict[str, Any]] | None,
) -> dict[str, int] | None:
    """Stamp provenance, MERGE the nodes in one txn, then add the edges."""
    nodes = [n for n in nodes if n.get("id")]
    if not nodes:
        return None
    try:
        txn = client.txn.begin(graph=graph)
        for node in nodes:
            props = {k: v for k, v in node.items() if k != "id" and v is not None}
            props.setdefault("source", _SOURCE)
            props.setdefault("domain", _DOMAIN)
            client.txn.add_node(txn, node["id"], props)
        committed = client.txn.commit(txn)
    except Exception as e:  # noqa: BLE001 — engine/txn failure is non-fatal
        logger.warning("KG ingest: txn failed: %s", e)
        return None
    if not committed:
        logger.warning("KG ingest: txn not committed (conflict)")
        return None

    edges = 0
    for rel in relationships or []:
        try:
            client.edges.add(
                rel["source"], rel["target"], {"type": rel.get("type", "RELATED")}
            )
            edges += 1
        except Exception as e:  # noqa: BLE001 — pure edge link, best-effort
            logger.debug("KG ingest: edge skipped: %s", e)

    logger.info("KG ingest: wrote %d nodes, %d edges", len(nodes), edges)
    return {"nodes": len(nodes), "edges": edges}


def ingest_entities(
    entities: list[dict[str, Any]],
    relationships: list[dict[str, Any]] | None = None,
    *,
    client: Any | None = None,
    graph: str | None = None,
) -> dict[str, int] | None:
    """Write typed OWL nodes (+ edges) into the engine.

    Delegates to the shared ``agent_utilities`` primitive when available (carrying the
    ServiceNow ``source``/``domain`` provenance), otherwise uses the local txn fallback.
    ``client``/``graph`` may be injected (tests); returns ``{"nodes":n, "edges":m}`` or
    ``None`` (no engine / empty / failure; never raises).
    """
    entities = [e for e in (entities or []) if e.get("id")]
    if not entities:
        return None
    if _shared_entities is not None:
        return _shared_entities(
            entities,
            relationships,
            source=_SOURCE,
            domain=_DOMAIN,
            client=client,
            graph=graph,
        )
    if client is None:
        client, graph = _local_client()
    if client is None:
        return None
    return _local_write_nodes(client, graph or _DEFAULT_GRAPH, entities, relationships)


def ingest_documents(
    documents: list[dict[str, Any]],
    *,
    client: Any | None = None,
    graph: str | None = None,
) -> dict[str, int] | None:
    """Write text records as ``:Document`` nodes (semantic-search fodder).

    Each doc: ``{"id":..., "text":..., "title"?:..., "source_uri"?:..., ...props}``.
    Delegates to the shared primitive when available, otherwise the local fallback.
    """
    if not documents:
        return None
    if _shared_documents is not None:
        return _shared_documents(
            documents, source=_SOURCE, domain=_DOMAIN, client=client, graph=graph
        )
    import time

    now = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    nodes: list[dict[str, Any]] = []
    for doc in documents:
        did = doc.get("id")
        text = doc.get("text") or doc.get("content")
        if not did or not text:
            continue
        node = {k: v for k, v in doc.items() if k not in ("content",) and v is not None}
        node["id"] = did
        node["type"] = "Document"
        node["text"] = text
        node.setdefault("created_at", now)
        nodes.append(node)
    if not nodes:
        return None
    if client is None:
        client, graph = _local_client()
    if client is None:
        return None
    return _local_write_nodes(client, graph or _DEFAULT_GRAPH, nodes, None)


def _media_store() -> Any | None:
    """Return a ``MediaStore`` over a live engine (for raw-blob ingestion), or ``None``."""
    if _shared_media_store is not None:
        return _shared_media_store()
    client, _ = _local_client()
    if client is None:
        return None
    try:
        from agent_utilities.knowledge_graph.core.graph_compute import (
            GraphComputeEngine,
        )
        from agent_utilities.knowledge_graph.memory.media_store import MediaStore

        return MediaStore(GraphComputeEngine())
    except Exception as e:  # noqa: BLE001
        logger.debug("KG ingest: media_store unavailable: %s", e)
        return None


# --- ServiceNow field helpers -------------------------------------------------------


def _as_dict(rec: Any) -> dict[str, Any]:
    """Coerce a pydantic record (or dict) into a plain dict."""
    if hasattr(rec, "model_dump"):
        try:
            return rec.model_dump()
        except Exception:  # noqa: BLE001
            return dict(getattr(rec, "__dict__", {}) or {})
    return rec if isinstance(rec, dict) else {}


def _disp(val: Any) -> Any:
    """Human-readable value of a ServiceNow field (ReferenceField dict or scalar)."""
    if isinstance(val, dict):
        return val.get("display_value") or val.get("value") or val.get("name")
    return val


def _ref_id(val: Any) -> Any:
    """Internal sys_id/value of a ServiceNow reference field (or the scalar itself)."""
    if isinstance(val, dict):
        return val.get("value") or val.get("sys_id")
    return val


def _link_ci(
    rec: dict[str, Any],
    source_id: str,
    entities: list[dict[str, Any]],
    relationships: list[dict[str, Any]],
) -> None:
    """Attach the record's ``cmdb_ci`` as a :ConfigurationItem + :affects edge."""
    ci_id = _ref_id(rec.get("cmdb_ci"))
    if not ci_id:
        return
    entities.append(
        {
            "id": f"servicenow:ci:{ci_id}",
            "type": "ConfigurationItem",
            "shortDescription": _disp(rec.get("cmdb_ci")),
            "externalToolId": str(ci_id),
        }
    )
    relationships.append(
        {"source": source_id, "target": f"servicenow:ci:{ci_id}", "type": "affects"}
    )


def _link_assignee(
    rec: dict[str, Any],
    source_id: str,
    entities: list[dict[str, Any]],
    relationships: list[dict[str, Any]],
) -> None:
    """Attach the record's ``assigned_to`` as a :Person + :assignedTo edge."""
    who_id = _ref_id(rec.get("assigned_to"))
    if not who_id:
        return
    entities.append(
        {
            "id": f"servicenow:person:{who_id}",
            "type": "Person",
            "name": _disp(rec.get("assigned_to")),
            "externalToolId": str(who_id),
        }
    )
    relationships.append(
        {
            "source": source_id,
            "target": f"servicenow:person:{who_id}",
            "type": "assignedTo",
        }
    )


# --- Public record → typed-node mappers ---------------------------------------------


def ingest_incidents(
    records: list[Any],
    *,
    client: Any | None = None,
    graph: str | None = None,
) -> dict[str, int] | None:
    """Map ServiceNow incident records → ``:Incident`` (+ CI/Person) nodes and ingest."""
    entities: list[dict[str, Any]] = []
    relationships: list[dict[str, Any]] = []
    for raw in records or []:
        rec = _as_dict(raw)
        sid = rec.get("sys_id")
        if not sid:
            continue
        node_id = f"servicenow:incident:{sid}"
        entities.append(
            {
                "id": node_id,
                "type": "Incident",
                "number": _disp(rec.get("number")),
                "shortDescription": _disp(rec.get("short_description")),
                "state": _disp(rec.get("state")),
                "priority": _disp(rec.get("priority")),
                "impact": _disp(rec.get("impact")),
                "urgency": _disp(rec.get("urgency")),
                "category": _disp(rec.get("category")),
                "opened_at": rec.get("opened_at"),
                "sys_updated_on": rec.get("sys_updated_on"),
                "externalToolId": str(sid),
            }
        )
        _link_ci(rec, node_id, entities, relationships)
        _link_assignee(rec, node_id, entities, relationships)
    return ingest_entities(entities, relationships, client=client, graph=graph)


def ingest_changes(
    records: list[Any],
    *,
    client: Any | None = None,
    graph: str | None = None,
) -> dict[str, int] | None:
    """Map ServiceNow change_request records → ``:Change`` (+ CI/Person) nodes and ingest."""
    entities: list[dict[str, Any]] = []
    relationships: list[dict[str, Any]] = []
    for raw in records or []:
        rec = _as_dict(raw)
        sid = rec.get("sys_id")
        if not sid:
            continue
        node_id = f"servicenow:change:{sid}"
        entities.append(
            {
                "id": node_id,
                "type": "Change",
                "number": _disp(rec.get("number")),
                "shortDescription": _disp(rec.get("short_description")),
                "state": _disp(rec.get("state")),
                "priority": _disp(rec.get("priority")),
                "risk": _disp(rec.get("risk")),
                "type_field": _disp(rec.get("type")),
                "start_date": rec.get("start_date"),
                "end_date": rec.get("end_date"),
                "sys_updated_on": rec.get("sys_updated_on"),
                "externalToolId": str(sid),
            }
        )
        _link_ci(rec, node_id, entities, relationships)
        _link_assignee(rec, node_id, entities, relationships)
    return ingest_entities(entities, relationships, client=client, graph=graph)


def ingest_cmdb(
    records: list[Any],
    *,
    client: Any | None = None,
    graph: str | None = None,
) -> dict[str, int] | None:
    """Map ServiceNow cmdb_ci records → ``:ConfigurationItem`` nodes and ingest."""
    entities: list[dict[str, Any]] = []
    for raw in records or []:
        rec = _as_dict(raw)
        sid = _ref_id(rec.get("sys_id"))
        if not sid:
            continue
        entities.append(
            {
                "id": f"servicenow:ci:{sid}",
                "type": "ConfigurationItem",
                "name": _disp(rec.get("name")),
                "shortDescription": _disp(rec.get("short_description")),
                "sys_class_name": _disp(rec.get("sys_class_name")),
                "operational_status": _disp(rec.get("operational_status")),
                "state": _disp(rec.get("install_status") or rec.get("state")),
                "externalToolId": str(sid),
            }
        )
    return ingest_entities(entities, None, client=client, graph=graph)


def ingest_kb_articles(
    records: list[Any],
    *,
    client: Any | None = None,
    graph: str | None = None,
) -> dict[str, int] | None:
    """Map ServiceNow knowledge-base articles → ``:Document`` nodes (text + source_uri)."""
    docs: list[dict[str, Any]] = []
    for raw in records or []:
        rec = _as_dict(raw)
        aid = rec.get("sys_id") or rec.get("id")
        if not aid:
            continue
        text = (
            rec.get("text")
            or rec.get("content")
            or rec.get("snippet")
            or rec.get("short_description")
        )
        if not text:
            continue
        docs.append(
            {
                "id": f"servicenow:kb:{aid}",
                "subtype": "KnowledgeArticle",
                "title": _disp(rec.get("title")) or _disp(rec.get("short_description")),
                "number": rec.get("number"),
                "text": text,
                "source_uri": rec.get("link"),
                "externalToolId": str(aid),
            }
        )
    return ingest_documents(docs, client=client, graph=graph)


def ingest_attachment(
    data: bytes,
    name: str,
    *,
    mime_type: str | None = None,
    incident_id: str | None = None,
    source_uri: str | None = None,
    media_store: Any | None = None,
) -> dict[str, Any] | None:
    """Store a ticket attachment's raw bytes as a blob + ``:MediaAsset`` in the KG.

    Returns ``{asset_id, digest, size_bytes}`` on success, or ``None`` when there is no
    engine, no data, or the store failed (never raises). ``media_store`` may be injected
    (tests); otherwise one is built on demand.
    """
    if not data:
        return None
    store = media_store if media_store is not None else _media_store()
    if store is None:
        return None

    extra: dict[str, Any] = {}
    if incident_id:
        extra["incident_id"] = incident_id
    if source_uri:
        extra["source_url"] = source_uri

    try:
        stored = store.store_media(
            data,
            media_type="file",
            mime_type=mime_type or "application/octet-stream",
            source=_SOURCE,
            name=name,
            extra=extra,
        )
    except Exception as e:  # noqa: BLE001 — engine/store failure is non-fatal
        logger.warning("KG ingest: store_media failed: %s", e)
        return None
    if stored is None:
        return None

    logger.info(
        "KG ingest: stored attachment %s (%d bytes) as asset %s",
        name,
        len(data),
        getattr(stored, "asset_id", "?"),
    )
    return {
        "asset_id": getattr(stored, "asset_id", None),
        "digest": getattr(stored, "digest", None),
        "size_bytes": len(data),
    }
