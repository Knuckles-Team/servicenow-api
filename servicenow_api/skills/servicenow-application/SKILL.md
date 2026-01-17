---
name: servicenow-application
description: Manages ServiceNow applications. Use for retrieving application details. Triggers - app info, sys_id queries.
---

### Overview
Handles application records via MCP.

### Key Tools
- `get_application`: Get app by ID. Params: application_id (required).

### Usage Instructions
1. Use application_id (sys_id).
2. Call for single apps.

### Examples
- Get app: `get_application` with application_id="abc123".

### Error Handling
- 404: Invalid ID—verify sys_id.
