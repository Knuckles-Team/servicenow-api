# Change Request field values (state / type / risk / approval)

Reference for the choice/field codes used on `change_request` records. These are
the **ServiceNow baseline** values — instances routinely customize them, so treat
this as a starting map and confirm against the target instance (list a record with
`sysparm_display_value:"all"` to see both raw codes and labels).

## Change type (`type`)
| Value | Meaning |
|-------|---------|
| `normal` | Full assessment + CAB approval; scheduled. |
| `standard` | Pre-authorized, low-risk, created from a template/model. |
| `emergency` | Expedited path for urgent fixes; ECAB approval. |

Standard changes are instantiated from a **standard-change template** and its
model — use `get_standard_change_request_templates` /
`get_standard_change_request_model`, then `create_change_request`, then
`calculate_standard_change_request_risk`.

## State (`state`) — baseline "state model"
| Code | State |
|------|-------|
| `-5` | New |
| `-4` | Assess |
| `-3` | Authorize |
| `-2` | Scheduled |
| `-1` | Implement |
| `0`  | Review |
| `3`  | Closed |
| `4`  | Canceled |

Use `get_change_request_nextstate` to discover the legal next state for a given
record rather than hard-coding transitions.

## Risk (`risk`)
| Code | Risk |
|------|------|
| `2` | High |
| `3` | Moderate |
| `4` | Low |

`calculate_standard_change_request_risk` computes risk from the standard-change
model's risk conditions; for normal changes `risk` may be set directly or driven
by a risk-assessment questionnaire depending on instance config.

## Impact (`impact`) / Urgency
| Code | Level |
|------|-------|
| `1` | High |
| `2` | Medium |
| `3` | Low |

## Approval (`approval`)
| Value | Meaning |
|-------|---------|
| `not requested` | Approval not yet requested. |
| `requested` | Awaiting approver action. |
| `approved` | Approved (CAB / delegated). |
| `rejected` | Rejected. |

`approve_change_request` drives the approval record; the platform may also require
the record to be in the correct state (e.g. Authorize) before approval is legal.

## Conflict scans
- `check_change_request_conflict` runs a conflict scan (schedule overlaps, blackout
  windows, CI collisions).
- `get_change_request_conflict` reads the results.
- `delete_change_request_conflict_scan` clears a prior scan.
Always scan + review before approving.
