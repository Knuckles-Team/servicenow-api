# CONN-SERVICENOW-API-CONNECTOR-CONTENT — Test specification

Governing spec: [spec.md](spec.md).

| Test ID | Requirement | Proving test | Expected observation |
|---|---|---|---|
| T-001 | `CONN-SERVICENOW-API-CONNECTOR-CONTENT-R001` | `tests/test_default_content_surfaces.py` | The listings include the packaged skills, ontology and prompts. |
| T-002 | `CONN-SERVICENOW-API-CONNECTOR-CONTENT-R002` | `tests/test_ontology_parent_link.py` | Every declared class reaches a parent class; the import of the parent IRI is present. |
| T-003 | `CONN-SERVICENOW-API-CONNECTOR-CONTENT-R003` | `tests/test_ingest_sources.py` | The declaration loads, names the read-only incidents tool and a mapped record type. |
| T-004 | `CONN-SERVICENOW-API-CONNECTOR-CONTENT-R004` | `tests/test_cmdb_trm_ontology.py` | New classes reach a parent, are mapped in the manifest and have shapes. |
| T-005 | `CONN-SERVICENOW-API-CONNECTOR-CONTENT-R005` | `tests/test_cmdb_trm_ontology.py` | Each ingest source names a read-only tool and a mapped record type. |
| T-006 | `CONN-SERVICENOW-API-CONNECTOR-CONTENT-R006` | `tests/test_cq_paths.py` | No shared concept is redeclared; incident properties have domains; no null mapping. |
| T-007 | `CONN-SERVICENOW-API-CONNECTOR-CONTENT-R007` | `tests/test_catalog_edges.py` | Every declared edge is an ontology property of its record type; incident references become group, assignee and CI edges; the change and knowledge sources call their tools with accepted arguments. |
