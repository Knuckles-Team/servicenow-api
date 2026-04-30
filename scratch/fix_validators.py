import re
import os


def fix_validators(content):
    # Fix @field_validator and @model_validator to use @classmethod and (cls, ...)
    # Pattern: @field_validator\(...\)\n    def (\w+)\(_cls,
    content = re.sub(
        r"@field_validator\((.*?)\)\n\s+def\s+(\w+)\(_cls,",
        r"@field_validator(\1)\n    @classmethod\n    def \2(cls,",
        content,
    )

    # Fix @model_validator(mode="before")
    content = re.sub(
        r'@model_validator\(mode="before"\)\n\s+@classmethod\n\s+def\s+(\w+)\(_cls,',
        r'@model_validator(mode="before")\n    @classmethod\n    def \1(cls,',
        content,
    )

    return content


f = "servicenow_api/servicenow_models.py"
if os.path.exists(f):
    print(f"Fixing {f}...")
    with open(f, "r") as f_in:
        content = f_in.read()
    new_content = fix_validators(content)
    if new_content != content:
        with open(f, "w") as f_out:
            f_out.write(new_content)
        print("  Done.")
    else:
        print("  No changes.")
