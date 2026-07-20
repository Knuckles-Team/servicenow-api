# Build & transform

## build — Fluent → deployable package
```bash
now-sdk build
```
- Compiles everything under `src/fluent/**` into a deployable package.
- Validates syntax and reports errors — fix these before deploying.
- Converts third-party JS library dependencies into XML.
- **Always the prerequisite for `deploy`/`install`.**

## transform — existing XML → Fluent (adoption path)
```bash
now-sdk transform                 # convert metadata into Fluent
now-sdk transform <table> [...]   # target one or more specific tables
```
- Converts existing instance XML metadata into Fluent source, scaffolded into the
  generated directory configured in `now.config.json`.
- On success, **removes the converted metadata** and cleans up the transformed XML.
- Use when adopting an existing scoped app into code (complements `init --from`).

## Sequencing
```
author Fluent  →  now-sdk dependencies  →  now-sdk build  →  deploy/install
adopt existing →  init --from / transform →  now-sdk build →  deploy/install
```

## Gotchas
- **`transform` is destructive to source XML** — commit (or snapshot) before running so a
  bad conversion is recoverable.
- A stale build ships old metadata: re-run `build` after every Fluent edit before deploy.
- Compile errors at `build` often mean a missing dependency def — run
  `now-sdk dependencies` (see `dependencies.md`).
