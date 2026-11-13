"""Access contracts bind fields the served read tools return."""

import asyncio
import json
from pathlib import Path

import pytest
from fastmcp import Client
from scion_sdk.access_contract import parse_access_contracts
from scion_sdk.connector import build_server

from tests.conftest import MockResponse, MockSession

ROOT = Path(__file__).resolve().parents[1]
ONTOLOGY = ROOT / "servicenow_api/ontology"


def _contracts():
    text = (ONTOLOGY / "access_contracts.ttl").read_text()
    return {c.entity: c for c in parse_access_contracts(text)}


@pytest.mark.spec("CONN-SERVICENOW-API-CONNECTOR-CONTENT-R008")
def test_competency_contracts_certified(monkeypatch):
    contract = _contracts()["incident"]
    recording = json.loads((ROOT / "tests/recordings/incident.json").read_text())
    ontology = (ONTOLOGY / "servicenow.ttl").read_text()
    fields = {"cmdb_ci", "state", "number", "priority"}
    assert contract.access_kind == "mcp_tool"
    assert contract.key_field == "sys_id"
    assert contract.pagination == "offset"
    assert {field for _, field in contract.predicates} == fields
    for prop, _ in contract.predicates:
        local = prop.rsplit("#", 1)[-1]
        assert f":{local} a owl:DatatypeProperty" in ontology

    monkeypatch.setenv("SERVICENOW_INSTANCE", "https://fixture.invalid/api")
    monkeypatch.setenv("SERVICENOW_USERNAME", "fixture-user")
    monkeypatch.setenv(
        "SERVICENOW_PASSWORD", "fixture-pass"
    )  # sanitizer:ignore - synthetic fixture
    monkeypatch.setattr(
        MockSession,
        "get",
        lambda self, url, params=None, **kw: MockResponse(recording, 200),
    )

    async def call():
        _, mcp = build_server("servicenow_api", command_args=[])
        async with Client(mcp) as client:
            return await client.call_tool(contract.operation, {})

    result = asyncio.run(call())
    payload = result.data if result.data is not None else result.structured_content
    records = payload["result"]
    assert records
    for record in records:
        assert contract.key_field in record
        assert all(field in record for field in fields)
