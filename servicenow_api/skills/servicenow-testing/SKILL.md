---
name: servicenow-testing
description: Manages ServiceNow testing. Use for running test suites. Triggers - ATF, automated tests.
---

### Overview
Testing via MCP.

### Key Tools
- `run_test_suite`: Run suite with browser/OS.

### Usage Instructions
1. Provide suite sys_id/name.

### Examples
- Run: `run_test_suite` with test_suite_sys_id="suite1", browser_name="chrome".

### Error Handling
- Failures: Check results.
