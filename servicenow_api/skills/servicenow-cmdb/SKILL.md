---
name: servicenow-cmdb
description: Manages ServiceNow CMDB. Use for fetching CMDB records. Triggers - configuration items, CI queries.
---

### Overview
Queries CMDB via MCP.

### Key Tools
- `get_cmdb`: Get record by ID. Params: cmdb_id (required).

### Usage Instructions
1. Provide cmdb_id (sys_id).

### Examples
- Get CI: `get_cmdb` with cmdb_id="def456".

### Error Handling
- Missing ID: Required param.
