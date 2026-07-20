# Code Enhancement: servicenow-api

> Automated code enhancement review for servicenow-api. Covers 17 analysis domains.

## User Stories

- As a **developer**, I want to **address Project Analysis findings (grade: C, score: 74)**, so that **improve project project analysis from C to at least B (80+)**.
- As a **developer**, I want to **address Codebase Optimization findings (grade: F, score: 47)**, so that **improve project codebase optimization from F to at least B (80+)**.
- As a **developer**, I want to **address Architecture & Design Patterns findings (grade: F, score: 55)**, so that **improve project architecture & design patterns from F to at least B (80+)**.
- As a **developer**, I want to **address Concept Traceability findings (grade: F, score: 24)**, so that **improve project concept traceability from F to at least B (80+)**.
- As a **developer**, I want to **address Test Execution findings (grade: F, score: 25)**, so that **improve project test execution from F to at least B (80+)**.
- As a **developer**, I want to **address Changelog Audit findings (grade: C, score: 75)**, so that **improve project changelog audit from C to at least B (80+)**.
- As a **developer**, I want to **address Pytest Quality findings (grade: F, score: 58)**, so that **improve project pytest quality from F to at least B (80+)**.
- As a **developer**, I want to **address Environment Variables findings (grade: D, score: 60)**, so that **improve project environment variables from D to at least B (80+)**.
- As a **developer**, I want to **address analyze_xdg_kg findings (grade: F, score: 0)**, so that **improve project analyze_xdg_kg from F to at least B (80+)**.

## Functional Requirements

- **FR-001**: Detected 2 agent skill(s) — will grade in CE-026
- **FR-002**: Minor update: pytest-xdist 3.6.0 (constraint — not installed) -> 3.8.0
- **FR-003**: Minor update: agent-utilities 0.2.40 (installed) -> 0.16.0
- **FR-004**: 4 functions exceed 200 lines (actionable refactoring targets): test_api_client_exhaustive_methods (264L), test_servicenow_change_requests_responses (247L), test_servicenow_change_request_responses (240L), workflow_to_mermaid (223L)
- **FR-005**: Monolithic: mcp_server.py (1401L) — 4 functions with high complexity (worst: get_mcp_instance at 180L, CC=50); Low cohesion: 40 distinct concepts in one file
- **FR-006**: Monolithic: api_client_other.py (1395L) — 2 functions with high complexity (worst: extract_action_details at 57L, CC=29); Low cohesion: 24 distinct concepts in one file
- **FR-007**: Monolithic: api_client_cmdb.py (1257L) — 3 functions with high complexity (worst: ServiceNowApiCmdb.collect_graph_for_roots at 179L, CC=33); Low cohesion: 24 distinct concepts in one file
- **FR-008**: 33 functions with nesting depth >4
- **FR-009**: 1 flat directories with >15 Python files: servicenow_api/mcp
- **FR-010**: 12 potential doc-test drift items
- **FR-011**: README.md missing sections: usage|quick start
- **FR-012**: 2 broken internal links in README.md
- **FR-013**: README missing: Has a Table of Contents
- **FR-014**: README missing: Has usage examples with code blocks
- **FR-015**: SRP: 10 modules exceed 500 lines (god modules)
- **FR-016**: SRP: 4 classes have >15 methods
- **FR-017**: No discernible layer architecture (no domain/service/adapter separation)
- **FR-018**: Low dependency injection ratio: 1%
- **FR-019**: 30 Python files at top level — consider package organization
- **FR-020**: Low traceability ratio: 3% concepts fully traced
- **FR-021**: 37 orphaned concepts (only in one source)
- **FR-022**: 78 test functions missing concept markers
- **FR-023**: 361 significant functions (>10 lines) missing concept markers in docstrings
- **FR-024**: Total lint findings: 0 (high/error: 0, medium/warning: 0, low: 0)
- **FR-025**: 1 hook(s) may be outdated: ruff-pre-commit
- **FR-026**: 2 directories with >20 files: servicenow_api/mcp, servicenow_api/skills/servicenow-sdk-docs/references
- **FR-027**: 2 rogue/throwaway scripts detected (fix_*, validate_*, patch_*, etc.): scripts/validate_agent.py, scripts/validate_a2a_agent.py
- **FR-028**: CHANGELOG.md exists but could not be parsed — check format compliance
- **FR-029**: No changelog entries within the last 30 days
- **FR-030**: keepachangelog not installed — pip install 'universal-skills[code-enhancer]'
- **FR-031**: 2 test files exceed 500 lines — split into focused modules
- **FR-032**: Test directory lacks subdirectory organization (consider unit/, integration/, e2e/)
- **FR-033**: No @pytest.mark.parametrize usage — consider data-driven tests
- **FR-034**: 5 tests have no assertions
- **FR-035**: 24 tests use weak assertions (assert result is not None, assert True, etc.)
- **FR-036**: 4 tests have excessive mocking (>5 mocks) — test behavior, not implementation
- **FR-037**: 8 tests exceed 100 lines — likely doing too much per test
- **FR-038**: Only 25% of env vars documented in README.md
- **FR-039**: Undocumented env vars: ACCOUNTTOOL, ACTIVITY_SUBSCRIPTIONSTOOL, AGGREGATETOOL, APPLICATIONTOOL, ATTACHMENTTOOL, AUDIENCE, AUTHTOOL, AUTH_TYPE, BATCHTOOL, CHANGE_MANAGEMENTTOOL
- **FR-040**: 11 Python env vars not in .env.example: AUDIENCE, DELEGATED_SCOPES, LLM_API_KEY, LLM_BASE_URL, MCP_URL
- **FR-041**: Analysis error: No module named 'agent_utilities.knowledge_graph'

## Success Criteria

- Overall GPA: 2.06 → 3.0
- Domains at B or above: 8 → 17
- Actionable findings: 41 → 0
