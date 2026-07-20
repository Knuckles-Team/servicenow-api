"""Vulture whitelist for servicenow-api.

These are Pydantic field_validator classmethod parameters that vulture
incorrectly flags as unused.
"""

cls: type  # noqa — Pydantic @field_validator first parameter convention
