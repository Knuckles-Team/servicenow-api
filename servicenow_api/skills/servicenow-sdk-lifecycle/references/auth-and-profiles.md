# Auth & instance profiles

The CLI stores per-instance credentials in the OS keychain / credential manager — never
in the repo. A profile (alias) binds an instance URL to a credential.

## Interactive basic auth
```bash
now-sdk auth --add https://<instance>.service-now.com --type basic \
  --alias dev --username <user>
# prompts for password, stores it in the keychain
now-sdk auth --list          # show stored profiles
now-sdk auth --use dev       # make 'dev' the active profile
```

## Non-interactive (CI/CD)
Basic auth from a secret, no prompt:
```bash
echo "$SN_PASSWORD" | now-sdk auth --add https://<instance>.service-now.com \
  --type basic --alias ci --username "$SN_USER" --password-stdin
```
OAuth `client_credentials` for `install` in a pipeline is driven by environment
variables (client id/secret + instance) rather than an interactive prompt — see the
official CLI docs for the exact env-var names for your family release.

## Profiles vs. MCP credentials
- **CLI auth** governs what `build`/`deploy`/`install`/`dependencies` talk to.
- **MCP tools** authenticate separately via `SERVICENOW_INSTANCE` / `SERVICENOW_USERNAME`
  / `SERVICENOW_PASSWORD` (+ optional OAuth) — see
  `agent-tools/mcp-client/references/servicenow-api.md`.
- These are independent. Before deploying, confirm the active CLI profile and
  `SERVICENOW_INSTANCE` point at the intended instance.

## Gotchas
- Keychain access can fail in headless CI — prefer `--password-stdin` or OAuth env flow.
- Rotating a password invalidates the stored profile; re-run `auth --add` (same alias
  overwrites).
