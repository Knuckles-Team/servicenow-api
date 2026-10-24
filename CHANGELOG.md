# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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
