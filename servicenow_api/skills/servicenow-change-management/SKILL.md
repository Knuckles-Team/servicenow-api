---
name: servicenow-change-management
description: "Manages ServiceNow Change Requests (CRs). Use this skill to create, read, update, and delete CRs, tasks, and models, and to manage conflicts, schedules, and approvals."
---

### Overview
This skill provides comprehensive access to the ServiceNow Change Management API via MCP tools. You can manage the entire lifecycle of a change request, from creation (Standard, Normal, Emergency) to closure, including task management and conflict detection.

### Tool Usage Reference

#### 1. Retrieval
- **`get_change_requests`**: Search for CRs.
    - `change_type` (str): 'emergency', 'normal', 'standard', 'model'.
    - `sysparm_query` (str): Encoded query string (e.g., `active=true^ORDERBYnumber`).
    - `sysparm_limit` (int): Max records (default 5).
    - `sysparm_offset` (int): Pagination offset.
    - `name_value_pairs` (str): Key-value pairs for equality matching.
    - `text_search` (str): Free text search.
- **`get_change_request`**: Get a single CR.
    - `change_request_sys_id` (str): The CR sys_id.
    - `change_type` (str, optional): 'emergency', 'normal', 'standard'.
- **`get_change_request_tasks`**: Get tasks for a CR.
    - `change_request_sys_id` (str): Target CR sys_id.
    - `sysparm_query`, `sysparm_limit`, `order`, etc.
- **`get_change_request_ci`**: Get CIs associated with a CR.
    - `change_request_sys_id` (str): Target CR sys_id.
- **`get_change_request_schedule`**: Get schedule for a CI.
    - `cmdb_ci_sys_id` (str): Config Item sys_id.
- **`get_change_request_nextstate`**: detailed state transition info.
    - `change_request_sys_id` (str).
- **`get_change_request_worker`**: Get worker details.
    - `worker_sys_id` (str).

#### 2. Templates & Models
- **`get_standard_change_request_templates`**: List standard change templates.
    - `name_value_pairs`, `sysparm_query`, `text_search`.
- **`get_standard_change_request_template`**: Get specific template.
    - `template_sys_id` (str).
- **`get_change_request_models`**: List change models.
    - `change_type` (str), `sysparm_query`, etc.
- **`get_standard_change_request_model`**: Get specific model.
    - `model_sys_id` (str).
- **`calculate_standard_change_request_risk`**: Risk assessment.
    - `change_request_sys_id` (str): **Standard** CR sys_id only.

#### 3. Creation
- **`create_change_request`**: Create a new CR.
    - `change_type` (str): Default 'normal'. Use 'standard' or 'emergency' as needed.
    - `name_value_pairs` (str): JSON-like string or dict str of fields (e.g., `{"short_description": "Fix DB", "cmdb_ci": "..."}`).
    - `standard_change_template_id` (str): Required if `change_type` is 'standard'.
- **`create_change_request_task`**: Add a task to a CR.
    - `change_request_sys_id` (str).
    - `data` (dict): Fields for the task (e.g., `{"short_description": "Deploy code"}`).
- **`create_change_request_ci_association`**: Associate CIs (Affected/Impacted).
    - `change_request_sys_id` (str).
    - `cmdb_ci_sys_ids` (List[str]): List of CI sys_ids.
    - `association_type` (str): 'affected', 'impacted', 'offering'.
    - `refresh_impacted_services` (bool): Optional refresh trigger.

#### 4. Modification
- **`update_change_request`**: Update CR fields.
    - `change_request_sys_id` (str).
    - `name_value_pairs` (str): Fields to update.
    - `change_type` (str): If changing type.
- **`update_change_request_task`**: Update a task.
    - `change_request_sys_id` (str).
    - `change_request_task_sys_id` (str).
    - `name_value_pairs` (str).
- **`approve_change_request`**: Approve/Reject.
    - `change_request_sys_id` (str).
    - `state` (str): 'approved' or 'rejected'.
- **`update_change_request_first_available`**: Move to next state.
    - `change_request_sys_id` (str).

#### 5. Conflict Management
- **`check_change_request_conflict`**: Run conflict detection.
    - `change_request_sys_id` (str).
- **`get_change_request_conflict`**: detailed conflict info.
    - `change_request_sys_id` (str).
- **`delete_change_request_conflict_scan`**: Cancel/Delete scan.
    - `change_request_sys_id` (str).
    - `task_sys_id` (str): Task ID associated with conflict (if required by tool definition).

#### 6. Deletion
- **`delete_change_request`**: Delete a CR.
    - `change_request_sys_id` (str).
    - `change_type` (str).
- **`delete_change_request_task`**: Delete a creation task.
    - `change_request_sys_id` (str).
    - `task_sys_id` (str).

### Important Notes
- **Name-Value Pairs**: When providing `name_value_pairs`, ensure you use valid field names (e.g., `short_description`, `assignment_group`, `start_date`).
- **Standard Changes**: Always require `standard_change_template_id`.
- **Dates**: Use UTC strings (e.g., "2023-10-01 12:00:00").

### Examples

**Search for Open Normal Changes**:
```python
get_change_requests(
    change_type="normal",
    sysparm_query="active=true^state=1"
)
```

**Create a Normal Change**:
```python
create_change_request(
    change_type="normal",
    name_value_pairs="{'short_description': 'Upgrade Server', 'priority': '2', 'cmdb_ci': 'sys_id_here'}"
)
```

**Check Conflicts**:
```python
check_change_request_conflict(change_request_sys_id="...")
```
