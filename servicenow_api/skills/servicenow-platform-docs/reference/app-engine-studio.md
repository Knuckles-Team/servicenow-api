# App Engine Studio / Application Studio

> Product reference (concepts, not code). Sources:
> - App Engine Studio overview — https://www.servicenow.com/docs/bundle/zurich-application-development/page/build/app-engine-studio/concept/aes-overview.html
> - Building apps in AES — https://www.servicenow.com/docs/bundle/vancouver-application-development/page/build/app-engine-studio/concept/aes-app-creation.html
> - Product page — https://www.servicenow.com/products/app-engine-studio.html
> - App Engine product — https://www.servicenow.com/products/now-platform-app-engine.html

## What it is

**App Engine Studio (AES)** is ServiceNow's guided **low-code** application development
environment. It lets developers and builders of all skill levels — including
**citizen developers** — create workflow apps quickly through visual tooling rather than
pure code. Apps built in AES run on the **same governed Now Platform** as core
ServiceNow workflows, inheriting security, audit trails, and change management.

**Application Studio** (the classic **Studio** IDE / broader App Engine ecosystem) is
the pro-code counterpart: a full application development workspace for building and
managing **scoped applications** with deeper scripting and extensibility. AES emphasizes
guided visual development (with **Now Assist** AI assistance); Application Studio /
Studio provides deeper pro-code extensibility for complex customizations.

## How you build a low-code app (AES flow)

1. **Create an application** — give it a name and a **namespace/scope** identifier
   (isolates it from the global scope and other apps).
2. **Add data** — define the **data model**: custom **tables** and **fields** that store
   the app's records.
3. **Design the experience / UI** — build **forms**, list views, workspaces, and portal
   experiences visually; add question types, validation, and dynamic behavior.
4. **Add logic / automation** — wire **flows**, **playbooks**, triggers, decision logic,
   and integrations (authored via Flow Designer / Workflow Studio — see
   `reference/flow-designer.md`).
5. **Set roles & access** — assign application access roles.
6. **Test and deploy** — package and promote through the **App Engine Management
   Center (AEMC)**.

## Key concepts and components

- **Scoped application** — an isolated app within its own namespace; changes are captured
  in **update sets** for safe promotion.
- **Data tables / fields** — the app's custom database schema.
- **Forms & questions** — user-input interfaces bound to table records, with validation
  and dynamic behavior; reusable **templates** and question sets accelerate creation.
- **Experiences / UI** — workspaces, portals, record layouts, and other user-facing
  surfaces.
- **Flows / playbooks** — automation and guided process logic (from Workflow Studio).
- **App Engine Management Center (AEMC)** — the governance hub for **deployment,
  testing, intake/requests**, and compliance monitoring across the app portfolio.
- **Roles / citizen developer** — governance-based access (e.g., app admin / app
  developer / app user roles) so non-technical builders can participate safely under
  guardrails.
- **Templates** — reusable app, catalog, and question templates that jump-start builds.

## AES vs. Application Studio (when each)

- **AES** — fastest path for citizen and core developers; guided, visual, AI-assisted;
  scales with scoped apps + AEMC governance.
- **Application Studio / Studio** — pro-code IDE for advanced scripting, business rules,
  script includes, UI scripts, and complex platform customization beyond the AES canvas.

## How it fits the Now Platform

App Engine is the platform's **application-building layer**. It composes the other
layers: the **data layer** (tables), the **automation layer** (Flow Designer / Workflow
Studio), and platform services (ACLs, audit, update sets). It is the on-ramp for
custom apps that sit alongside ITSM, IRM, and SecOps on one platform.
