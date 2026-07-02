# App Engine Studio / Application Studio — concepts

Two UI surfaces build the same scoped-app metadata this skill authors as code:
- **Application Studio** (the "Studio" IDE) — the classic developer surface: a file-tree of
  every metadata record in the scope (tables, business rules, ACLs, script includes, UI
  actions, menus, …). It maps almost 1:1 to Fluent constructs.
- **App Engine Studio (AES)** — the guided, low-code app-builder. It groups the same
  records under task-oriented sections rather than raw table names.

## AES artifact vocabulary → what it really is
| AES section | Underlying metadata (what Fluent emits) |
|-------------|-----------------------------------------|
| **Data** (tables & columns) | `sys_db_object` / `sys_dictionary` → `Table` + Column types |
| **Experience** (pages, portals, workspaces) | UI pages, Service Portal, UX records → `UiPage`, Service Portal widgets, React/Solid/Svelte/Vue UI pages |
| **Logic and automation** | Business rules, flows, actions, script includes → `BusinessRule`, `Flow`/`Subflow`, `ScriptAction`, script includes |
| **Security** | ACLs and roles → `Acl`, `Role` |
| **Requests / catalog** | Catalog items, record producers, variable sets → `ServiceCatalog` |
| **Connections / integrations** | Scripted REST APIs, integrations → `RestApi` |

## How code-first coexists with the UI
- Both write to the **same instance records** in the same scope. A code-built app is
  indistinguishable on the instance from a UI-built one.
- **UI → code:** adopt an existing AES/Studio app with `now-sdk init --from <sys_id>` or
  convert specific metadata with `now-sdk transform` (see `servicenow-sdk-lifecycle`).
- **code → UI:** after deploy, the artifacts appear in Studio/AES and can be inspected or
  (with care) edited there.

## Reconciliation guidance
- Pick **one source of truth per artifact**. Editing the same record from both AES and
  Fluent will conflict on the next deploy/transform.
- Prefer code-first for anything that benefits from review/versioning (data model, logic,
  security); AES is convenient for rapid experience/page building, which can then be
  transformed into code.
- Use `servicenow_flows` (via `servicenow-workflow-studio`) to introspect UI-built flows
  before transforming them, so the generated Fluent is understood, not blindly imported.

## Gotchas
- AES may create helper/config records (e.g. UX experience records) that have no
  first-class Fluent construct yet — `transform`/`init --from` captures them as generic
  `Record({...})` entries; treat those as generated and avoid hand-editing.
- Roles/ACLs created in AES must still be referenced by name/scope in Fluent
  (`x_<prefix>.role_name`) — see `acl-sample`.
