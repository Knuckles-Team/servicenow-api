---
name: servicenow-sdk-docs
skill_type: skill
description: A comprehensive, self-contained collection of ServiceNow SDK (Fluent API) examples and core documentation. Use this when the agent needs to reference how to use the ServiceNow SDK for various components like Tables, REST APIs, UI Actions, Script Includes, etc. All source code is bundled within the skill for portability.
license: MIT
tags: [servicenow, sdk, fluent-api, examples, typescript, reference, self-contained]
metadata:
  author: Antigravity
  version: '0.2.1'
---
# ServiceNow SDK Documentation (Self-Contained)

# ServiceNow SDK

The ServiceNow IDE and ServiceNow SDK support developing applications in source code with ServiceNow Fluent, creating JavaScript modules, and using third-party libraries. ServiceNow Fluent is a domain-specific programming language for creating application metadata in code.

This respository currently does not contain the source code for the SDK

### Support, Questions, and Announcements
Visit the [discussions](https://github.com/ServiceNow/sdk/discussions) section!

### Links

[NPM Package](https://www.npmjs.com/package/@servicenow/sdk)

[Documentation](https://www.servicenow.com/docs/r/application-development/servicenow-sdk/servicenow-sdk-landing.html)

[Release Notes](https://github.com/servicenow/sdk/releases)

[Community Forum](https://www.servicenow.com/community/servicenow-ide-sdk-and-fluent/bd-p/ide-sdk-fluent-forum)

[SDK Examples](https://github.com/servicenow/sdk-examples)


<h1 align="center">
ServiceNow SDK Samples
</h1>
This repository contains sample code illustrating the [ServiceNow SDK](https://docs.servicenow.com/csh?topicname=servicenow-sdk.html&version=latest) and Fluent language. You can read, play with or adapt from these samples to create your own application.
## Prerequisites
- [node](https://nodejs.org/en/) v20+
- [pnpm](https://pnpm.io/) v9+
## Usage
- `git clone https://github.com/ServiceNow/sdk-examples`
- `pnpm install` to install all dependencies on samples (optional can run individually)
- `code <sample directory>` to open one of the sample projects, e.g. hello-world-sample
- `pnpm run build` to build any of the sample projects if desired
## Samples
<!-- SAMPLES_BEGIN -->
| Sample Name                                                   | API & Contribution             |
| ------------------------------------------------------------- | ------------------------------ |
| [ACL](assets/samples/acl-sample/)                                   | ACL example                    |
| [Application Menu](assets/samples/applicationmenu-sample/)          | Application Menu example       |
| [Business Rule](assets/samples/businessrule-sample/)                | Business Rule example          |
| [Client Script](assets/samples/clientscript-sample/)                | Client Script example          |
| [Dependencies](assets/samples/dependencies-sample/)                 | Use table dependencies example |
| [Hello World](assets/samples/hello-world-sample/)                   | Basic sample application       |
| [List](assets/samples/list-sample/)                                 | List example                   |
| [Scripted Rest API](assets/samples/restapi-sample/)                 | RestApi simple example         |
| [Cross-Scope Module](assets/samples/sys_module-sample/)             | How to call module cross-scope |
| [Record](assets/samples/record-sample/)                             | Record example                 |
| [Tables](assets/samples/table-sample/)                              | Tables API sample              |
| [Automated Test Framework](assets/samples/test-atf-sample/)         | ATF test sample                |
| [React UI Page Typescript](assets/samples/react-ui-page-ts-sample/) | React Typescript sample        |
| [Service Portal](assets/samples/service-portal-sample/)             | Service Portal sample          |
| [UI Action](assets/samples/uiaction-sample/)                        | UiAction sample                |
| [Script Action](assets/samples/scriptaction-sample/)                | ScriptAction sample            |
| [Script Include](assets/samples/script-include-sample/)             | ScriptInclude sample           |
| [UI Page](assets/samples/uipage-sample/)                            | UiPage sample                  |
| [Service Catalog](assets/samples/service-catalog-sample/)           | Service Catalog sample         |
| [Flow](assets/samples/flow-sample/)                                 | Flow sample                    |
| [SolidJS UI Page](assets/samples/solidjs-ui-page-sample/)           | SolidJS UI Page sample         |
| [Svelte UI Page](assets/samples/svelte-ui-page-sample/)             | Svelte UI Page sample          |
| [Vue UI Page](assets/samples/vue-ui-page-sample/)                   | Vue UI Page sample             |
<!-- SAMPLES_END -->

## SDK Example Index

- [ACL Sample](references/acl-sample.md) - This example shows the the usage of ACLs with the now-sdk
- [Automated Test Framework (ATF) API Samples](references/test-atf-sample.md) - This example shows usage of the `Test` fluent interface for creating ATF Tests in ServiceNow.
- [BusinessRule Sample](references/businessrule-sample.md) - This example shows the the usage of the `BusinessRule` fluent interface for creating business rules ...
- [Dependencies Sample](references/dependencies-sample.md) - This example shows you how to use other tables in your ServiceNow instance as part of your applicati...
- [Flow Sample](references/flow-sample.md) - This is a sample of using the various `Flow` APIs available in the ServiceNow SDK
- [Hello World Sample](references/hello-world-sample.md) - This is a Hello World example that shows you how to set up and do basic configuration of the SDK.
- [React UIPage API Sample](references/react-ui-page-ts-sample.md) - This example shows the usage of the `UIPage` Fluent interface for creating UI Pages with React in Se...
- [Script Includes Sample](references/script-include-sample.md) - This example shows the the usage of script includes with the now-sdk and how to connect type informa...
- [ScriptAction Sample](references/scriptaction-sample.md) - This example shows the the usage of `ScriptAction` (`sysevent_script_action`)
- [Scripted Rest API Module Sample](references/restapi-sample.md) - This example shows the the usage of the `RestApi` fluent interface for creating scripted rest APIs i...
- [Service Catalog Sample](references/service-catalog-sample.md) - This is a sample of using the various `ServiceCatalog` APIs available in the ServiceNow SDK
- [Service Portal Sample](references/service-portal-sample.md) - This example shows the the usage of Service Portal with widgets and dependencies
- [Simple List API Sample](references/list-sample.md) - This example shows the basic usage of the `List` fluent interface for creating UI Lists in ServiceNo...
- [Simple List API Sample](references/clientscript-sample.md) - This example shows the basic usage of the `List` fluent interface for creating UI Lists in ServiceNo...
- [Simple Sys Module Sample](references/sys_module-sample.md) - These examples show two techniques to call a module cross-scope.
- [Simple Table API Sample](references/record-sample.md) - This example shows the basic usage of the `Record` fluent interface for creating Tables in ServiceNo...
- [Simple Table API Sample](references/applicationmenu-sample.md) - This example shows the basic usage of the `ApplicationMenu` fluent interface for creating Applicatio...
- [Simple Table API Sample](references/table-sample.md) - This example shows the basic usage of the `Table` fluent interface for creating Tables in ServiceNow
- [Svelte UI Example](references/svelte-ui-page-sample.md) - No description provided.
- [UI Page Sample](references/uipage-sample.md) - This example shows the the usage of `UiPage` (`sys_ui_page`)
- [UiAction Sample](references/uiaction-sample.md) - This example shows the the usage of `UiAction` (`sys_ui_action`)
- [solidjs-ui-page-sample](references/solidjs-ui-page-sample.md) - No description provided.
- [vue-ui-page-sample](references/vue-ui-page-sample.md) - No description provided.

---

## Technical Details

- **Self-Contained**: All examples are mirrored in `assets/samples/`.
- **SDK Version**: Latest Fluent API
- **Structure**: Each sample represents a standalone ServiceNow application or component implementation using the SDK.

## Troubleshooting

If you cannot find a specific example, try searching by keywords (e.g., 'portal', 'rest', 'acl') within this skill or the `references/` directory.
