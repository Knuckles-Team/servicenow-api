---
name: servicenow-change-management
description: Manages ServiceNow changes. Use for CRs, tasks, models, approvals. Triggers: ITIL changes, risks.
---

### Overview
Comprehensive change mgmt. Load `tools-reference.md` for details on many tools.

### Key Tools
- Get/create/update/delete CRs, tasks, CIs.
- Conflicts, risks, approvals, models/templates.

### Usage Instructions
1. Use sys_ids, types (normal/standard).
2. For creation: name_value_pairs dict.

### Examples
- Create CR: `create_change_request` with name_value_pairs="short_description=Issue", change_type="normal".
- Approve: `approve_change_request` with state="approved".

### Error Handling
- State invalid: Check nextstate.
- Conflicts: Use check/refresh.
