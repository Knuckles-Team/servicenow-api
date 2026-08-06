"""Offline governance checks for the staged ServiceNow validation campaign.

This module deliberately never constructs an API client or sends an HTTP request.
It validates the package-side contract that must pass before an operator performs
the separate, least-privilege read-only and dry-run writeback stages.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import yaml

from servicenow_api.connectors import CANONICAL_PROVIDER, DEPLOYED_MCP_SERVICE

REQUIRED_GOVERNANCE = {
    "default_acl": "quarantine",
    "identity": "opaque-reference",
    "tenant": "required-at-materialization",
    "provenance": "required-at-materialization",
}
REQUIRED_RUNTIME_REFS = ("SERVICENOW_TENANT_REF", "SERVICENOW_ACL_REF")


def package_root() -> Path:
    return Path(__file__).resolve().parent.parent


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _load_yaml(path: Path) -> dict[str, Any]:
    return yaml.safe_load(path.read_text(encoding="utf-8")) or {}


def source_preset_contract(root: Path | None = None) -> list[str]:
    """Return violations for the signed-source-preset input contract."""
    root = root or package_root()
    presets = _load_json(root / "servicenow_api/connectors/mcp_source_presets.json")
    violations: list[str] = []
    for name in ("servicenow-incidents", "servicenow-knowledge"):
        preset = presets.get(name)
        if not isinstance(preset, dict):
            violations.append(f"missing preset: {name}")
            continue
        if preset.get("server") != CANONICAL_PROVIDER:
            violations.append(f"{name} must use {CANONICAL_PROVIDER}")
        for field in ("tool", "action", "id_field", "updated_field", "records_path"):
            if not preset.get(field):
                violations.append(f"{name} missing {field}")
    return violations


def governance_contract(root: Path | None = None) -> list[str]:
    """Require tenant/ACL/provenance materialization rather than accepting defaults."""
    root = root or package_root()
    mapping = _load_yaml(root / "servicenow_api/ontology/mappings/source.yaml")
    governance = mapping.get("governance")
    if not isinstance(governance, dict):
        return ["missing governance mapping"]
    return [
        f"governance.{key} must be {value!r}"
        for key, value in REQUIRED_GOVERNANCE.items()
        if governance.get(key) != value
    ]


def skill_contract(root: Path | None = None) -> list[str]:
    """Ensure every shipped ServiceNow skill is represented in the campaign."""
    root = root or package_root()
    skills_root = root / "servicenow_api/skills"
    return [
        f"missing SKILL.md: {path.name}"
        for path in sorted(skills_root.iterdir())
        if path.is_dir() and not (path / "SKILL.md").is_file()
    ]


def build_campaign(root: Path | None = None) -> dict[str, Any]:
    """Build a sanitized, offline-only validation plan for operator execution."""
    root = root or package_root()
    skills = sorted(
        path.name
        for path in (root / "servicenow_api/skills").iterdir()
        if path.is_dir() and (path / "SKILL.md").is_file()
    )
    violations = source_preset_contract(root) + governance_contract(root) + skill_contract(root)
    return {
        "status": "ready" if not violations else "blocked",
        "provider": CANONICAL_PROVIDER,
        "deployed_mcp_service": DEPLOYED_MCP_SERVICE,
        "offline": True,
        "violations": violations,
        "stages": [
            "offline-contract-and-catalog-validation",
            "operator-approved-least-privilege-read-only-probe",
            "bounded-source-sync-and-repeat-no-change-check",
            "dry-run-writeback-proposal-review",
            "separately-approved-single-reversible-write",
        ],
        "required_runtime_references": list(REQUIRED_RUNTIME_REFS),
        "skills": skills,
        "catalogs": {"condensed": "MCP_TOOL_MODE=intent", "verbose": "MCP_TOOL_MODE=verbose"},
    }


if __name__ == "__main__":
    print(json.dumps(build_campaign(), sort_keys=True))
