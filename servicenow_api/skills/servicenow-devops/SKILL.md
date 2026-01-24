---
name: servicenow-devops
description: Manages DevOps integration in ServiceNow. Use for checking change control and registering artifacts.
---

### Overview
Handles DevOps integration tasks via MCP.

### Key Tools
- `check_devops_change_control`: Checks if the orchestration task is under change control. Params: toolId (required), orchestrationTaskName (optional).
- `register_devops_artifact`: Registers artifacts into a ServiceNow instance. Params: artifacts (list), pipelineName etc.

### Usage Instructions
1. Use `check_devops_change_control` to verify if a task requires change management.
2. Use `register_devops_artifact` to push build artifacts to ServiceNow.

### Examples
- Check change control: `check_devops_change_control` with toolId="jenkins-1".

### Error Handling
- 400: Invalid tool ID or parameters.
