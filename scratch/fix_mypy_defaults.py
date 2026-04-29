import re
import os


def fix_mypy_defaults(content):
    # Fix 'arg: type = None' to 'arg: type | None = None'
    # Pattern: \b(\w+):\s*([\w\[\], |]+)\s*=\s*None

    # We want to match: sysparm_limit: int = None
    # And change to: sysparm_limit: int | None = None

    # regex for simple types
    content = re.sub(
        r"(\b\w+):\s*(int|str|bool|float|dict|list|Any)\s*=\s*None",
        r"\1: \2 | None = None",
        content,
    )

    # regex for complex types like list[str]
    content = re.sub(
        r"(\b\w+):\s*([a-zA-Z]+\[[^\]]+\])\s*=\s*None", r"\1: \2 | None = None", content
    )

    return content


files_to_fix = [
    "servicenow_api/api_wrapper.py",
    "servicenow_api/mcp_server.py",
    "servicenow_api/servicenow_models.py",
]

for f in files_to_fix:
    if os.path.exists(f):
        print(f"Fixing {f}...")
        with open(f, "r") as f_in:
            content = f_in.read()
        new_content = fix_mypy_defaults(content)
        if new_content != content:
            with open(f, "w") as f_out:
                f_out.write(new_content)
            print("  Done.")
        else:
            print("  No changes.")
