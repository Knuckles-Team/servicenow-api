import re
import os


def fix_vulture_unused(content):
    # Fix unused 'cls' in methods (mostly validators)
    content = re.sub(r"def\s+(\w+)\s*\(\s*cls\b", r"def \1(_cls", content)
    # Fix unused '__context'
    content = re.sub(r",\s*__context\b", r", _context", content)

    return content


files_to_fix = ["servicenow_api/servicenow_models.py", "servicenow_api/mcp_server.py"]

for f in files_to_fix:
    if os.path.exists(f):
        print(f"Fixing {f}...")
        with open(f, "r") as f_in:
            content = f_in.read()
        new_content = fix_vulture_unused(content)
        if new_content != content:
            with open(f, "w") as f_out:
                f_out.write(new_content)
            print("  Done.")
        else:
            print("  No changes.")
