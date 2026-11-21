"""CONN-SERVICENOW-API-CONNECTOR-CONTENT-R011: the packaged ontology extends only the medulla core ontology."""

import re
from pathlib import Path

import pytest

ONTOLOGY = Path(__file__).resolve().parents[1] / "servicenow_api" / "ontology"
CONNECTOR_NAMESPACES = ('https://knuckles-team.github.io/ontology/connector/servicenow#',)
CORE_TERMS = ('AssignmentGroup', 'BusinessApplication', 'ChangeRequest', 'ConfigurationItem', 'Incident', 'Person', 'TRMPhase', 'TRMStandard', 'affects', 'assignedTo', 'hasPhase', 'hostedOn', 'lifecyclePhase', 'priority', 'relationshipType', 'state', 'touches', 'usesTechnology')
OLD_BASE = re.compile(r"knuckles\.team/kg|http://knuckles\.team")


def _files() -> list[Path]:
    return sorted(ONTOLOGY.glob("**/*.ttl"))


def _subjects(text: str) -> set[str]:
    """Full IRIs of every statement subject written under a connector namespace."""
    found = set()
    for namespace in CONNECTOR_NAMESPACES:
        prefixes = re.findall(r"@prefix\s+(\w*):\s*<" + re.escape(namespace) + ">", text)
        for prefix in prefixes:
            for match in re.finditer(r"^" + re.escape(prefix) + r":([\w-]+)\s", text, re.M):
                found.add(namespace + match.group(1))
        for match in re.finditer(r"^<" + re.escape(namespace) + r"([\w-]+)>", text, re.M):
            found.add(namespace + match.group(1))
    return found


@pytest.mark.spec("CONN-SERVICENOW-API-CONNECTOR-CONTENT-R011")
def test_pack_declares_no_core_term():
    """No core class or property is redeclared under a connector namespace."""
    subjects = set().union(*(_subjects(p.read_text()) for p in _files()))
    redeclared = sorted(
        namespace + term
        for namespace in CONNECTOR_NAMESPACES
        for term in CORE_TERMS
        if namespace + term in subjects
    )
    assert redeclared == []


@pytest.mark.spec("CONN-SERVICENOW-API-CONNECTOR-CONTENT-R011")
def test_pack_uses_the_one_iri_base():
    """No packaged ontology file carries the retired IRI base."""
    stale = [p.name for p in _files() if OLD_BASE.search(p.read_text())]
    assert stale == []
