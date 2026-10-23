"""Every class of the packaged ontology reaches an epistemic-graph parent class (CONN-SERVICENOW-API-CONNECTOR-CONTENT-R002)."""

from __future__ import annotations

import re
from pathlib import Path

import pytest

pytestmark = pytest.mark.spec("CONN-SERVICENOW-API-CONNECTOR-CONTENT-R002")

PARENT_IRI = "http://knuckles.team/kg"
ONTOLOGIES = sorted(
    (Path(__file__).resolve().parents[1] / "servicenow_api" / "ontology").glob("*.ttl")
)
OWL = "http://www.w3.org/2002/07/owl#"
RDF_TYPE = "http://www.w3.org/1999/02/22-rdf-syntax-ns#type"
SUBCLASS = "http://www.w3.org/2000/01/rdf-schema#subClassOf"
# Parent classes of the epistemic-graph ontology that this connector links to or redeclares.
PARENT_CLASSES = frozenset(
    (
        "http://knuckles.team/kg#AssetInstance",
        "http://knuckles.team/kg#Change",
        "http://knuckles.team/kg#Concept",
        "http://knuckles.team/kg#Document",
        "http://knuckles.team/kg#Incident",
        "http://knuckles.team/kg#JunctionLink",
        "http://knuckles.team/kg#Organization",
        "http://knuckles.team/kg#Person",
        "http://knuckles.team/kg#TRMRequest",
        "http://knuckles.team/kg#TechnologyStandard",
    )
)
# Classes for which the parent ontology has no fitting class yet. Each is a candidate for a new
# parent class (see the orphan mapping report); a class leaves this set when it gains a parent.
PENDING_NEW_PARENT: frozenset[str] = frozenset()

_STRING = re.compile(r'"""(?:.|\n)*?"""|"(?:[^"\\\n]|\\.)*"')
_IRI = re.compile(r"<([^<>\s]*)>")
_PREFIX = re.compile(r"(?im)^\s*@?prefix\s+([A-Za-z][\w.-]*)?:\s+\x00(\d+)\s*\.?")
_END = re.compile(r"\s\.(?=\s|$)|(?<=[\]>)\w\"'])\.(?=\s|$)")


def _triples(text: str) -> list[tuple[str, str, str]]:
    """Subject, predicate and object of a Turtle file; names are expanded, literals dropped."""
    iris: list[str] = []

    def keep(match: re.Match[str]) -> str:
        iris.append(match.group(1))
        return f" \x00{len(iris)} "

    body = re.sub(r"(?m)#[^\n]*$", "", _IRI.sub(keep, _STRING.sub(' "" ', text)))
    prefixes = {
        m.group(1) or "": iris[int(m.group(2)) - 1] for m in _PREFIX.finditer(body)
    }
    body = re.sub(r"\[[^\[\]]*\]", " _:b ", _PREFIX.sub("", body))

    def expand(token: str) -> str:
        if token.startswith("\x00"):
            return iris[int(token[1:]) - 1]
        prefix, sep, local = token.partition(":")
        return (
            prefixes[prefix] + local
            if sep and prefix in prefixes
            else RDF_TYPE if token == "a" else token
        )

    triples: list[tuple[str, str, str]] = []
    for statement in _END.split(body):
        tokens = statement.replace(";", " ; ").replace(",", " , ").split()
        subject, predicate, fresh = "", "", True
        for index, token in enumerate(tokens):
            if index == 0:
                subject = expand(token)
            elif token == ";":
                fresh = True
            elif token != ",":
                if fresh:
                    predicate, fresh = expand(token), False
                else:
                    triples.append((subject, predicate, expand(token)))
    return triples


def _orphans(triples: list[tuple[str, str, str]]) -> set[str]:
    declared = {s for s, p, o in triples if p == RDF_TYPE and o == OWL + "Class"}
    linked: set[str] = set()
    changed = True
    while changed:
        changed = False
        for cls in declared - linked - PARENT_CLASSES:
            ups = {o for s, p, o in triples if s == cls and p == SUBCLASS}
            if ups & (PARENT_CLASSES | linked):
                linked.add(cls)
                changed = True
    return declared - linked - PARENT_CLASSES


@pytest.mark.parametrize("path", ONTOLOGIES, ids=lambda p: p.name)
def test_ontology_joins_the_parent_graph(path: Path) -> None:
    triples = _triples(path.read_text(encoding="utf-8"))
    declared = {s for s, p, o in triples if p == RDF_TYPE and o == OWL + "Class"}
    if not declared:
        pytest.skip("declares no classes")
    imports = {o for s, p, o in triples if p == OWL + "imports"}
    assert any(i == PARENT_IRI or i.startswith(PARENT_IRI + "/") for i in imports)
    assert _orphans(triples) == PENDING_NEW_PARENT & declared
