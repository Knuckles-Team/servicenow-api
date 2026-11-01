# CONN-SERVICENOW-API-CONNECTOR-CONTENT — Test specification

Governing spec: [spec.md](spec.md).

| Test ID | Requirement | Proving test | Expected observation |
|---|---|---|---|
| T-001 | `CONN-SERVICENOW-API-CONNECTOR-CONTENT-R001` | `tests/test_default_content_surfaces.py::test_default_content_surfaces` (planned) | `resources/list` includes `skill://` and `ontology://`; `prompts/list` includes each packaged prompt. |
| T-002 | `CONN-SERVICENOW-API-CONNECTOR-CONTENT-R002` | `tests/test_ontology_parent_link.py::test_ontology_joins_the_parent_graph` | The test parses each ontology and finds no orphan class beyond the pending list. |
| T-003 | `CONN-SERVICENOW-API-CONNECTOR-CONTENT-R003` | `tests/test_ingest_sources.py::test_declares_ingestible_sources` | The declaration loads through the SDK, names the tool and the mapped record type, and the read-only annotation holds. |
| T-004 | `CONN-SERVICENOW-API-CONNECTOR-CONTENT-R004` | `tests/test_cmdb_trm_ontology.py::test_new_classes_extend_their_parent` | No declared class is an orphan, every new type is a `schema_mappings` key and a shape target, and the edges name classes this ontology declares. |
| T-005 | `CONN-SERVICENOW-API-CONNECTOR-CONTENT-R005` | `tests/test_cmdb_trm_ontology.py::test_ingest_sources_name_read_only_tools_and_mapped_types` | Every source names a read-only tool, the table named above and a mapped record type. |
| T-006 | `CONN-SERVICENOW-API-CONNECTOR-CONTENT-R006` | `tests/test_cq_paths.py::test_shared_concepts_are_not_redeclared` | The test finds no shared-concept declaration, the incident domains, the host edge span and no null mapping. |
| T-007 | `CONN-SERVICENOW-API-CONNECTOR-CONTENT-R007` | `tests/test_catalog_edges.py::test_every_declared_edge_is_an_ontology_property_of_its_record_type` | `tests/test_catalog_edges.py::test_every_declared_edge_is_an_ontology_property_of_its_record_type` and `::test_incident_references_become_owner_group_and_ci_edges` and `::test_change_and_knowledge_sources_read_their_tables_through_the_table_tool`. |
| T-008 | `CONN-SERVICENOW-API-CONNECTOR-CONTENT-R008` | `tests/test_access_contracts.py::test_competency_contracts_certified` (planned) | Test: `tests/test_access_contracts.py::test_competency_contracts_certified` (L2) runs the connector ontology certification and validates each recording against its contract. |

## Negative and boundary cases

Each proving test above includes the refusal or error case that its row names. A vendor outage or an unauthorised call must return the SDK typed error.

## Quality and release proof

Run `uv run pytest tests` and `pre-commit run --all-files` from the repository root. A planned test is added by the code change that lands the row.
