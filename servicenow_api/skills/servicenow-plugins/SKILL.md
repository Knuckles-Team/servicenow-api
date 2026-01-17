---
name: servicenow-plugins
description: Manages ServiceNow plugins. Use for activating/rolling back plugins. Triggers - extensions, activations.
---

### Overview
Plugin lifecycle via MCP.

### Key Tools
- `activate_plugin`: Activate by ID.
- `rollback_plugin`: Rollback by ID.

### Usage Instructions
1. Provide plugin_id.

### Examples
- Activate: `activate_plugin` with plugin_id="plugin123".

### Error Handling
- Already active: Idempotent.
