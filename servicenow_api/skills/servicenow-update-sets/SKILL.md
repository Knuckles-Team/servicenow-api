---
name: servicenow-update-sets
description: Manages ServiceNow update sets. Use for creating, retrieving, previewing, committing. Triggers - customizations, deployments.
---

### Overview
Update set ops via MCP.

### Key Tools
- `update_set_create` / `retrieve` / `preview` / `commit` / `commit_multiple` / `back_out`.

### Usage Instructions
1. Use IDs for actions.

### Examples
- Create: `update_set_create` with update_set_name="fix1", scope="global".

### Error Handling
- Preview conflicts: Resolve before commit.
