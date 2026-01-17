---
name: servicenow-source-control
description: Manages ServiceNow source control. Use for applying changes, importing repos. Triggers - git integration, SCM.
---

### Overview
Source control ops via MCP.

### Key Tools
- `apply_remote_source_control_changes`: Apply branch changes.
- `import_repository`: Import repo.

### Usage Instructions
1. Use sys_ids, branches.

### Examples
- Apply: `apply_remote_source_control_changes` with app_sys_id="app1", scope="global", branch_name="main".

### Error Handling
- Conflicts: Resolve manually.
