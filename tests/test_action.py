import re

import yaml
from helpers import ROOT


def _load(path):
    return yaml.safe_load((ROOT / path).read_text())


def test_action_is_composite_with_documented_inputs():
    a = _load("action.yml")
    assert a["runs"]["using"] == "composite"
    assert set(a["inputs"]) == {"path", "strict", "budget"}
    runs = " ".join(s["run"] for s in a["runs"]["steps"])
    assert "skilltrial lint" in runs and "skilltrial budget" in runs


def test_action_passes_inputs_through_env_only():
    """Broken case: `${{ inputs.path }}` inside a run script allows script injection. Inputs must go through env."""
    for step in _load("action.yml")["runs"]["steps"]:
        assert "${{" not in step["run"], step["name"]


def test_pre_commit_hook():
    hooks = _load(".pre-commit-hooks.yaml")
    assert hooks[0]["id"] == "skilltrial-lint" and hooks[0]["entry"] == "skilltrial lint"
    assert re.search(hooks[0]["files"], "skills/x/SKILL.md") and not re.search(hooks[0]["files"], "README.md")


def test_ci_lints_examples_and_uses_the_action():
    ci = (ROOT / ".github/workflows/ci.yml").read_text()
    assert "skilltrial lint examples/skills" in ci and "uses: ./" in ci
    for check in ("trigger examples/skills --check", "overlap examples/skills --check", "readme --check"):
        assert check in ci


def test_record_workflow_is_manual_only():
    rec = (ROOT / ".github/workflows/record.yml").read_text()
    assert "workflow_dispatch" in rec and "push:" not in rec and "pull_request" not in rec
