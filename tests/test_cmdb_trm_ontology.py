"""CMDB and TRM ontology classes, edges, shapes and ingest sources (CONN-SERVICENOW-API-CONNECTOR-CONTENT-R004, R005)."""

from __future__ import annotations

from pathlib import Path

import pytest
from servicenow_api.connector_sources import declaration as declared_sources
from agent_connector_sdk.mcp.method_tools import operation_annotations, operation_verb
from agent_connector_sdk.mcp.tool_surface import operation_prefix

import servicenow_api
from servicenow_api.api.api_client_change import ServiceNowApiChange
from servicenow_api.api.api_client_system import ServiceNowApiSystem
from tests.test_ontology_parent_link import (
    ONTOLOGIES,
    PARENT_CLASSES,
    SUBCLASS,
    _triples,
)

PACKAGE = Path(servicenow_api.__file__).parent
KG = "http://knuckles.team/kg#"
# new class -> the parent class (epistemic-graph or this pack) it must extend
NEW_CLASSES = {
    "CmdbServer": "ConfigurationItem",
    "CmdbApplication": "ConfigurationItem",
    "BusinessApplication": "CmdbApplication",
    "CmdbBusinessService": "ConfigurationItem",
    "CIRelationship": "JunctionLink",
    "AssignmentGroup": "Organization",
    "ChangeRequest": "Change",
    "TRMStandard": "TechnologyStandard",
    "TRMCategory": "Concept",
    "TRMPhase": "Concept",
    "TRMLifecycle": "TechnologyStandard",
    "TRMTechnicalDebt": "Concept",
    "TechnologyRequest": "TRMRequest",
    "LifecycleRequest": "TechnologyRequest",
}
EDGES = (
    "usesTechnology",
    "touches",
    "inCategory",
    "requestsTechnology",
    "hostedOn",
    "hasPhase",
    "lifecycleOf",
    "lifecyclePhase",
    "debtOn",
    "debtOfApplication",
)
# source id -> (record type, ServiceNow table)
SOURCES = {
    "cmdb-cis": ("ConfigurationItem", "cmdb_ci"),
    "cmdb-ci-relationships": ("CIRelationship", "cmdb_rel_ci"),
    "trm-standards": ("TRMStandard", "sn_apm_trm_standards_product"),
    "trm-categories": ("TRMCategory", "sn_apm_trm_standards_category"),
    "trm-phases": ("TRMPhase", "sn_apm_trm_standards_phase"),
    "trm-lifecycles": ("TRMLifecycle", "sn_apm_trm_standards_product_lifecycle"),
    "trm-technical-debt": ("TRMTechnicalDebt", "sn_apm_trm_standards_technical_debt"),
    "trm-requests": ("TechnologyRequest", "sn_apm_trm_product_request"),
    "trm-lifecycle-requests": (
        "LifecycleRequest",
        "sn_apm_trm_product_lifecycle_request",
    ),
}
CLIENTS = {
    "servicenow_get_table": (ServiceNowApiSystem, "get_table"),
    "servicenow_get_change_requests": (ServiceNowApiChange, "get_change_requests"),
}


def _pack() -> list[tuple[str, str, str]]:
    path = next(p for p in ONTOLOGIES if p.name == "servicenow.ttl")
    return _triples(path.read_text(encoding="utf-8"))


@pytest.mark.spec("CONN-SERVICENOW-API-CONNECTOR-CONTENT-R004")
def test_new_classes_extend_their_parent() -> None:
    triples = _pack()
    for name, parent in NEW_CLASSES.items():
        assert (KG + name, SUBCLASS, KG + parent) in triples, name
    # No new class is an orphan: each chain ends in a parent-ontology class.
    for name in NEW_CLASSES:
        cursor, seen = KG + name, set()
        while cursor not in PARENT_CLASSES:
            assert cursor not in seen, f"{name} loops"
            seen.add(cursor)
            ups = [o for s, p, o in triples if s == cursor and p == SUBCLASS]
            assert ups, f"{name} is an orphan"
            cursor = ups[0]


@pytest.mark.spec("CONN-SERVICENOW-API-CONNECTOR-CONTENT-R004")
def test_edges_connect_declared_classes() -> None:
    triples = _pack()
    declared = {s for s, p, o in triples if o.endswith("#Class")}
    for edge in EDGES:
        assert any(s == KG + edge for s, _, _ in triples), edge
    for s, p, o in triples:
        if s.startswith(KG) and p.endswith(("#domain", "#range")) and o.startswith(KG):
            local = o.removeprefix(KG)
            assert o in declared or o in PARENT_CLASSES or local in {"Person"}, o


@pytest.mark.spec("CONN-SERVICENOW-API-CONNECTOR-CONTENT-R004")
def test_manifest_maps_and_shapes_cover_new_types() -> None:
    shapes = (PACKAGE / "ontology" / "shapes" / "connector.shacl.ttl").read_text(
        "utf-8"
    )
    for name, parent in NEW_CLASSES.items():
        assert name in declared_sources().schema_mappings, name
        assert declared_sources().schema_mappings[name].ontology_class == parent
    for name in (
        "CIRelationship",
        "AssignmentGroup",
        "ChangeRequest",
        "TRMStandard",
        "TRMCategory",
        "TRMPhase",
        "TRMLifecycle",
        "TRMTechnicalDebt",
        "TechnologyRequest",
        "LifecycleRequest",
    ):
        assert f"sh:targetClass :{name} " in shapes, name


@pytest.mark.spec("CONN-SERVICENOW-API-CONNECTOR-CONTENT-R005")
def test_ingest_sources_name_read_only_tools_and_mapped_types() -> None:
    declaration = declared_sources()
    assert declaration is not None
    prefix = operation_prefix("servicenow-api")
    ids = {k: v[0] for k, v in SOURCES.items()}
    ids["change-requests"] = "ChangeRequest"
    for source_id, record_type in ids.items():
        source = declaration.source(source_id)
        assert source is not None, source_id
        assert source.record_type == record_type
        assert record_type in declared_sources().schema_mappings
        for tool in source.tools:
            cls, method_name = CLIENTS[f"{prefix}_{tool.removeprefix(prefix + '_')}"]
            annotations = operation_annotations(
                method_name, operation_verb(getattr(cls, method_name))
            )
            assert annotations.read_only_hint is True, tool
    tables = {
        s.source_id: s.arguments.get("table")
        for s in declaration.sources
        if s.tools == (f"{prefix}_get_table",)
    }
    for source_id, (_, table) in SOURCES.items():
        assert tables[source_id] == table, source_id
    assert not {
        "cmdb_software_product_model",
        "cmdb_model_category",
        "dmn_demand",
    } & set(tables.values())
