# Path A — native Studio source control

ServiceNow's own git client pulls from (or imports) the GitLab repository directly.
Simpler than Path B when it's reachable — no external CI runner needed — but it
requires **inbound** reach from the ServiceNow instance to the GitLab host.

## The recipe

1. **Import** the repo as a new scoped app (`servicenow_source_control`, action
   `import_repository`):
   ```json
   {"repo_url":"https://gitlab.example/group/app-repo.git","branch_name":"main","credential_sys_id":"<credential_sys_id>"}
   ```
   `repo_url` is required; `credential_sys_id` points at a stored ServiceNow
   credential record (basic auth or SSH key) the instance uses to authenticate to
   GitLab. `auto_upgrade_base_app` is optional.
2. **Pull further changes** into the now-existing app (action
   `apply_remote_source_control_changes`):
   ```json
   {"app_sys_id":"<app_sys_id>","scope":"x_myco_app","branch_name":"main"}
   ```
   Requires `app_sys_id` **or** `scope`.
3. **Promote** with `servicenow_cicd` (`app_repo_publish`/`app_repo_install`) —
   full contract: `servicenow-cicd-devops` → `references/actions-catalog.md`.

## The hard requirement: inbound reachability

Both calls above are made **by the ServiceNow instance itself**, outbound from
ServiceNow to the GitLab host. If GitLab is only reachable through an access
proxy (for example, a Cloudflare Access-fronted internal GitLab), the request
must satisfy that proxy's auth challenge — and **ServiceNow's native git client
cannot attach a custom header** (an Access service-token pair) to its outbound
git/HTTP calls. A plain `credential_sys_id` (basic auth / SSH key) is not enough
on its own in that topology.

## What the owner must approve — pick exactly one

Neither option is created, weakened, or bypassed by this skill; both are
infrastructure decisions with real trade-offs that only the resource owner can
make:

1. **Issue an access-proxy service token scoped to the GitLab hostname, fronted
   by a small credential-injection proxy.** The proxy sits between ServiceNow
   and the access-controlled GitLab host, attaches the service-token header
   ServiceNow's git client can't send itself, and forwards the request.
   Narrowly scoped (one hostname, one token), but adds an operational
   component that must itself be secured and kept alive.
2. **Add an access-proxy bypass policy for ServiceNow's outbound egress IP
   range(s), scoped to that one GitLab hostname.** Simpler — no extra
   component — but it widens what can reach that hostname unauthenticated to
   anything able to route through (or spoof) those egress IPs, not just the
   ServiceNow instance itself.

If neither has been approved, Path A cannot reach a proxy-fronted GitLab —
fall back to Path B (GitLab CI reaching outbound to ServiceNow instead) or stop
and flag the perimeter gap; do not attempt a workaround that weakens the proxy.

## Diagnosing a Path-A failure

- **`import_repository`/`apply_remote_source_control_changes` times out or
  errors with a connection/auth failure** → almost always the perimeter gap
  above, not a bad `credential_sys_id`. Confirm by checking whether the GitLab
  host is reachable *from the ServiceNow instance's network*, not from wherever
  the agent is running.
- **`MissingParameterError`** → check the required-key table in the recipe
  above (`repo_url` for import; `app_sys_id` or `scope` for apply) — see
  `servicenow-cicd-devops` → `references/actions-catalog.md` for the same
  silent-drop gotcha that applies to every `CICDModel`-backed action.
- **Import succeeds but `apply_remote_source_control_changes` doesn't pick up
  new commits** → confirm `branch_name` matches the branch actually pushed to
  (Path B's pipeline pushes to `main` by default — see
  `references/path-b-gitlab-ci.md`).
