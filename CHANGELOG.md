# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Action-routed architecture for MCP tools to comply with 100-tool limit and improve token usage
- Strict Pydantic V2 validations with `@classmethod` signatures

### Changed
- Consolidated fragmented MCP tools into action-routed pattern (e.g. `servicenow_incidents`, `servicenow_change_management`, `servicenow_table_api`)
- Removed leading underscores from method parameters to improve linting and tool inference
- Updated generic `Response` instances in test mocks to be fully schema compliant

### Fixed
- Pydantic V2 `ValidationError` and `AttributeError` failures in test suite
- Type hints on `model_validator` and `field_validator` throughout models

## [1.6.56] - 2026-04-29

### Added
- Initial release
