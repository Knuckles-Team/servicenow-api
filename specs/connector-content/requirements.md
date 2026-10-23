# CONN-SERVICENOW-API-CONNECTOR-CONTENT — Requirements

Governing spec: [spec.md](spec.md).

Each row is one requirement. A row names the file it touches and the test that proves it. The generator sets each row's state in `status.json`.

| ID | Requirement | Acceptance |
|---|---|---|
| `CONN-SERVICENOW-API-CONNECTOR-CONTENT-R001` | **Default content.** `pyproject.toml` declares `servicenow-mcp` as the single `agent_connector_sdk.connector` entry point. The server lists the packaged `skill://` and `ontology://` resources and the packaged prompts with no `content=` argument. Proving test: `tests/test_default_content_surfaces.py`. | `resources/list` includes `skill://` and `ontology://`; `prompts/list` includes each packaged prompt. |
| `CONN-SERVICENOW-API-CONNECTOR-CONTENT-R002` | **Ontology joins the parent graph.** Each `<package>/ontology/*.ttl` that declares classes imports `http://knuckles.team/kg`, and each class reaches an epistemic-graph parent class through `rdfs:subClassOf`. Proving test: `tests/test_ontology_parent_link.py`. | The test parses each ontology and finds no orphan class beyond the pending list. |
