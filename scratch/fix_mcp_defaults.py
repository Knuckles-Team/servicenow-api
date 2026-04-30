import re
import os


def fix_mcp_defaults(content):
    # Fix os.environ.get(...) defaults that cause type mismatches
    # Pattern: default=os.environ.get\("(\w+)", to_integer\(string="(\d+)"\)\)
    content = re.sub(
        r'default=os\.environ\.get\("(\w+)", to_integer\(string="(\d+)"\)\)',
        r'default=to_integer(os.environ.get("\1", "\2"))',
        content,
    )

    # Also handle simpler cases
    content = re.sub(
        r'default=os\.environ\.get\("(\w+)", "(\d+)"\)',
        r'default=to_integer(os.environ.get("\1", "\2"))',
        content,
    )

    return content


f = "servicenow_api/mcp_server.py"
if os.path.exists(f):
    print(f"Fixing {f}...")
    with open(f, "r") as f_in:
        content = f_in.read()
    new_content = fix_mcp_defaults(content)
    if new_content != content:
        with open(f, "w") as f_out:
            f_out.write(new_content)
        print("  Done.")
    else:
        print("  No changes.")
