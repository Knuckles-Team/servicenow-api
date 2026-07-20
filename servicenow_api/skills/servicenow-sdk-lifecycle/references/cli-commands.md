# now-sdk CLI — command reference

Invoke as `npx @servicenow/sdk <command>` (no install) or `now-sdk <command>` when the
package is installed. This is a working summary; confirm flags against the
[official CLI reference](https://www.servicenow.com/docs/r/application-development/servicenow-sdk/servicenow-sdk-cli-commands.html)
when a flag is load-bearing, since they change per family release.

| Command | Purpose |
|---------|---------|
| `init` | Scaffold a new Fluent project, or convert an app already installed on an instance into a source-code project. |
| `auth` | Add / list / select stored instance credentials (basic or OAuth). Stored in the OS keychain. |
| `dependencies` | Fetch schema/type definitions for platform tables the project references into `src/fluent/generated`. |
| `build` | Compile the Fluent source into a deployable package; validate syntax and report errors. |
| `transform` | Convert existing instance XML metadata into Fluent source (scaffolds into the generated dir; removes converted metadata). |
| `deploy` / `install` | Push the built package to the authenticated instance. `build` must run first. |
| `version` | Print the CLI version (fast — does not load the project). |
| `upgrade` | Update the SDK / CLI to the latest release. |
| `help` | Show usage for the CLI or a subcommand (`now-sdk help <command>`). |

Startup for project-independent commands (`help`, `version`, `explain`) is fast because
they do not load the project.

## init
- `now-sdk init` — interactive scaffold; answer prompts (app name, package name, scope).
- `now-sdk init --from <sys_id_of_application>` — convert an installed scoped app into a
  code project (pull its metadata down as Fluent).
- Common prompts/flags: application name, package name, scope name, template.
- Produces the standard layout — see `project-init.md`.

## auth
- `now-sdk auth --add <instance-url> --type basic --alias <alias> --username <user>` —
  add a basic-auth profile (prompts for password interactively).
- Non-interactive (CI): `echo "$SN_PASSWORD" | now-sdk auth --add <url> --type basic --alias <alias> --username <user> --password-stdin`.
- `now-sdk auth --list` — list stored profiles. `now-sdk auth --use <alias>` — select the
  active profile. See `auth-and-profiles.md` for OAuth and CI patterns.

## dependencies
- `now-sdk dependencies` — reads the dependency list configured in `now.config.json` and
  writes type/schema definitions into `src/fluent/generated`, auto-imported by the project.
- Use when referencing a platform table not shipped with the SDK (e.g. `sc_cat_item`,
  `sys_ui_action`). Cross-reference: `servicenow-sdk-docs` →
  `assets/samples/dependencies-sample/` and `references/dependencies-sample.md`.

## build
- `now-sdk build` — compiles `src/fluent/**` into a deployable package. Third-party JS
  library dependencies are converted into XML. Run before every deploy/install.

## transform
- `now-sdk transform` — converts XML metadata into Fluent code in the generated directory
  (path configurable in `now.config.json`); on success, removes the converted metadata.
- Supports targeting one or more specific tables at a time. **Destructive to source XML —
  commit before running.**

## deploy / install
- `now-sdk deploy` / `now-sdk install` — push the built package to the active instance.
  `install` supports the OAuth `client_credentials` flow via env vars for CI/CD.
- `--auth <alias>` selects a stored profile. See `deploy-and-install.md`.

## version / upgrade / help
- `now-sdk version` — print CLI version. `now-sdk upgrade` — update the SDK.
- `now-sdk help [command]` — usage details.
