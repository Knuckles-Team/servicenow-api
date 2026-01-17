---
name: servicenow-import-sets
description: Manages ServiceNow import sets. Use for getting/inserting records. Triggers - data imports, ETL.
---

### Overview
Import set ops via MCP.

### Key Tools
- `get_import_set` / `insert_import_set` / `insert_multiple_import_sets`.

### Usage Instructions
1. Table name, data dicts.

### Examples
- Insert: `insert_import_set` with table="import_table", data={"field1": "val"}.

### Error Handling
- Validation errors: Check data.
