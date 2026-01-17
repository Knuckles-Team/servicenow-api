---
name: servicenow-incidents
description: "Manages ServiceNow incidents. Use for getting/creating incidents. Triggers - tickets, issues."
---

### Overview
Incident mgmt via MCP.

### Key Tools
- `get_incidents`: List/get by ID.
- `create_incident`: Create.

### Usage Instructions
1. Filters: sysparm_query.

### Examples
- Create: `create_incident` with data={"short_description": "Outage"}.
- Get: `get_incidents` with sysparm_query="number=INC001".

### Error Handling
- No results: Empty valid.
