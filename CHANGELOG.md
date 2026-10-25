# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2.4.11] - 2026-10-25

### Fixed

- G13: the `change-requests` source reads the `change_request` table through `servicenow_get_table` (first 100 records,
  the sys_id, number, short_description, description, state, priority, cmdb_ci and sys_updated_on fields only), because
  `servicenow_get_change_requests` overran the MCP stream-size limit with or without a limit argument;
  `servicenow-knowledge` reads the `kb_knowledge` table the same way, because `servicenow_get_knowledge_articles` is
  refused by the instance. Both syncs ended failed with 0 records.
- The `incidents` source requests its reference fields without display values or links
  (`sysparm_display_value=false`, `sysparm_exclude_reference_link=true`), so the owner, group and CI edges read the
  referenced sys_id.
- Corrected the 2.4.10 changelog entry, which claimed its argument fix resolved the failed G13 syncs.

## [2.4.10] - 2026-10-24

### Added

- Owner, steward and CMDB edges on the ingest sources (SDK 0.5.5 `EdgeSpec`): incident to assignment group,
  assignee and CI; CI to owner, managing and support group; CI relationship to parent and child CI; change
  request to the CI it touches (CONN-SERVICENOW-API-CONNECTOR-CONTENT-R007). Requires `agent-connector-sdk>=0.5.5`.

### Fixed

- The `change-requests` source no longer passes `sysparm_limit`, and `servicenow-knowledge` reads `result.articles`
  (G13). Corrected in 2.4.11: the live probe showed this did not fix the failed syncs — `servicenow_get_change_requests`
  overruns the MCP stream-size limit with or without a limit argument, and `servicenow_get_knowledge_articles` is
  refused by the instance. The read-path fix ships in 2.4.11.

## [2.4.9] - 2026-10-24

### Changed
- Central connector migration: requires `agent-connector-sdk>=0.5.4`; server bootstrap, version, containers, ontology artifacts, security scaffold and pre-commit config are provided centrally.

## [2.4.8] - 2026-10-23

### Changed
- Requires `agent-connector-sdk>=0.4.1`; data sources are declared in code (`connector_sources`).

## [Unreleased]

## [1.19.0] - 2026-05-22

### Added
- Consolidated Action-Routed MCP tools pattern across all ServiceNow endpoints (e.g., `servicenow_change_management`, `servicenow_incidents`, `servicenow_cmdb`, etc.) to stay well below the 100-tool limit.
- Strict Pydantic V2 `@classmethod` signature validations for input params and responses.
- 100% test coverage across newly restructured action-routed tools, auth mechanisms, and graph subflows.

### Changed
- Refactored all method arguments to remove leading underscores, resolving Pyrefly linting issues and enabling precise LLM tool parameter inference.
- Replaced custom mock classes in the test suite with strict Pydantic model equivalents.
- Filtered dynamic namespace dictionary results in package standard `dir(servicenow_api)` to exclude private helper functions (symbols starting with `_`).

### Fixed
- Pydantic V2 `ValidationError` and `AttributeError` trace failures across the entire pytest coverage suite.
- Type annotations and signature matching for `get_mcp_instance` returning a 5-tuple.

## [1.6.56] - 2026-04-29

### Added
- Initial release
