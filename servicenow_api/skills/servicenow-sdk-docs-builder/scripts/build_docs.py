import argparse
import os
import shutil


def merge_readmes(sdk_readme_path, examples_readme_path):
    with open(sdk_readme_path) as f:
        sdk_content = f.read()
    with open(examples_readme_path) as f:
        examples_content = f.read()

    # Simple merging logic: combine them and de-duplicate common headers
    # The first few lines are identical in both
    sdk_lines = sdk_content.splitlines()
    examples_lines = examples_content.splitlines()

    unique_examples = []
    seen_lines = set(sdk_lines)

    for line in examples_lines:
        if line not in seen_lines:
            unique_examples.append(line)

    merged = sdk_content + "\n\n" + "\n".join(unique_examples)
    return merged


def process_samples(source_dir, skill_dir):
    ref_dir = os.path.join(skill_dir, "references")
    asset_samples_dir = os.path.join(skill_dir, "assets", "samples")

    os.makedirs(ref_dir, exist_ok=True)
    os.makedirs(asset_samples_dir, exist_ok=True)

    samples = []

    for item in os.listdir(source_dir):
        item_path = os.path.join(source_dir, item)
        if os.path.isdir(item_path) and not item.startswith("."):
            readme_path = os.path.join(item_path, "README.md")
            title = item
            description = "No description provided."

            if os.path.exists(readme_path):
                with open(readme_path) as f:
                    lines = f.readlines()
                    if lines:
                        title = lines[0].strip("# ").strip()
                        if len(lines) > 2:
                            description = "".join(
                                [
                                    line.strip()
                                    for line in lines[1:]
                                    if line.strip() and not line.startswith("[")
                                ]
                            ).strip()

            # Find code files recursively in src/
            code_files = []
            src_dir = os.path.join(item_path, "src")
            sample_asset_dir = os.path.join(asset_samples_dir, item)

            if os.path.exists(src_dir):
                if not os.path.exists(sample_asset_dir):
                    os.makedirs(sample_asset_dir, exist_ok=True)

                for root, _, files in os.walk(src_dir):
                    # Skip 'generated' folders often found in SDK examples
                    if "generated" in root:
                        continue
                    for file in files:
                        if file.endswith(".now.ts"):
                            src_cf = os.path.join(root, file)
                            rel_path_in_src = os.path.relpath(src_cf, src_dir)
                            dst_cf = os.path.join(sample_asset_dir, rel_path_in_src)
                            os.makedirs(os.path.dirname(dst_cf), exist_ok=True)
                            shutil.copy2(src_cf, dst_cf)
                            code_files.append(dst_cf)

            samples.append(
                {
                    "id": item,
                    "title": title,
                    "description": description,
                    "code_files": code_files,
                }
            )

    # Generate reference files
    for sample in samples:
        ref_file_path = os.path.join(ref_dir, f"{sample['id']}.md")
        with open(ref_file_path, "w") as f:
            f.write(f"# {sample['title']}\n\n")
            f.write(f"{sample['description']}\n\n")
            f.write("## Example Location\n")
            f.write(
                f"Source Code: [assets/samples/{sample['id']}](../assets/samples/{sample['id']})\n\n"
            )

            if sample["code_files"]:
                f.write("## Code Samples\n\n")
                for cf in sample["code_files"]:
                    rel_cf = os.path.relpath(cf, asset_samples_dir)
                    rel_to_ref = os.path.join("..", "assets", "samples", rel_cf)
                    f.write(f"### `{os.path.basename(cf)}`\n")
                    f.write(f"Path: [{rel_cf}]({rel_to_ref})\n\n")
                    f.write("```typescript\n")
                    with open(cf) as cf_file:
                        f.write(cf_file.read())
                    f.write("\n```\n\n")
    return samples


def generate_skill_md(target_path, samples, merged_readme_content):
    samples.sort(key=lambda x: x["title"])

    # Extract some context from merged README if possible
    content = f"""---
name: servicenow-sdk
description: A comprehensive, self-contained collection of ServiceNow SDK (Fluent API) examples and core documentation. Use this when the agent needs to reference how to use the ServiceNow SDK for various components like Tables, REST APIs, UI Actions, Script Includes, etc. All source code is bundled within the skill for portability.
license: MIT
tags: [servicenow, sdk, fluent-api, examples, typescript, reference, self-contained]
metadata:
  author: Antigravity
  version: '0.2.1'
---
# ServiceNow SDK Documentation (Self-Contained)

{merged_readme_content}

## SDK Example Index

"""

    for sample in samples:
        short_desc = sample["description"].split("\n")[0][:100]
        if len(sample["description"].split("\n")[0]) > 100:
            short_desc += "..."
        content += (
            f"- [{sample['title']}](references/{sample['id']}.md) - {short_desc}\n"
        )

    content += """
---

## Technical Details

- **Self-Contained**: All examples are mirrored in `assets/samples/`.
- **SDK Version**: Latest Fluent API
- **Structure**: Each sample represents a standalone ServiceNow application or component implementation using the SDK.

## Troubleshooting

If you cannot find a specific example, try searching by keywords (e.g., 'portal', 'rest', 'acl') within this skill or the `references/` directory.
"""

    with open(target_path, "w") as f:
        f.write(content)


def main():
    parser = argparse.ArgumentParser(
        description="Build ServiceNow SDK documentation skill"
    )
    parser.print_usage()
    parser.add_argument(
        "--sdk-path",
        default=os.path.expanduser("~/Workspace/sdk"),
        help="Path to sdk repo",
    )
    parser.add_argument(
        "--examples-path",
        default=os.path.expanduser("~/Workspace/sdk-examples"),
        help="Path to sdk-examples repo",
    )
    parser.add_argument("--target", required=True, help="Target skill directory")

    args = parser.parse_args()

    # Ensure repos exist
    if not os.path.exists(args.sdk_path) or not os.path.exists(args.examples_path):
        print("Error: Missing repositories. Please clone them first.")
        return

    # 1. Merge READMEs
    merged_readme = merge_readmes(
        os.path.join(args.sdk_path, "README.md"),
        os.path.join(args.examples_path, "README.md"),
    )

    # 2. Process samples
    samples = process_samples(args.examples_path, args.target)

    # 3. Generate SKILL.md
    generate_skill_md(os.path.join(args.target, "SKILL.md"), samples, merged_readme)

    print(f"Successfully generated documentation skill at {args.target}")


if __name__ == "__main__":
    main()
