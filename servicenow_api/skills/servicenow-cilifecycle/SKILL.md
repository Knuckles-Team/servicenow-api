---
name: servicenow-cilifecycle
description: Manages CI Lifecycle Management in ServiceNow. Use for checking compatibility of CI actions and registering operators.
---

### Overview
Handles CI Lifecycle Management operations via MCP.

### Key Tools
- `check_ci_lifecycle_compat_actions`: Determines whether two specified CI actions are compatible. Params: actionName, otherActionName.
- `register_ci_lifecycle_operator`: Registers an operator for a non-workflow user.
- `unregister_ci_lifecycle_operator`: Unregisters an operator for non-workflow users. Params: req_id.

### Usage Instructions
1. Use `check_ci_lifecycle_compat_actions` before applying concurrent actions.
2. Register an operator if needed for non-workflow contexts.

### Examples
- Check compatibility: `check_ci_lifecycle_compat_actions` with actionName="retire", otherActionName="install"

### Error Handling
- 400: Invalid action names or parameters.
