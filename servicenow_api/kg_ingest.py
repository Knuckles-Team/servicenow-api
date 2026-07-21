"""Native epistemic-graph ingestion for ServiceNow records and attachments.

Incidents, changes, CMDB items, knowledge documents, and attachment blobs share the
authoritative native graph and media-store boundary.

All writes use the required ``agent_utilities.knowledge_graph.memory.native_ingest``
primitive. Nodes use canonical ``node_type`` and edges use canonical ``relationship``;
nodes and edges commit in one native transaction. Missing engine dependencies, rejected
records, conflicts, and transaction failures propagate as ``NativeIngestError``.
"""

from __future__ import annotations

import logging
from typing import Any

from agent_utilities.knowledge_graph.memory.native_ingest import NativeIngestError
from agent_utilities.knowledge_graph.memory.native_ingest import (
    ingest_documents as _native_ingest_documents,
)
from agent_utilities.knowledge_graph.memory.native_ingest import (
    ingest_entities as _native_ingest_entities,
)
from agent_utilities.knowledge_graph.memory.native_ingest import (
    media_store as _native_media_store,
)

logger = logging.getLogger("servicenow_api.kg")

_SOURCE = "servicenow-api"
_DOMAIN = "servicenow"


def ingest_entities(
    entities: list[dict[str, Any]],
    relationships: list[dict[str, Any]] | None = None,
    *,
    source: str = _SOURCE,
    domain: str = _DOMAIN,
    client: Any | None = None,
    graph: str | None = None,
) -> dict[str, int]:
    """Write canonical typed nodes and relationships in one native transaction."""
    return _native_ingest_entities(
        entities,
        relationships,
        source=source,
        domain=domain,
        client=client,
        graph=graph,
    )


def ingest_documents(
    documents: list[dict[str, Any]],
    *,
    source: str = _SOURCE,
    domain: str = _DOMAIN,
    client: Any | None = None,
    graph: str | None = None,
) -> dict[str, int]:
    """Write text records as canonical Document nodes."""
    return _native_ingest_documents(
        documents, source=source, domain=domain, client=client, graph=graph
    )


def _media_store() -> Any:
    """Return the authoritative native media store."""
    return _native_media_store()


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
            "node_type": "ConfigurationItem",
            "shortDescription": _disp(rec.get("cmdb_ci")),
            "externalToolId": str(ci_id),
        }
    )
    relationships.append(
        {
            "source": source_id,
            "target": f"servicenow:ci:{ci_id}",
            "relationship": "affects",
        }
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
            "node_type": "Person",
            "name": _disp(rec.get("assigned_to")),
            "externalToolId": str(who_id),
        }
    )
    relationships.append(
        {
            "source": source_id,
            "target": f"servicenow:person:{who_id}",
            "relationship": "assignedTo",
        }
    )


# --- Public record → typed-node mappers ---------------------------------------------


def ingest_incidents(
    records: list[Any],
    *,
    client: Any | None = None,
    graph: str | None = None,
) -> dict[str, int]:
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
                "node_type": "Incident",
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
) -> dict[str, int]:
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
                "node_type": "Change",
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
) -> dict[str, int]:
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
                "node_type": "ConfigurationItem",
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
) -> dict[str, int]:
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
) -> dict[str, Any]:
    """Store a ticket attachment's raw bytes as a blob + ``:MediaAsset`` in the KG.

    Returns ``{asset_id, digest, size_bytes}``. Invalid bytes or a storage failure raises
    :class:`NativeIngestError`; ``media_store`` may be injected in tests.
    """
    if not data:
        raise NativeIngestError("native media ingest requires non-empty bytes")
    store = media_store if media_store is not None else _media_store()

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
    except Exception as exc:  # noqa: BLE001 - preserve retryable cause privately
        raise NativeIngestError("native media ingest transaction failed") from exc
    if stored is None:
        raise NativeIngestError("native media ingest was not committed")

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
