# CONN-SERVICENOW-API-CONNECTOR-IDENTITY — Requirements

Governing spec: [spec.md](spec.md).

Each row is one requirement. A row names the file it touches and the test that proves it. The generator sets each row's state in `status.json`.

| ID | Requirement | Acceptance |
|---|---|---|
| `CONN-SERVICENOW-API-CONNECTOR-IDENTITY-R001` | **Fleet name.** `pyproject.toml` declares `servicenow-mcp` as the single `agent_connector_sdk.connector` entry point. The content pack, the manifest `connector`, the fingerprints and the ingest binding all carry `servicenow-mcp`. Proving test: `tests/test_fleet_name.py::test_connector_name_is_the_fleet_name`. | Every connector name in the package is `servicenow-mcp`. |
