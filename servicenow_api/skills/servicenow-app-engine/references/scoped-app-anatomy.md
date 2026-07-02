# Scoped-app anatomy

A scoped application is a set of metadata records bound to one **application scope**
(`sys_scope`). The scope is a namespace that isolates the app's tables, scripts, and APIs
from other apps and from the global scope.

## The scope & the `x_` prefix
- Every non-global scoped app has a scope identifier of the form **`x_<vendor>_<app>`**
  (e.g. `x_acme_pizza`). Store/ISV apps use the `x_` prefix; the platform reserves the
  bare/global namespace.
- Custom **tables** created in the app are prefixed with the scope:
  `x_<prefix>_<table>` (seen throughout the samples as `x_tablesample_*`,
  `x_helloworld_*`). Fields, script includes, and REST APIs are likewise scoped.
- Cross-scope access is explicit: a script include must be `access: 'public'` with a
  fully-qualified `api_name` (e.g. `x_sysmodulesample.SampleScriptInclude`) to be callable
  from another scope — see `servicenow-sdk-docs` → `references/dependencies-sample.md` and
  `sys_module-sample.md`.

## now.config.json
The SDK's app manifest. Key fields (see `servicenow-sdk-lifecycle` →
`references/project-init.md` for the full list):
- `scope` / `scopeId` — the `x_<prefix>_` namespace and its unique id.
- `name` — the application display name.
- generated-directory setting — where `dependencies`/`transform` write output.
- the dependency list — platform tables to fetch schema for.

## package.json
An ordinary npm/pnpm manifest that declares `@servicenow/sdk` and the `now-sdk` scripts
(build/deploy/etc.). It makes the project installable and buildable.

## src/fluent/ layout
```
src/
├── fluent/
│   ├── index.now.ts          # entry point
│   ├── <tables>.now.ts       # Table / Record definitions
│   ├── <rules>.now.ts        # BusinessRule / ScriptAction
│   ├── <security>.now.ts     # Acl / Role
│   ├── <nav>.now.ts          # ApplicationMenu
│   ├── <catalog>.now.ts      # ServiceCatalog
│   └── generated/            # dependency/transform output (auto-imported)
└── server/                   # server-side JS/TS referenced via Now.include(...) / imports
```
File names are conventional; what matters is that each `*.now.ts` exports Fluent
constructs and everything is reachable from the project.

## Gotchas
- **Choose the scope once.** Changing `x_<prefix>_` after tables exist means renaming every
  scoped artifact — decide it at init.
- Server scripts live in `src/server/` and are referenced (`Now.include('./x.server.js')`
  or an import), never inlined into the metadata object.
- `sys_scope` is the instance-side record for the scope; the app installs under it and its
  sys_id identifies the app for `servicenow_cicd` / update-set operations.
