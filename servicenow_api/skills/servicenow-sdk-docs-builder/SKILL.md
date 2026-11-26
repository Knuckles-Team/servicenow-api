---
name: servicenow-sdk-docs-builder
skill_type: skill
description: Automation skill to generate or update the `servicenow-sdk-docs` documentation skill by fetching and processing the ServiceNow SDK and Examples repositories. It combines READMEs, extracts code samples, harvests the SDK CLI/auth docs, and creates a self-contained, portable documentation skill.
license: MIT
tags: [servicenow, sdk, documentation, builder, automation, documentation-generation]
metadata:
  author: Repository Maintainers
  version: '0.2.0'
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
5.  **Harvest CLI Docs**: Scans the `sdk` repo's `README.md` and `docs/**` for CLI / auth / command-oriented markdown and mirrors each into `references/cli-*.md`, keeping the `now-sdk` CLI surface refreshed for the `servicenow-sdk-lifecycle` skill to reference.
6.  **Index Documentation**: Generates the main `SKILL.md` for the `servicenow-sdk-docs` skill (samples + a "SDK CLI & Tooling Reference" section), emitting `name: servicenow-sdk-docs` at version `0.3.0`.

## Steps

1. Check the source repositories exist locally, and verify both `sdk` and `sdk-examples` directories are present.
2. Run `python build_docs.py --sync --target <output dir>` from the scripts directory, and verify the console reports each sample processed.
3. List the output with `ls <output dir>/references`, and verify one reference file per sample plus the `cli-*.md` files exist.
4. Open the generated `SKILL.md`, and verify it has `name: servicenow-sdk-docs` and the sample index table.

## Failure recovery

| Failure | Cause | Recovery |
|---|---|---|
| Build cannot find the repositories | Sources not cloned at the configured paths | Re-run with `--sync` so the script fetches both repositories |
| Missing README error | Upstream directory layout changed | Open the upstream repository, adjust the README path, and re-run `python build_docs.py` |
| Output skill lacks CLI references | No CLI markdown found in the SDK `docs/` | Check the SDK checkout is current and rerun with `--sync` |

## Configuration

The builder uses the repositories mirrored at:
- `Workspace/sdk`
- `Workspace/sdk-examples`

Ensure these are present or use the `--sync` flag to fetch them.

## Troubleshooting

If the build fails, check the console output for specific errors related to directory structures or missing README files.
