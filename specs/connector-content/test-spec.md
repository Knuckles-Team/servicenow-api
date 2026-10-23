# CONN-SERVICENOW-API-CONNECTOR-CONTENT — Test specification

Governing spec: [spec.md](spec.md).

| Test ID | Requirement | Proving test | Expected observation |
|---|---|---|---|
| T-001 | `CONN-SERVICENOW-API-CONNECTOR-CONTENT-R001` | `tests/test_default_content_surfaces.py` | The listings include the packaged skills, ontology and prompts. |
| T-002 | `CONN-SERVICENOW-API-CONNECTOR-CONTENT-R002` | `tests/test_ontology_parent_link.py` | Every declared class reaches a parent class; the import of the parent IRI is present. |
