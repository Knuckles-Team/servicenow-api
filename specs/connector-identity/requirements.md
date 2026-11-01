# CONN-SERVICENOW-API-CONNECTOR-IDENTITY — Requirements

Governing spec: [spec.md](spec.md).

Each row is one requirement. A row names the file it touches and the test that proves it. The generator sets each row's state in `status.json`.

| ID | Requirement | Acceptance |
|---|---|---|
| `CONN-SERVICENOW-API-CONNECTOR-IDENTITY-R001` | **Fleet name.** `pyproject.toml` declares `servicenow-mcp` as the single `scion_sdk.connector` entry point. The content pack, the manifest `connector`, the fingerprints and the ingest binding all carry `servicenow-mcp`. Caller chain: `servicenow-mcp` in `pyproject.toml` runs `scion_sdk.cli:serve`, which builds the server from the `scion_sdk.connector` entry point `servicenow_api:connector` (`servicenow_api/__init__.py:10`); `connector_name("servicenow_api")` in the SDK resolves the same entry point name for the content pack, the manifest and the ingest binding. Shape: `pyproject.toml` entry point `servicenow-mcp`, the `connector_name` helper of the SDK and the `ConnectorContent`/`IngestBinding` calls under `servicenow_api/`; reuses the SDK name resolution and adds no second constant. Proving test: `tests/test_fleet_name.py::test_connector_name_is_the_fleet_name`. | Every connector name in the package is `servicenow-mcp`. |
