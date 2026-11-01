# CONN-SERVICENOW-API-CONNECTOR-CONTENT — The connector serves its packaged content

Owner: servicenow-api. Cross-repo IDs: `SCION-CONNECTOR-CONTROL-R071`, `SCION-CONNECTOR-CONTROL-R073`.

## Purpose and user stories

The `servicenow-mcp` server serves its packaged skills, prompts and ontology to any client, with no wiring of its own.

## Delivery mapping

Component: servicenow-api connector

Code: ../../servicenow_api/__init__.py

## Why a new spec

Searched `specs/` of `servicenow-api` with `git grep` for the terms of this spec. No other spec of this repository owns the capability, so this spec owns it.

## User Scenarios & Testing

### User Story 1 - Default content (Priority: P1)

The fleet operator and the engine rely on this behaviour of `servicenow-api`: `pyproject.toml` declares `servicenow-mcp` as the single `scion_sdk.connector` entry point. It is proven independently of the other stories.

**Acceptance Scenarios**:

1. **Given** the `servicenow-api` connector built from the default branch, **When** `tests/test_default_content_surfaces.py::test_default_content_surfaces` runs, **Then** `resources/list` includes `skill://` and `ontology://`; `prompts/list` includes each packaged prompt.

### User Story 2 - Ontology joins the parent graph (Priority: P1)

The fleet operator and the engine rely on this behaviour of `servicenow-api`: Each `<package>/ontology/*.ttl` that declares classes imports `http://knuckles.team/kg`, and each class reaches an medulla parent class through `rdfs:subClassOf`. It is proven independently of the other stories.

**Acceptance Scenarios**:

1. **Given** the `servicenow-api` connector built from the default branch, **When** `tests/test_ontology_parent_link.py::test_ontology_joins_the_parent_graph` runs, **Then** the test parses each ontology and finds no orphan class beyond the pending list.

### User Story 3 - Declared ingest sources (Priority: P1)

The fleet operator and the engine rely on this behaviour of `servicenow-api`: `servicenow_api/ontology/ingest_sources.json` declares the `incidents` source (record type `Incident`, read-only tool `servicenow_get_incidents`, first 50 records) for the connector `servicenow-mcp`, and the record type is a key of the connector manifest `schema_mappings`. It is proven independently of the other stories.

**Acceptance Scenarios**:

1. **Given** the `servicenow-api` connector built from the default branch, **When** `tests/test_ingest_sources.py::test_declares_ingestible_sources` runs, **Then** the declaration loads through the SDK, names the tool and the mapped record type, and the read-only annotation holds.

### User Story 4 - CMDB and TRM ontology (Priority: P2)

The fleet operator and the engine rely on this behaviour of `servicenow-api`: `servicenow.ttl` declares `CmdbServer`, `CmdbApplication` (parent of `BusinessApplication`) and `CmdbBusinessService` under `ConfigurationItem` and the shared `Server`, `Application` and `BusinessService`, `CIRelationship` (under the parent `JunctionLink`, typed dependsOn/runsOn/hostedOn), `AssignmentGroup` (under `Organization`), `ChangeRequest` (under `Change`), the TRM classes `TRMStandard` and `TRMLifecycle` (under `TechnologyStandard`), `TRMCategory`, `TRMPhase` and `TRMTechnicalDebt` (under `Concept`), and `TechnologyRequest` (under `TRMRequest`) with `LifecycleRequest` under it, with the edges `affects`, `ownedBy`, `usesTechnology`, `touches`, `inCategory`, `hasPhase` (TRMStandard to TRMPhase, the lifecycle phase), `lifecycleOf`, `lifecyclePhase`, `debtOn`, `debtOfApplication` and `requestsTechnology` (TechnologyRequest to TRMStandard), and a governance shape per new record class. It is proven independently of the other stories.

**Acceptance Scenarios**:

1. **Given** the `servicenow-api` connector built from the default branch, **When** `tests/test_cmdb_trm_ontology.py::test_new_classes_extend_their_parent` runs, **Then** no declared class is an orphan, every new type is a `schema_mappings` key and a shape target, and the edges name classes this ontology declares.

### User Story 5 - CMDB and TRM ingest sources (Priority: P2)

The fleet operator and the engine rely on this behaviour of `servicenow-api`: `ingest_sources.json` declares `cmdb-cis` (`cmdb_ci`), `cmdb-ci-relationships` (`cmdb_rel_ci`), the Enterprise Architecture TRM sources `trm-standards` (`sn_apm_trm_standards_product`), `trm-categories` (`sn_apm_trm_standards_category`), `trm-phases` (`sn_apm_trm_standards_phase`), `trm-lifecycles` (`sn_apm_trm_standards_product_lifecycle`), `trm-technical-debt` (`sn_apm_trm_standards_technical_debt`), `trm-requests` (`sn_apm_trm_product_request`) and `trm-lifecycle-requests` (`sn_apm_trm_product_lifecycle_request`), and `change-requests`, each through the read-only `servicenow_get_table` tool and each with a record type that is a key of `schema_mappings`. It is proven independently of the other stories.

**Acceptance Scenarios**:

1. **Given** the `servicenow-api` connector built from the default branch, **When** `tests/test_cmdb_trm_ontology.py::test_ingest_sources_name_read_only_tools_and_mapped_types` runs, **Then** every source names a read-only tool, the table named above and a mapped record type.

### User Story 6 - Competency-question paths (Priority: P2)

The fleet operator and the engine rely on this behaviour of `servicenow-api`: `servicenow.ttl` references the shared `Server`, `Application`, `BusinessService` and `Change` and never redeclares them, so each has one parent chain decided by the medulla ontology; `affects`, `priority` and `state` carry a domain of `Incident` and `Change`; `hostedOn` spans `ConfigurationItem`, `Application` and `Server`; no `schema_mappings` entry has a null `ontology_class`. It is proven independently of the other stories.

**Acceptance Scenarios**:

1. **Given** the `servicenow-api` connector built from the default branch, **When** `tests/test_cq_paths.py::test_shared_concepts_are_not_redeclared` runs, **Then** the test finds no shared-concept declaration, the incident domains, the host edge span and no null mapping.

### User Story 7 - Owner, steward and CMDB edges (Priority: P2)

The fleet operator and the engine rely on this behaviour of `servicenow-api`: The ingest sources declare edges with SDK `EdgeSpec`. It is proven independently of the other stories.

**Acceptance Scenarios**:

1. **Given** the `servicenow-api` connector built from the default branch, **When** `tests/test_catalog_edges.py::test_every_declared_edge_is_an_ontology_property_of_its_record_type` runs, **Then** `tests/test_catalog_edges.py::test_every_declared_edge_is_an_ontology_property_of_its_record_type` and `::test_incident_references_become_owner_group_and_ci_edges` and `::test_change_and_knowledge_sources_read_their_tables_through_the_table_tool`.

### User Story 8 - Declare access contracts for the competency reads of servicenow-api (Priority: P2)

The fleet operator and the engine rely on this behaviour of `servicenow-api`: Subsystem: connector `servicenow-api`. It is proven independently of the other stories.

**Acceptance Scenarios**:

1. **Given** the `servicenow-api` connector built from the default branch, **When** `tests/test_access_contracts.py::test_competency_contracts_certified` runs, **Then** test: `tests/test_access_contracts.py::test_competency_contracts_certified` (L2) runs the connector ontology certification and validates each recording against its contract.

### Edge Cases

- The vendor service is unreachable or rejects the credential: the connector returns the SDK typed error and never a partial result.
- An argument outside the documented inputs is refused with the SDK typed refusal and causes no effect on the vendor service.

## Requirements

- **FR-001**: Default content. Rows: `CONN-SERVICENOW-API-CONNECTOR-CONTENT-R001`.
- **FR-002**: Ontology joins the parent graph. Rows: `CONN-SERVICENOW-API-CONNECTOR-CONTENT-R002`.
- **FR-003**: Declared ingest sources. Rows: `CONN-SERVICENOW-API-CONNECTOR-CONTENT-R003`.
- **FR-004**: CMDB and TRM ontology. Rows: `CONN-SERVICENOW-API-CONNECTOR-CONTENT-R004`.
- **FR-005**: CMDB and TRM ingest sources. Rows: `CONN-SERVICENOW-API-CONNECTOR-CONTENT-R005`.
- **FR-006**: Competency-question paths. Rows: `CONN-SERVICENOW-API-CONNECTOR-CONTENT-R006`.
- **FR-007**: Owner, steward and CMDB edges. Rows: `CONN-SERVICENOW-API-CONNECTOR-CONTENT-R007`.
- **FR-008**: Declare access contracts for the competency reads of servicenow-api. Rows: `CONN-SERVICENOW-API-CONNECTOR-CONTENT-R008`.

## Success Criteria

- **SC-001**: `resources/list` includes `skill://` and `ontology://`; `prompts/list` includes each packaged prompt. Rows: `CONN-SERVICENOW-API-CONNECTOR-CONTENT-R001`.
- **SC-002**: The test parses each ontology and finds no orphan class beyond the pending list. Rows: `CONN-SERVICENOW-API-CONNECTOR-CONTENT-R002`.
- **SC-003**: The declaration loads through the SDK, names the tool and the mapped record type, and the read-only annotation holds. Rows: `CONN-SERVICENOW-API-CONNECTOR-CONTENT-R003`.
- **SC-004**: No declared class is an orphan, every new type is a `schema_mappings` key and a shape target, and the edges name classes this ontology declares. Rows: `CONN-SERVICENOW-API-CONNECTOR-CONTENT-R004`.
- **SC-005**: Every source names a read-only tool, the table named above and a mapped record type. Rows: `CONN-SERVICENOW-API-CONNECTOR-CONTENT-R005`.
- **SC-006**: The test finds no shared-concept declaration, the incident domains, the host edge span and no null mapping. Rows: `CONN-SERVICENOW-API-CONNECTOR-CONTENT-R006`.
- **SC-007**: `tests/test_catalog_edges.py::test_every_declared_edge_is_an_ontology_property_of_its_record_type` and `::test_incident_references_become_owner_group_and_ci_edges` and `::test_change_and_knowledge_sources_read_their_tables_through_the_table_tool`. Rows: `CONN-SERVICENOW-API-CONNECTOR-CONTENT-R007`.
- **SC-008**: Test: `tests/test_access_contracts.py::test_competency_contracts_certified` (L2) runs the connector ontology certification and validates each recording against its contract. Rows: `CONN-SERVICENOW-API-CONNECTOR-CONTENT-R008`.

## Assumptions

- The `servicenow-api` package keeps the entry point and module layout named in the rows.
- The shared SDK supplies the transport, authentication, retry and certification helpers the rows reuse.

## Traceability

| Label | Rows | Design section | Test ID | Evidence |
|---|---|---|---|---|
| FR-001 | `CONN-SERVICENOW-API-CONNECTOR-CONTENT-R001` | plan.md Production caller chain | T-001 | tests/test_default_content_surfaces.py::test_default_content_surfaces |
| FR-002 | `CONN-SERVICENOW-API-CONNECTOR-CONTENT-R002` | plan.md Production caller chain | T-002 | tests/test_ontology_parent_link.py::test_ontology_joins_the_parent_graph |
| FR-003 | `CONN-SERVICENOW-API-CONNECTOR-CONTENT-R003` | plan.md Production caller chain | T-003 | tests/test_ingest_sources.py::test_declares_ingestible_sources |
| FR-004 | `CONN-SERVICENOW-API-CONNECTOR-CONTENT-R004` | plan.md Production caller chain | T-004 | tests/test_cmdb_trm_ontology.py::test_new_classes_extend_their_parent |
| FR-005 | `CONN-SERVICENOW-API-CONNECTOR-CONTENT-R005` | plan.md Production caller chain | T-005 | tests/test_cmdb_trm_ontology.py::test_ingest_sources_name_read_only_tools_and_mapped_types |
| FR-006 | `CONN-SERVICENOW-API-CONNECTOR-CONTENT-R006` | plan.md Production caller chain | T-006 | tests/test_cq_paths.py::test_shared_concepts_are_not_redeclared |
| FR-007 | `CONN-SERVICENOW-API-CONNECTOR-CONTENT-R007` | plan.md Production caller chain | T-007 | tests/test_catalog_edges.py::test_every_declared_edge_is_an_ontology_property_of_its_record_type |
| FR-008 | `CONN-SERVICENOW-API-CONNECTOR-CONTENT-R008` | plan.md Production caller chain | T-008 | tests/test_access_contracts.py::test_competency_contracts_certified |
