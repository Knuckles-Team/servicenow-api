# Project init & layout

## Scaffold a new project
```bash
mkdir my-app && cd my-app
now-sdk init          # answer prompts: app name, package name, scope
```

## Convert an installed app to code
```bash
now-sdk init --from <sys_id_of_application>
```
Pulls the installed scoped app's metadata down as a Fluent project so it can be managed
as code going forward.

## Standard layout
```
my-app/
├── package.json          # npm/pnpm project + now-sdk scripts + @servicenow/sdk dep
├── now.config.json       # SDK config: scope, name, generated-dir, dependencies
├── src/
│   ├── fluent/           # your Fluent metadata (*.now.ts) — the source of truth
│   │   ├── index.now.ts  # entry point
│   │   └── generated/    # `dependencies`/`transform` output (auto-imported)
│   └── server/           # server-side JS/TS referenced via Now.include(...) / imports
└── .now-sdk/             # local CLI state (gitignored)
```

## now.config.json (key fields)
- `scope` / `scopeId` — the application scope (the `x_<prefix>_` namespace).
- `name` — application display name.
- generated-directory setting — where `dependencies` and `transform` write output
  (commonly `src/fluent/generated`).
- dependency list — the platform tables to fetch defs for (consumed by `now-sdk dependencies`).

Deeper anatomy of the scope, `x_` prefix, and how these files map to `sys_scope` lives in
`servicenow-app-engine` → `references/scoped-app-anatomy.md`.

## First build
```bash
pnpm install        # install @servicenow/sdk + deps
now-sdk build       # compile Fluent → deployable package
```

Reference the bundled starter: `servicenow-sdk-docs` →
`assets/samples/hello-world-sample/` and `references/hello-world-sample.md` (a table +
a seed record — the minimal working project).
