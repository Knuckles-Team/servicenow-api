---
name: ServiceNow PPM
description: Manage Project Portfolio Management cost plans and project tasks.
---

# Project Portfolio Management (PPM)

This skill allows the agent to interact with the ServiceNow PPM API.

## Capabilities

- **Insert Cost Plans**: Create multiple cost plans in a batch.
- **Insert Project Tasks**: Create a project structure with tasks and dependencies.

## Tools

### `insert_cost_plans`
Creates cost plans.

**Parameters:**
- `plans` (list): List of cost plan dictionaries.

### `insert_project_tasks`
Creates a project and associated project tasks.

**Parameters:**
- `short_description` (string): Project description.
- `start_date` (string, optional): Start date (YYYY-MM-DD HH:MM:SS).
- `end_date` (string, optional): End date.
- `child_tasks` (list, optional): Recursive list of child tasks.
- `dependencies` (list, optional): Dependencies between tasks.

## Examples

### Create Cost Plans
```python
insert_cost_plans(plans=[
    {
        "name": "Hardware Cost",
        "resource_type": "resource_type_sys_id",
        "start_fiscal_period": "period_sys_id",
        "end_fiscal_period": "period_sys_id",
        "task": "project_sys_id",
        "unit_cost": 5000.0
    }
])
```

### Create Project Structure
```python
insert_project_tasks(
    short_description="New Infrastructure Project",
    start_date="2024-01-01 09:00:00",
    child_tasks=[
        {"short_description": "Phase 1: Planning"},
        {"short_description": "Phase 2: Execution"}
    ]
)
```
