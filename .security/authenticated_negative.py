#!/usr/bin/env python3
# ruff: noqa: I001 -- synchronized across repositories with different import policies
"""Bounded negative authorization checks for repository workflow control planes."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path


CASES = (
    "on:\n  pull_request_target:\npermissions: {}\n",
    "on: push\npermissions: write-all\n",
    "on: push\npermissions: {}\njobs:\n  x:\n    steps:\n      - uses: owner/action@main\n",
    "on: push\npermissions: {}\njobs:\n  x:\n    steps:\n      - run: echo '${{ secrets.RUNTIME_TOKEN }}'\n",
)
ACTION_REF = re.compile(r"^\s*-?\s*uses:\s*([^\s#]+)", re.MULTILINE)


def _run_uses_secret(text: str) -> bool:
    lines = text.splitlines()
    for index, line in enumerate(lines):
        match = re.match(r"^(\s*)(?:-\s*)?run:\s*(.*)$", line)
        if match is None:
            continue
        indent = len(match.group(1))
        body = [match.group(2)]
        for following in lines[index + 1 :]:
            if following.strip() and len(following) - len(following.lstrip()) <= indent:
                break
            body.append(following)
        if "${{ secrets." in "\n".join(body):
            return True
    return False


def _violations(text: str) -> list[str]:
    findings: list[str] = []
    if re.search(r"^\s*pull_request_target\s*:", text, re.MULTILINE):
        findings.append("privileged pull-request trigger")
    if re.search(r"^permissions:\s*(?:write-all|read-all)\s*$", text, re.MULTILINE):
        findings.append("broad token permissions")
    if _run_uses_secret(text):
        findings.append("secret expression in shell")
    for reference in ACTION_REF.findall(text):
        if reference.startswith("./"):
            continue
        if reference.startswith("docker://"):
            if re.fullmatch(r"docker://[^\s]+@sha256:[0-9a-f]{64}", reference) is None:
                findings.append("mutable container action")
        elif re.fullmatch(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+(?:/[A-Za-z0-9_./-]+)?@[0-9a-f]{40}", reference) is None:
            findings.append("mutable action")
    return findings


def main() -> int:
    if len(sys.argv) != 2:
        return 2
    unauthorized_acceptances = sum(not _violations(case) for case in CASES)
    failures = 0
    workflow_root = Path(".github/workflows")
    if workflow_root.is_dir():
        for path in sorted((*workflow_root.glob("*.yml"), *workflow_root.glob("*.yaml"))):
            try:
                payload = path.read_text(encoding="utf-8")
            except (OSError, UnicodeError):
                failures += 1
                continue
            failures += len(_violations(payload))
    output = Path(sys.argv[1])
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(
        json.dumps(
            {
                "version": 1,
                "kind": "authenticated_negative",
                "passed": failures == 0 and unauthorized_acceptances == 0,
                "cases": len(CASES),
                "failures": failures,
                "unauthorized_acceptances": unauthorized_acceptances,
            },
            sort_keys=True,
        ),
        encoding="utf-8",
    )
    return 0 if failures == 0 and unauthorized_acceptances == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
