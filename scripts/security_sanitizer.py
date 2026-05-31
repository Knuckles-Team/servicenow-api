#!/usr/bin/env python3
import os
import re
import subprocess
import sys
from pathlib import Path

# Config
ALLOWED_TXT_NAMES = {"requirements.txt", "requirements-dev.txt"}
TRANSIENT_PY_PATTERNS = [
    re.compile(r"^test_.*\.py$"),
    re.compile(r"^fix_.*\.py$"),
    re.compile(r"^debug_.*\.py$"),
    re.compile(r"^scratch_.*\.py$"),
    re.compile(r"^temp_.*\.py$"),
]

SECRET_PATTERNS = [
    ("GitHub PAT", re.compile(r"ghp_[A-Za-z0-9_]{36,255}")),
    ("GitHub Fine-grained PAT", re.compile(r"github_pat_[A-Za-z0-9_]{82,255}")),
    ("GitLab PAT", re.compile(r"glpat-[A-Za-z0-9\-]{20,255}")),
    (
        "Generic Secret Assignment",
        re.compile(
            r"secret[A-Za-z0-9_]*\s*[:=]\s*['\"][A-Za-z0-9_\-\.\~\*]{16,255}['\"]",
            re.IGNORECASE,
        ),
    ),
    (
        "Generic Token Assignment",
        re.compile(
            r"token\s*[:=]\s*['\"][A-Za-z0-9_\-\.\~\*]{16,255}['\"]", re.IGNORECASE
        ),
    ),
]

EXCLUDED_DIRS = {
    ".git",
    ".venv",
    "venv",
    "node_modules",
    "build",
    "dist",
    "__pycache__",
    ".tox",
    ".specify",
}
EXCLUDED_EXTENSIONS = {
    ".png",
    ".jpg",
    ".jpeg",
    ".gif",
    ".webp",
    ".ico",
    ".pyc",
    ".db",
    ".kuzu",
    ".sqlite",
    ".sqlite3",
    ".zip",
    ".tar.gz",
    ".tgz",
    ".bz2",
    ".xz",
    ".pdf",
    ".bin",
    ".exe",
    ".dll",
    ".so",
    ".dylib",
    ".woff",
    ".woff2",
    ".eot",
    ".ttf",
    ".mp4",
    ".mp3",
    ".wav",
    ".lock",
    ".svg",
}

# Placeholder / Mock indicators
PLACEHOLDER_SUBSTRINGS = [
    "1234567890",
    "abcdef12345",
    "abc123youandme",
    "askdfalskdvjas",
    "your_",
    "YOUR_",
    "your-",
    "dummy",
    "DUMMY",
    "example",
    "EXAMPLE",
    "mock",
    "MOCK",
    "test_token",
    "test_secret",
    "glpat-askdfalskdvjas",
    "github_pat_12345",
    "glpat-abc123youandme",
    "github_pat_...",
    "glpat-*************",
    "ghp_*************",
    "github_pat_*************",
    "token_*************",
    "secret_*************",
    "glpat-abc",
    "ghp_abc",
    "github_pat_abc",
    "${env:",
]


def is_placeholder(match_str: str) -> bool:
    match_lower = match_str.lower()
    for placeholder in PLACEHOLDER_SUBSTRINGS:
        if placeholder in match_lower:
            return True

    # Check if match is mostly asterisks or single repeated char
    cleaned = match_str.replace("'", "").replace('"', "").strip()
    if not cleaned:
        return True

    # Check if there are sequences of asterisks indicating masked values
    if "*" in cleaned:
        # e.g., glpat-*************
        return True

    return False


def get_repo_files(repo_path: Path):
    try:
        result = subprocess.run(
            ["git", "ls-files", "--cached", "--others", "--exclude-standard"],
            cwd=str(repo_path),
            capture_output=True,
            text=True,
            check=True,
        )
        files = []
        for line in result.stdout.splitlines():
            if line.strip():
                # Avoid files inside excluded directories
                parts = Path(line.strip()).parts
                if not any(part in EXCLUDED_DIRS for part in parts):
                    files.append(repo_path / line.strip())
        return files
    except Exception:
        # Fallback to manual recursive scan
        files = []
        for root, dirs, walk_files in os.walk(str(repo_path)):
            dirs[:] = [
                d for d in dirs if d not in EXCLUDED_DIRS and not d.startswith(".")
            ]
            for file in walk_files:
                files.append(Path(root) / file)
        return files


def scan_repository(repo_path: Path):
    violations = []
    files_to_scan = get_repo_files(repo_path)

    for file_path in files_to_scan:
        if not file_path.is_file():
            continue

        # 1. Check root level naming constraints
        if file_path.parent == repo_path:
            # Check txt files
            if file_path.suffix == ".txt":
                if file_path.name.lower() not in ALLOWED_TXT_NAMES:
                    violations.append(
                        f"Non-standard root-level text file detected: '{file_path.name}'. Only 'requirements.txt' and 'requirements-dev.txt' are allowed."
                    )
            # Check transient py files
            elif file_path.suffix == ".py":
                for pattern in TRANSIENT_PY_PATTERNS:
                    if pattern.match(file_path.name):
                        violations.append(
                            f"Transient/temporary script detected in root: '{file_path.name}'. Please move it to a subfolder or delete it."
                        )
                        break

        # 2. Check for secrets
        if file_path.suffix.lower() in EXCLUDED_EXTENSIONS:
            continue

        if file_path.name == "security_sanitizer.py":
            continue

        try:
            content = file_path.read_text(encoding="utf-8", errors="ignore")
            lines = content.splitlines()

            for idx, line in enumerate(lines, 1):
                if any(
                    bypass in line
                    for bypass in [
                        "# sanitizer:ignore",
                        "# sanitizer-ignore",
                        "# nosec",
                    ]
                ):
                    continue

                for label, pattern in SECRET_PATTERNS:
                    for match in pattern.findall(line):
                        match_str = match[0] if isinstance(match, tuple) else match
                        if not is_placeholder(match_str):
                            rel_path = file_path.relative_to(repo_path)
                            violations.append(
                                f"Potential unmasked secret ({label}) detected in {rel_path}:{idx}\n"
                                f"  Line: {line.strip()}"
                            )
        except Exception:
            pass

    return violations


def main():
    repo_path = Path.cwd()

    print("🔒 Running Security and Garbage Sanitizer...")
    violations = scan_repository(repo_path)

    if violations:
        print("\n❌ SECURITY AND GARBAGE VALIDATION FAILED!")
        print("Please correct the following issues before committing:")
        for idx, violation in enumerate(violations, 1):
            print(f"\n[{idx}] {violation}")
        print(
            "\nNote: To bypass secret checks on specific lines, append '# sanitizer:ignore' to the end of the line."
        )
        sys.exit(1)

    print("✅ All checks passed! No root garbage or unmasked secrets detected.")
    sys.exit(0)


if __name__ == "__main__":
    main()
