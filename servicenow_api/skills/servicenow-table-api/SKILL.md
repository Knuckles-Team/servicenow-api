---
name: servicenow-table-api
description: Manages ServiceNow tables. Use for CRUD on any table. Triggers - generic data ops.
---

### Overview
Table API via MCP.

### Key Tools
- Delete/get/patch/update/add records.

### Usage Instructions
1. Table name, sys_id, data.

### Examples
- Add: `add_table_record` with table="custom", data={"field": "val"}.
- Update: `update_table_record` with sys_id="rec1", data=updates.

### Error Handling
- Table not found: Verify name.
