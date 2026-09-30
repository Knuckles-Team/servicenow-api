"""The ontology gate resolves its framework without bypassing validation."""

import importlib.util
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock

import pytest
import yaml

ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture
def gate(monkeypatch, tmp_path):
    spec = importlib.util.spec_from_file_location(
        "gate_runner", ROOT / "scripts/run_agent_utilities_gate.py"
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    framework = tmp_path / "agent-utilities"
    (framework / "scripts").mkdir(parents=True)
    (framework / "agent_utilities").mkdir()
    (framework / "pyproject.toml").write_text("[project]\nname = 'agent-utilities'\n")
    (framework / "scripts/check_connector_manifests.py").write_text("")
    monkeypatch.setenv("AGENT_UTILITIES_ROOT", str(framework))
    monkeypatch.setattr(module.shutil, "which", lambda name: "/fake/bin/uv")
    monkeypatch.setattr(
        module.sys,
        "argv",
        [
            "runner",
            "--script",
            "scripts/check_connector_manifests.py",
            "--",
            "--manifest",
            "connector_manifest.yml",
        ],
    )
    return module, framework


def test_ontology_hook_runs_locked_gate_in_calling_worktree(gate, monkeypatch):
    module, framework = gate
    run = Mock(return_value=SimpleNamespace(returncode=7))
    monkeypatch.setattr(module.subprocess, "run", run)
    assert module.main() == 7
    command = run.call_args.args[0]
    assert command == [
        "/fake/bin/uv",
        "run",
        "--project",
        str(framework),
        "--locked",
        "python",
        str(framework / "scripts/check_connector_manifests.py"),
        "--manifest",
        "connector_manifest.yml",
    ]
    assert run.call_args.kwargs["cwd"] == ROOT
    assert run.call_args.kwargs["env"]["PYTHONPATH"].split(":")[0] == str(ROOT)
    config = yaml.safe_load((ROOT / ".pre-commit-config.yaml").read_text())
    hook = next(
        hook
        for repo in config["repos"]
        for hook in repo["hooks"]
        if hook["id"] == "check-ontology-integrity"
    )
    assert "run_agent_utilities_gate.py" in hook["entry"]
    assert "check_connector_manifests.py" in hook["entry"]


def test_missing_framework_refuses_execution(gate, monkeypatch, tmp_path):
    module, _ = gate
    monkeypatch.setenv("AGENT_UTILITIES_ROOT", str(tmp_path / "missing"))
    run = Mock()
    monkeypatch.setattr(module.subprocess, "run", run)
    with pytest.raises(SystemExit) as error:
        module.main()
    assert error.value.code == 2
    run.assert_not_called()


def test_missing_validator_refuses_execution(gate, monkeypatch):
    module, framework = gate
    (framework / "scripts/check_connector_manifests.py").unlink()
    run = Mock()
    monkeypatch.setattr(module.subprocess, "run", run)
    with pytest.raises(SystemExit) as error:
        module.main()
    assert error.value.code == 2
    run.assert_not_called()
