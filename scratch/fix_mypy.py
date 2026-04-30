import re
import os


def fix_implicit_optional(content):
    # Fix 'arg: type = None' to 'arg: type | None = None'
    # Pattern: \b(\w+):\s*([\w\[\], ]+)\s*=\s*None
    # This is a bit risky for complex types, but let's try.

    # Simple case: arg: str = None -> arg: str | None = None
    content = re.sub(
        r"(\b\w+):\s*(str|int|bool|dict|list|float)\s*=\s*None",
        r"\1: \2 | None = None",
        content,
    )

    # Complex case: arg: list[str] = None -> arg: list[str] | None = None
    content = re.sub(
        r"(\b\w+):\s*([a-zA-Z]+\[[^\]]+\])\s*=\s*None", r"\1: \2 | None = None", content
    )

    return content


files_to_fix = [
    "servicenow_api/api_wrapper.py",
    "servicenow_api/mcp_server.py",
    "servicenow_api/auth.py",
]

for f in files_to_fix:
    if os.path.exists(f):
        print(f"Fixing {f}...")
        with open(f, "r") as f_in:
            content = f_in.read()
        new_content = fix_implicit_optional(content)
        if new_content != content:
            with open(f, "w") as f_out:
                f_out.write(new_content)
            print("  Done.")
        else:
            print("  No changes.")
