"""The served tool surface is typed: one tool per operation, no action routing,
and the packaged prompts and access contracts name only tools that are served."""

import asyncio
import json
import re
from pathlib import Path

import pytest

PKG = Path(__file__).resolve().parent.parent / "servicenow_api"


@pytest.fixture(scope="module")
def served_tools():
    from scion_sdk.connector import build_server

    _, mcp = build_server("servicenow_api", command_args=[])
    return asyncio.run(mcp.list_tools())


def test_no_served_tool_routes_an_action_string(served_tools):
    routed = [
        t.name
        for t in served_tools
        if "action" in (t.parameters or {}).get("properties", {})
    ]
    assert routed == []


def test_prompts_and_access_contracts_name_served_tools(served_tools):
    served = {t.name for t in served_tools}
    named: set[str] = set()
    for prompt in (PKG / "prompts").glob("*.json"):
        named.update(json.loads(prompt.read_text()).get("tools", []))
    contracts = (PKG / "ontology" / "access_contracts.ttl").read_text()
    named.update(re.findall(r'ac:operation "([^"]+)"', contracts))
    assert sorted(named - served) == []
