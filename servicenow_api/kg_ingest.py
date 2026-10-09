"""Native epistemic-graph ingestion for ServiceNow records and attachments.

Incidents, changes, CMDB items, knowledge documents, and attachment blobs share the
authoritative EG client and media boundary.

All writes go through the ``agent_connector_sdk.ingest`` knowledge-ingest facade (the
generated EG client). Nodes use canonical ``node_type`` and edges use canonical
``relationship``; nodes and edges commit in one submission. Missing engine
dependencies, rejected records, and conflicts propagate as ``IngestError``.
"""

from __future__ import annotations

import hashlib
import logging
from typing import Any

from agent_connector_sdk.ingest import (
    ChangeSet,
    Document,
    Entity,
    IngestBinding,
    IngestError,
    KnowledgeIngest,
    MediaAsset,
    Relationship,
    current_ingest,
)

logger = logging.getLogger("servicenow_api.kg")

_SOURCE = "servicenow-api"
_DOMAIN = "servicenow"
_BINDING = IngestBinding(connector="servicenow-api", stream=_DOMAIN)


def _to_entity(record: dict[str, Any]) -> Entity:
    return Entity(
        id=record.get("id"),
        node_type=record.get("node_type"),
        properties={
            k: v for k, v in record.items() if k not in ("id", "node_type")
        },
    )


def _to_relationship(record: dict[str, Any]) -> Relationship:
    props = {
        k: v
        for k, v in record.items()
        if k not in ("source", "target", "relationship")
    }
    return Relationship(
        source=record["source"],
        target=record["target"],
        relationship=record["relationship"],
        properties=props or None,
    )


def _to_document(record: dict[str, Any]) -> Document:
    return Document(
        id=record.get("id"),
        text=record.get("text", ""),
        title=record.get("title"),
        source_uri=record.get("source_uri"),
        properties={
            k: v
            for k, v in record.items()
            if k not in ("id", "text", "title", "source_uri")
        },
    )


async def ingest_entities(
    entities: list[dict[str, Any]],
    relationships: list[dict[str, Any]] | None = None,
    *,
    ingest: KnowledgeIngest | None = None,
) -> dict[str, int]:
    """Write canonical typed nodes and relationships in one submission."""
    if not entities:
        raise IngestError("ingest_entities needs at least one entity")
    change_set = ChangeSet(
        entities=tuple(_to_entity(e) for e in entities),
        relationships=tuple(_to_relationship(r) for r in relationships or ()),
    )
    service = ingest or current_ingest()
    receipt = await service.submit(_BINDING, change_set)
    return {"nodes": receipt.affected_count, "edges": receipt.relationship_count}


async def ingest_documents(
    documents: list[dict[str, Any]],
    *,
    ingest: KnowledgeIngest | None = None,
) -> dict[str, int]:
    """Write text records as canonical Document nodes."""
    if not documents:
        raise IngestError("ingest_documents needs at least one document")
    change_set = ChangeSet(documents=tuple(_to_document(d) for d in documents))
    service = ingest or current_ingest()
    receipt = await service.submit(_BINDING, change_set)
    return {"nodes": receipt.affected_count, "edges": receipt.relationship_count}


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


async def ingest_incidents(
    records: list[Any],
    *,
    ingest: KnowledgeIngest | None = None,
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
    return await ingest_entities(entities, relationships, ingest=ingest)


async def ingest_changes(
    records: list[Any],
    *,
    ingest: KnowledgeIngest | None = None,
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
    return await ingest_entities(entities, relationships, ingest=ingest)


async def ingest_cmdb(
    records: list[Any],
    *,
    ingest: KnowledgeIngest | None = None,
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
    return await ingest_entities(entities, None, ingest=ingest)


async def ingest_kb_articles(
    records: list[Any],
    *,
    ingest: KnowledgeIngest | None = None,
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
    return await ingest_documents(docs, ingest=ingest)


async def ingest_attachment(
    data: bytes,
    name: str,
    *,
    mime_type: str | None = None,
    incident_id: str | None = None,
    source_uri: str | None = None,
    ingest: KnowledgeIngest | None = None,
) -> dict[str, Any]:
    """Store a ticket attachment's raw bytes as a blob + ``:MediaAsset`` in the KG.

    Returns ``{asset_id, size_bytes}``. Invalid bytes or a commit failure raises
    :class:`IngestError`; ``ingest`` may be injected in tests with a fake transport.
    """
    if not data:
        raise IngestError("ingest requires non-empty bytes")

    properties: dict[str, Any] = {}
    if incident_id:
        properties["incident_id"] = incident_id
    if source_uri:
        properties["source_url"] = source_uri

    asset_id = f"servicenow:attachment:{hashlib.sha256(data).hexdigest()}"
    asset = MediaAsset(
        data=data,
        mime_type=mime_type or "application/octet-stream",
        id=asset_id,
        name=name,
        properties=properties,
    )
    change_set = ChangeSet(media=(asset,))
    service = ingest or current_ingest()
    receipt = await service.submit(_BINDING, change_set)

    logger.info(
        "KG ingest: stored attachment %s (%d bytes)",
        name,
        len(data),
    )
    return {
        "asset_id": asset.id,
        "size_bytes": len(data),
        "affected_count": receipt.affected_count,
    }
