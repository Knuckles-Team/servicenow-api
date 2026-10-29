"""Ensure the canonical Pages workflow is the sole documentation publisher."""

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_legacy_mkdocs_publisher_is_absent() -> None:
    assert not (ROOT / ".github/workflows/docs.yml").exists()
