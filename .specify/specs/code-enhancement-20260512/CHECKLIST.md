# Verification Checklist: Code Enhancement: servicenow-api

## Functional Requirements Verification
- [ ] **FR-001**: Detected 2 agent skill(s) — will grade in CE-026
- [ ] **FR-002**: 7 functions exceed 200 lines (actionable refactoring targets): register_change_management_tools (709L), register_cicd_tools (256L), test_servicenow_change_requests_responses (247L), test_servicenow_change_request_responses (240L), register_knowledge_management_tools (229L)
- [ ] **FR-003**: Monolithic: mcp_server.py (3012L) — 5 functions with high complexity (worst: register_change_management_tools at 709L, CC=8); Low cohesion: 40 distinct concepts in one file
- [ ] **FR-004**: Monolithic: api_wrapper.py (5408L) — 4 functions with high complexity (worst: Api.workflow_to_mermaid at 221L, CC=23); Low cohesion: 22 distinct concepts in one file
- [ ] **FR-005**: Monolithic: servicenow_models.py (3092L) — 1 functions with high complexity (worst: CICDModel.model_post_init at 63L, CC=28); Low cohesion: 93 distinct concepts in one file
- [ ] **FR-006**: 10 functions with nesting depth >4
- [ ] **FR-007**: 28 potential doc-test drift items
- [ ] **FR-008**: README.md missing sections: installation
- [ ] **FR-009**: README missing: Has a Table of Contents
- [ ] **FR-010**: README missing: References /docs directory material
- [ ] **FR-011**: SRP: 4 modules exceed 500 lines (god modules)
- [ ] **FR-012**: SRP: 1 classes have >15 methods
- [ ] **FR-013**: No discernible layer architecture (no domain/service/adapter separation)
- [ ] **FR-014**: Low dependency injection ratio: 1%
- [ ] **FR-015**: Low traceability ratio: 0% concepts fully traced
- [ ] **FR-016**: 51 test functions missing concept markers
- [ ] **FR-017**: 303 significant functions (>10 lines) missing concept markers in docstrings
- [ ] **FR-018**: Total lint findings: 435 (high/error: 422, medium/warning: 13, low: 0)
- [ ] **FR-019**: 1 hook(s) may be outdated: ruff-pre-commit
- [ ] **FR-020**: 7 test execution error(s)
- [ ] **FR-021**: 2 directories with >20 files: servicenow_api/servicenow_flow_reports, servicenow_api/skills/servicenow-sdk-docs/references
- [ ] **FR-022**: 2 rogue/throwaway scripts detected (fix_*, validate_*, patch_*, etc.): scripts/validate_agent.py, scripts/validate_a2a_agent.py
- [ ] **FR-023**: Found 15 file(s) with version '1.15.0' that are NOT tracked in .bumpversion.cfg:
- [ ] **FR-024**: - .mypy_cache/3.13/pydantic/_migration.meta.json
- [ ] **FR-025**: - .mypy_cache/3.13/pydantic/errors.meta.json
- [ ] **FR-026**: - .mypy_cache/3.13/pydantic/functional_validators.meta.json
- [ ] **FR-027**: - .mypy_cache/3.13/pydantic/__init__.meta.json
- [ ] **FR-028**: - .mypy_cache/3.13/pydantic/warnings.meta.json
- [ ] **FR-029**: ... and 10 more.
- [ ] **FR-030**: CHANGELOG.md exists but could not be parsed — check format compliance
- [ ] **FR-031**: No changelog entries within the last 30 days
- [ ] **FR-032**: keepachangelog not installed — pip install 'universal-skills[code-enhancer]'
- [ ] **FR-033**: 1 test files exceed 500 lines — split into focused modules
- [ ] **FR-034**: Test directory lacks subdirectory organization (consider unit/, integration/, e2e/)
- [ ] **FR-035**: No @pytest.mark.parametrize usage — consider data-driven tests
- [ ] **FR-036**: 5 tests have no assertions
- [ ] **FR-037**: 24 tests use weak assertions (assert result is not None, assert True, etc.)
- [ ] **FR-038**: 6 tests exceed 100 lines — likely doing too much per test
- [ ] **FR-039**: Undocumented env vars: ENABLE_OTEL, OTEL_EXPORTER_OTLP_ENDPOINT, OTEL_EXPORTER_OTLP_PROTOCOL, OTEL_EXPORTER_OTLP_PUBLIC_KEY, OTEL_EXPORTER_OTLP_SECRET_KEY, SNOW_CLIENT_ID, SNOW_CLIENT_SECRET, SNOW_HOST, SNOW_INSTANCE, SNOW_PASSWORD
- [ ] **FR-040**: 51 Python env vars not in .env.example: ACCOUNTTOOL, ACTIVITY_SUBSCRIPTIONSTOOL, AGGREGATETOOL, APPLICATIONTOOL, ATTACHMENTTOOL

## User Stories / Acceptance Criteria
- [ ] As a **developer**, I want to **address Project Analysis findings (grade: C, score: 74)**, so that **improve project project analysis from C to at least B (80+)**.
- [ ] As a **developer**, I want to **address Codebase Optimization findings (grade: F, score: 50)**, so that **improve project codebase optimization from F to at least B (80+)**.
- [ ] As a **developer**, I want to **address Architecture & Design Patterns findings (grade: D, score: 65)**, so that **improve project architecture & design patterns from D to at least B (80+)**.
- [ ] As a **developer**, I want to **address Concept Traceability findings (grade: F, score: 30)**, so that **improve project concept traceability from F to at least B (80+)**.
- [ ] As a **developer**, I want to **address Linting & Formatting findings (grade: F, score: 0)**, so that **improve project linting & formatting from F to at least B (80+)**.
- [ ] As a **developer**, I want to **address Test Execution findings (grade: F, score: 10)**, so that **improve project test execution from F to at least B (80+)**.
- [ ] As a **developer**, I want to **address Version Sync Analysis findings (grade: D, score: 60)**, so that **improve project version sync analysis from D to at least B (80+)**.
- [ ] As a **developer**, I want to **address Changelog Audit findings (grade: C, score: 75)**, so that **improve project changelog audit from C to at least B (80+)**.
- [ ] As a **developer**, I want to **address Pytest Quality findings (grade: D, score: 65)**, so that **improve project pytest quality from D to at least B (80+)**.

## Success Criteria
- [ ] Overall GPA: 2.12 → 3.0
- [ ] Domains at B or above: 8 → 17
- [ ] Actionable findings: 40 → 0

## Technical Quality Gates
- [x] Pre-commit linting (Ruff check/format) passed
- [x] Repository standards checked and verified
- [x] Zero deprecated / local absolute `file:///` URLs

## Review & Acceptance
- **Overall Verification Score**: 0%
- **Final Review Status**: **Needs Revision**
