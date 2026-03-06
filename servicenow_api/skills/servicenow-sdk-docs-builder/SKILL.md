---
name: servicenow-sdk-docs-builder
description: Automation skill to generate or update the `servicenow-sdk` documentation skill by fetching and processing the ServiceNow SDK and Examples repositories. It combines READMEs, extracts code samples, and creates a self-contained, portable documentation skill.
license: MIT
tags: [servicenow, sdk, documentation, builder, automation, documentation-generation]
metadata:
  author: Antigravity
  version: '0.1.0'
---
# ServiceNow SDK Docs Builder

This skill provides an automated pipeline for generating the `servicenow-sdk` documentation skill. It ensures that the documentation is always up-to-date with the latest examples and core SDK information.

## Workflow

To update the documentation skill, run the provided build script:

```bash
# From the skill's scripts directory
python build_docs.py --target /path/to/universal-skills/servicenow-sdk
```

### Automation Steps:
1.  **Sync Repositories**: (Optional) Pulls the latest changes from `https://github.com/ServiceNow/sdk` and `https://github.com/ServiceNow/sdk-examples`.
2.  **Combine READMEs**: Merges the main READMEs from both repositories, de-duplicating headers and categorizing content.
3.  **Process Samples**: Iterates through all examples in `sdk-examples`, mirroring source files into the target skill's `assets/` directory.
4.  **Generate References**: Creates detailed markdown reference files for each example with relative links to bundled source code.
5.  **Index Documentation**: Generates the main `SKILL.md` for the `servicenow-sdk` skill.

## Configuration

The builder uses the repositories mirrored at:
- `Workspace/sdk`
- `Workspace/sdk-examples`

Ensure these are present or use the `--sync` flag to fetch them.

## Troubleshooting

If the build fails, check the console output for specific errors related to directory structures or missing README files.
