# ATF — authoring & running tests

Automated Test Framework (ATF) tests are authored as Fluent (`Test(...)` from
`@servicenow/sdk/core`) and run either from the instance UI or via the MCP testing tool
as part of CI/CD.

## Authoring (cross-reference — do not copy)
The full worked examples — REST table-API test, record query/insert, output variables
across steps, impersonation, and multi-batch UI/server tests — are bundled at:
- `servicenow-sdk-docs` → `assets/samples/test-atf-sample/`
- `servicenow-sdk-docs` → `references/test-atf-sample.md`

Shape (illustrative only; see the sample for real steps):
```typescript
import { Test } from '@servicenow/sdk/core'
export default Test(
  { $id: Now.ID['my_test'], active: true, name: '...', description: '...' },
  (atf) => {
    atf.server.recordInsert({ $id: 'step1', table: 'incident', fieldValues: { short_description: '...' }, assert: 'record_successfully_inserted' })
    // atf.rest.* / atf.form.* / atf.server.* steps ...
  }
)
```
Group tests into a **test suite** on the instance so they can be run as a unit.

## Running (MCP — `servicenow_testing`)
Run a suite (action `run_test_suite`):
```json
{"test_suite_sys_id":"<suite_sys_id>","os_name":"","os_version":"","browser_name":"","browser_version":""}
```
Or identify the suite by name if the tool accepts `test_suite_name`. The call returns a
result/progress handle — poll or fetch the result to determine pass/fail.

## Placement in the lifecycle
```
build → deploy/install → run_test_suite → (gate promotion on green) → app_repo_publish
```
ATF is the validation gate before promoting a version across environments.

## Gotchas
- ATF must be enabled on the instance and, for UI steps, a client-test runner/browser
  must be available; REST/server steps run headless.
- REST inbound steps need a basic-auth profile selected on the step (see the sample's
  `atf-record-rest.now.ts` note).
- A `$id` can be an explicit sys_id or `Now.ID[...]`; keep it stable so re-deploys update
  the same test rather than creating duplicates.
