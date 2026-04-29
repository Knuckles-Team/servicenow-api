import re
import os


def fix_all_validators(content):
    # 1. Normalize signatures: def func(_cls, v) -> def func(cls, v)
    # This also fixes the case where _cls was getting the first arg.
    content = re.sub(r"def\s+(\w+)\s*\(_cls,", r"def \1(cls,", content)

    # 2. Add @classmethod to all @field_validator and @model_validator
    # (Pydantic v2 usually wants them, especially if they use 'cls')

    # Match @field_validator(...) and check if next line is @classmethod
    # This is a bit complex for multi-line decorators.
    # We'll use a simpler approach: find @field_validator and @model_validator
    # and if they are not followed by @classmethod, add it.

    lines = content.split("\n")
    new_lines = []
    i = 0
    while i < len(lines):
        line = lines[i]
        new_lines.append(line)
        if ("@field_validator" in line or "@model_validator" in line) and "(" in line:
            # Skip until we find the end of the decorator
            while ")" not in lines[i]:
                i += 1
                new_lines.append(lines[i])

            # Check if next line is already @classmethod
            if i + 1 < len(lines) and "@classmethod" not in lines[i + 1]:
                new_lines.append("    @classmethod")
        i += 1

    content = "\n".join(new_lines)

    # 3. Fix the 'isinstance(v, str)' for lists in ChangeManagementModel
    # and other similar models.
    content = content.replace(
        "not isinstance(v, str)", "not isinstance(v, (str, list))"
    )

    return content


f = "servicenow_api/servicenow_models.py"
if os.path.exists(f):
    print(f"Fixing {f}...")
    with open(f, "r") as f_in:
        content = f_in.read()
    new_content = fix_all_validators(content)
    if new_content != content:
        with open(f, "w") as f_out:
            f_out.write(new_content)
        print("  Done.")
    else:
        print("  No changes.")
