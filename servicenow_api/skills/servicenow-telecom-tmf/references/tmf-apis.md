# TM Forum Open APIs on ServiceNow — API → purpose → endpoint/table map (discover-first)

> **CANDIDATE / typical paths.** ServiceNow exposes TM Forum Open APIs through
> Store-installed scoped telecom apps (TSM/TSOM). The **exact scoped-app REST path,
> API version, scope prefix, and backing table depend on which TMF plugins are
> installed** on the instance — they are NOT guaranteed. Always discover what's
> installed before calling a raw endpoint. Query/aggregate/table mechanics come from
> the `servicenow-table-api` skill; the raw-call mechanics come from
> `servicenow_custom_api` `api_request`.

## Discover-first recipe
1. **List installed telecom scopes** via `api_request`:
   ```json
   {"method":"GET","endpoint":"api/now/table/sys_db_object?sysparm_query=nameSTARTSWITHsn_ind_&sysparm_fields=name,label,sys_scope&sysparm_limit=200"}
   ```
   Look for prefixes such as `sn_ind_tmt_*` (telecom technology / orchestration) and
   `sn_ind_tsm_*` (telecom service management).
2. **Inspect scoped REST APIs** registered on the instance:
   ```json
   {"method":"GET","endpoint":"api/now/table/sys_ws_definition?sysparm_query=nameLIKEtmf&sysparm_fields=name,base_uri,sys_scope&sysparm_limit=100"}
   ```
   The `base_uri` is the real path to call.
3. Only then build `api_request` calls against the confirmed `base_uri`.

## TMF API map (candidate paths)

| TMF # | API | Purpose | Domain-typed tool | Candidate scoped path / backing area |
|-------|-----|---------|-------------------|--------------------------------------|
| TMF622 | Product Ordering | Create/track product orders | — (use `api_request`) | `api/sn_ind_tmt_*/tmf-api/productOrderingManagement/v4/productOrder` |
| TMF637 | Product Inventory | Query/manage installed products | `servicenow_product_inventory` | `api/sn_ind_tmt_*/tmf-api/productInventoryManagement/v4/product` |
| TMF641 | Service Ordering | Create/track service orders | — (use `api_request`) | `api/sn_ind_tmt_*/tmf-api/serviceOrderingManagement/v4/serviceOrder` |
| TMF642 | Alarm Management | Query/ack/clear alarms | — (use `api_request`) | `api/sn_ind_tmt_*/tmf-api/alarmManagement/v4/alarm` |
| TMF645 | Service Qualification | Check if a service can be delivered | `servicenow_service_qualification` | `api/sn_ind_tmt_*/tmf-api/serviceQualificationManagement/v4/checkServiceQualification` |
| TMF666 / TMF629 | Account / Customer Mgmt | Fetch billing account / customer | `servicenow_account` | `api/sn_ind_tmt_*/tmf-api/accountManagement/v4/*` |
| TMF632 | Party Management | Individuals / organizations | — (use `api_request`) | `api/sn_ind_tmt_*/tmf-api/partyManagement/v4/*` |
| TMF620 | Product Catalog | Product offerings/specs | — (use `api_request`) | `api/sn_ind_tmt_*/tmf-api/productCatalogManagement/v4/*` |
| TMF638 | Service Inventory | Query service instances | — (use `api_request`) | `api/sn_ind_tmt_*/tmf-api/serviceInventoryManagement/v4/service` |

> Notes: the `v4` version segment and the `sn_ind_tmt_*` scope prefix are **candidates**
> — confirm the real `base_uri` and version via the discover-first recipe above. Some
> deployments front these APIs under `sn_ind_tsm_*` or a customer-specific scope.

## Body/resource-model notes
- TMF bodies are polymorphic — objects carry an `@type` and nest related resources
  (`serviceQualificationItem`, `relatedParty`, `place`, `productSpecification`, …).
- Validate the exact required/optional fields against **your installed app's API
  version** — TM Forum resource models evolve between v4/v5.
- For reads, TMF supports field selection + paging query params (e.g. `?fields=...`,
  `?limit=...&offset=...`, and attribute filters) — keep result sets bounded.

## When to fall back
- No TMF endpoint for what you need, but data lives in a plain scoped table → use the
  `servicenow-table-api` skill against that table (discover it via `sys_db_object`).
