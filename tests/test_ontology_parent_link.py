"""Every class of the packaged ontology reaches an epistemic-graph parent class (CONN-SERVICENOW-API-CONNECTOR-CONTENT-R002)."""

from __future__ import annotations

from pathlib import Path

import pytest
from rdflib import OWL, RDF, RDFS, Graph, URIRef

pytestmark = pytest.mark.spec("CONN-SERVICENOW-API-CONNECTOR-CONTENT-R002")

PARENT_IRI = URIRef("http://knuckles.team/kg")
ONTOLOGIES = sorted(
    (Path(__file__).resolve().parents[1] / "servicenow_api" / "ontology").glob("*.ttl")
)
# Parent classes of the epistemic-graph ontology that this connector links to or redeclares.
PARENT_CLASSES = frozenset(
    URIRef(iri)
    for iri in (
        "http://knuckles.team/kg#AssetInstance",
        "http://knuckles.team/kg#Change",
        "http://knuckles.team/kg#Document",
        "http://knuckles.team/kg#Incident",
        "http://knuckles.team/kg#Person",
    )
)
# Classes for which the parent ontology has no fitting class yet. Each is a candidate for a new
# parent class (see the orphan mapping report); a class leaves this set when it gains a parent.
PENDING_NEW_PARENT: frozenset[URIRef] = frozenset()


def _orphans(graph: Graph) -> set[URIRef]:
    declared = {s for s in graph.subjects(RDF.type, OWL.Class) if isinstance(s, URIRef)}
    linked: set[URIRef] = set()
    changed = True
    while changed:
        changed = False
        for cls in declared - linked - PARENT_CLASSES:
            if any(
                up in PARENT_CLASSES or up in linked
                for up in graph.objects(cls, RDFS.subClassOf)
            ):
                linked.add(cls)
                changed = True
    return declared - linked - PARENT_CLASSES


@pytest.mark.parametrize("path", ONTOLOGIES, ids=lambda p: p.name)
def test_ontology_joins_the_parent_graph(path: Path) -> None:
    graph = Graph().parse(path, format="turtle")
    if not any(graph.subjects(RDF.type, OWL.Class)):
        pytest.skip("declares no classes")
    imports = set(graph.objects(None, OWL.imports))
    assert any(
        str(i) == str(PARENT_IRI) or str(i).startswith(str(PARENT_IRI) + "/")
        for i in imports
    )
    assert _orphans(graph) == {
        c for c in PENDING_NEW_PARENT if (c, RDF.type, OWL.Class) in graph
    }
