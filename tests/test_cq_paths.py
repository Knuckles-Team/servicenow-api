"""Competency-question paths of the ServiceNow pack (CONN-SERVICENOW-API-CONNECTOR-CONTENT-R006)."""

from __future__ import annotations

from scion_sdk.ingest import load_declaration
import re
from pathlib import Path

import pytest

import servicenow_api

pytestmark = pytest.mark.spec("CONN-SERVICENOW-API-CONNECTOR-CONTENT-R006")

PACKAGE = Path(servicenow_api.__file__).parent
TTL = (PACKAGE / "ontology" / "servicenow.ttl").read_text("utf-8")
# Concepts the epistemic-graph ontology and other packs own: referenced, never declared here.
SHARED = ("Server", "Application", "BusinessService", "Change")


def _block(name: str) -> str:
    match = re.search(rf"^:{name} a [^\n]*\n(?:[^\n]+\n)*", TTL, flags=re.M)
    assert match, name
    return match.group(0)


@pytest.mark.parametrize("name", SHARED)
def test_shared_concepts_are_not_redeclared(name: str) -> None:
    assert not re.search(rf"^:{name} a owl:Class", TTL, flags=re.M), name


@pytest.mark.parametrize(
    ("name", "shared"),
    (
        ("CmdbServer", "Server"),
        ("CmdbApplication", "Application"),
        ("CmdbBusinessService", "BusinessService"),
    ),
)
def test_subtypes_join_the_configuration_item_and_shared_concept(
    name: str, shared: str
) -> None:
    block = _block(name)
    assert ":ConfigurationItem" in block
    assert f":{shared}" in block


@pytest.mark.parametrize("prop", ("affects", "priority", "state"))
def test_incident_properties_carry_an_incident_domain(prop: str) -> None:
    block = _block(prop)
    assert re.search(r"rdfs:domain \[ a owl:Class ; owl:unionOf \( :Incident ", block)


def test_host_edge_spans_application_and_server() -> None:
    block = _block("hostedOn")
    assert block.count(":Application :Server") == 2


def test_no_mapping_has_a_null_ontology_class() -> None:
    unmapped = [
        name
        for name, mapping in load_declaration("servicenow_api").schema_mappings.items()
        if not mapping.ontology_class
    ]
    assert unmapped == []
