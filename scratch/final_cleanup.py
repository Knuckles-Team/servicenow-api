import re
import os


def final_cleanup(content, filename):
    if filename.endswith("servicenow_models.py"):
        # Fix remaining unused cls by renaming to _cls
        # (Only in signatures where it's actually unused)
        # But wait! I already renamed them to 'cls' and added @classmethod.
        # Vulture says they are unused because they are not used in the body.
        # So I'll rename them to '_' or prefix with '_'.
        content = re.sub(r"def (\w+)\(cls,", r"def \1(_cls,", content)

        # Fix 'info' unused in validators too if any
        content = re.sub(r"\(cls, v, info\)", r"(cls, v, _info)", content)

    if filename.endswith("mcp_server.py"):
        # Add return None to get_change_request
        if "async def get_change_request" in content:
            # Find the end of the function and add return None
            # (Simplistic approach: find the next @mcp.tool or def)
            content = content.replace(
                "sysparm_view=sysparm_view,\n            )",
                "sysparm_view=sysparm_view,\n            )\n        return None",
            )

        # Fix unused 'request'
        content = content.replace("(request: Request)", "(_request: Request)")

    return content


files = ["servicenow_api/servicenow_models.py", "servicenow_api/mcp_server.py"]
for f in files:
    if os.path.exists(f):
        print(f"Final cleanup for {f}...")
        with open(f, "r") as f_in:
            content = f_in.read()
        new_content = final_cleanup(content, f)
        if new_content != content:
            with open(f, "w") as f_out:
                f_out.write(new_content)
            print("  Done.")
        else:
            print("  No changes.")
