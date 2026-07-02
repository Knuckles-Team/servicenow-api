# CI Lifecycle Management — operator / action / lease model

Reference for the `servicenow_cilifecycle` tool. CI Lifecycle Management (part of
ServiceNow ITOM) governs *how* a configuration item may transition between
lifecycle states and *who* is allowed to make those transitions. Read this before
mutating lifecycle state — transitions are guarded and can be rejected.

## The model at a glance
- **Lifecycle status** — the CI's current lifecycle position (e.g. planning /
  building / in use / retiring / end of life). Read with
  `get_ci_lifecycle_status`, change with `set_ci_lifecycle_status`. Allowed values
  and transitions are defined by the CI class's lifecycle definition, not free-form.
- **Actions** — discrete operations a registered operator performs against a CI
  during its lifecycle (e.g. an install, a scan, a maintenance op). Active actions
  are listed with `get_ci_lifecycle_active_actions`; add/remove with
  `add_ci_lifecycle_action` / `delete_ci_lifecycle_action`.
- **Operators** — the actors (integrations / processes / users) permitted to drive
  a CI's lifecycle. An operator must be **registered** against the CI before it can
  act: `register_ci_lifecycle_operator` / `unregister_ci_lifecycle_operator`.
- **Leases** — a time-bounded hold an operator takes so concurrent processes don't
  collide on the same CI. Extend a hold with `extend_ci_lifecycle_lease`; a lapsed
  lease blocks further actions.

## Guard / validation actions (call before mutating)
Use these read-only checks to avoid a rejected mutation:

| Action | Answers |
|--------|---------|
| `check_ci_lifecycle_compat_actions` | Which actions are compatible with the CI's current state. |
| `check_ci_lifecycle_lease_expired` | Whether the operator's lease has lapsed (would block actions). |
| `check_ci_lifecycle_not_allowed_action` | Whether a specific action is disallowed right now. |
| `check_ci_lifecycle_not_allowed_ops_transition` | Whether a specific operational-status transition is disallowed. |
| `check_ci_lifecycle_requestor_valid` | Whether the requesting operator/user is authorized. |

## Typical sequence
1. `register_ci_lifecycle_operator` — register the acting operator against the CI.
2. `check_ci_lifecycle_requestor_valid` + `check_ci_lifecycle_compat_actions` —
   confirm the operator may act and which actions are legal.
3. `add_ci_lifecycle_action` — begin the action (takes/holds a lease).
4. `extend_ci_lifecycle_lease` — extend if the work outlasts the lease window.
5. `set_ci_lifecycle_status` — advance the lifecycle status (validate the
   transition first with `check_ci_lifecycle_not_allowed_ops_transition`).
6. `delete_ci_lifecycle_action` — complete/clear the action.
7. `unregister_ci_lifecycle_operator` — release the operator when done.

## Notes
- Every `params_json` key is passed straight to the client method; keys are a
  **JSON string**, not an object.
- Available statuses, actions, and transitions are defined per CI class — inspect a
  live CI (`get_ci_lifecycle_status`, `get_ci_lifecycle_active_actions`) rather than
  assuming a fixed set.
- A blocked mutation is usually one of: unregistered/invalid operator, expired
  lease, or a not-allowed action/transition — run the matching `check_*` to find
  which.
