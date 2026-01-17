---
name: servicenow-cicd
description: Manages ServiceNow CI/CD. Use for batches, scans, installs, publishes. Triggers - deployments, testing, pipelines.
---

### Overview
CI/CD operations via MCP. Reference `tools-reference.md` for schemas.

### Key Tools
- `batch_install_result` / `instance_scan_progress` / `progress`: Query statuses.
- `batch_install` / `batch_rollback`: Batch ops.
- `app_repo_install` / `publish` / `rollback`: App repo.
- `full_scan` / `point_scan` / `combo_suite_scan` / `suite_scan`: Scans.

### Usage Instructions
1. Use IDs for queries/actions.
2. For installs: scopes, versions.

### Examples
- Batch install: `batch_install` with name="deploy", packages="pkg1,pkg2".
- Full scan: `full_scan`.

### Error Handling
- Invalid IDs: Check existence.
- Failures: Retry or check logs.
