# TRM / APM — candidate tables & fields (discover-first)

> **These are CANDIDATE / typical table names.** Scoped-app (`sn_apm_*`) and custom
> (`u_*`) tables — and their fields and choice values — **vary by instance and by
> plugin version**. Always confirm with a one-row probe before trusting any name:
> ```json
> {"table":"<candidate>","sysparm_limit":1,"sysparm_display_value":"all"}
> ```
> Inspect the returned keys to learn the real fields. All query/aggregate mechanics
> come from the `servicenow-table-api` skill.

## Discover-first recipe
1. **Find the tables.** List scoped tables via the dictionary:
   `servicenow_table_api` `get_table` on `sys_db_object` filtered by prefix —
   ```json
   {"table":"sys_db_object","sysparm_query":"nameSTARTSWITHsn_apm_^ORnameSTARTSWITHsamp_","sysparm_fields":"name,label,sys_scope","sysparm_limit":100}
   ```
2. **Inspect fields.** Probe each candidate with `sysparm_limit:1` +
   `sysparm_display_value:all` and read the keys.
3. **Confirm choice values.** For a lifecycle/approval field, list its choices via
   `get_table` on `sys_choice`:
   ```json
   {"table":"sys_choice","sysparm_query":"name=cmdb_software_product_model^element=life_cycle_stage","sysparm_fields":"value,label,sequence"}
   ```
4. Only then build inventory / roll-up / update queries.

## Candidate tables

| Candidate table | Typical purpose |
|-----------------|-----------------|
| `sn_apm_application` | APM business-application / application portfolio record |
| `sn_apm_capability` | Business capability the application supports |
| `sn_apm_app_indicator` / `sn_apm_indicator` | Application health / assessment indicators |
| `cmdb_ci_business_app` | CMDB business-application CI (often linked from APM) |
| `cmdb_software_product_model` | Software product model — **lifecycle & EOL live here** |
| `samp_sw_product_lifecycle` | SAM Pro software-product lifecycle (publisher lifecycle dates) |
| `cmdb_model_category` | Model category (classifies hardware/software models) |
| `cmdb_ci_spkg` / `cmdb_sam_sw_install` | Installed-software / software package records |
| `u_trm_request` | Custom TRM request/intake table (tracker composes this) |
| `dmn_demand` | Demand Management record (TRM asks often flow through demand) |

## Candidate fields (confirm per instance)

**Lifecycle / approval (technology & software)**
- `life_cycle_stage`, `life_cycle_stage_status` — software-product lifecycle stage/status.
- `end_of_life`, `end_of_support`, `end_of_sale` — software EOL/EOS/EOSale dates
  (typically on `cmdb_software_product_model` / `samp_sw_product_lifecycle`).
- `u_lifecycle_stage` / `u_approval_state` — common **custom** stage/approval fields on
  scoped or `u_*` records; values often model `Approved` / `Emerging` / `Retirement` /
  `End-of-life` as choices (confirm via `sys_choice`).

**Portfolio / ownership**
- `name`, `number`, `short_description`, `owned_by`, `managed_by_group`, `it_application_owner`.
- `install_status`, `operational_status`, `active`.

**Technical debt / architecture compliance**
- `u_technical_debt`, `u_risk_score`, `u_architecture_standard`, `u_standard_compliance`
  (naming is instance-specific — discover it).

## Common encoded queries (see servicenow-table-api for syntax)
- Active portfolio, newest first: `active=true^ORDERBYDESCsys_created_on`
- By lifecycle stage: `life_cycle_stage=end_of_life`
- EOL within next year: `end_of_lifeISNOTEMPTY^end_of_life<=javascript:gs.beginningOfNextYear()^ORDERBYend_of_life`
- Non-compliant with a standard: `u_standard_compliance=false` (confirm field name)

## Aggregate roll-ups (servicenow_aggregate `get_stats`)
- Count by lifecycle stage: `groupby` = the lifecycle field (e.g. `life_cycle_stage`).
- Count by owner group: `groupby` = `managed_by_group`.
- `get_stats` maps `groupby`→`sysparm_group_by`, `stats:true`→`sysparm_count=true`.
