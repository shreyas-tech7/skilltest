"""Each lint rule: it fires on its flawed variant and stays quiet on the fixed (clean) skill.
The broken case for every test is the flawed copy named in examples/flawed/MANIFEST.json."""

import pytest
from helpers import EXAMPLES, MANIFEST, ROOT

from skilltrial import lint
from skilltrial.lint import RULES, RULES_BY_ID, lint_all, lint_skill
from skilltrial.parse import load_skill, load_skills

IDS = [r.id for r in RULES]


def rule_ids(path) -> list[str]:
    return [f.rule for f in lint_skill(load_skill(ROOT / path))]


@pytest.mark.parametrize("rule", IDS)
def test_rule_fails_on_flawed_example(rule):
    assert rule in rule_ids(MANIFEST[rule]["flawed"])


@pytest.mark.parametrize("rule", IDS)
def test_rule_passes_on_fixed_example(rule):
    assert rule not in rule_ids(MANIFEST[rule]["fixed"])


@pytest.mark.parametrize("rule", [r for r in IDS if r not in ("SKL001", "SKL002")])
def test_rule_test_catches_a_disabled_rule(rule, monkeypatch):
    """Broken case: the rule's check is turned off. The flawed example must then lose the finding,
    which proves the fail test above depends on the rule."""
    off = [lint.Rule(r.id, r.severity, r.source, "", "", lambda s: []) if r.id == rule else r for r in RULES]
    monkeypatch.setattr(lint, "RULES", off)
    assert rule not in rule_ids(MANIFEST[rule]["flawed"])


def test_examples_lint_clean():
    assert lint_all(load_skills(EXAMPLES)) == []


def test_rule_ids_unique_and_labeled():
    assert len(set(IDS)) == len(IDS)
    for r in RULES:
        assert r.severity in ("error", "warning") and r.hint
        assert (r.severity == "error") == (r.source == "spec")
        assert r.source in ("spec", "spec guidance", "style advice")
        assert r.id.startswith("SKL2") == (r.source == "style advice")


def test_finding_line_has_id_severity_and_hint():
    f = lint_skill(load_skill(ROOT / MANIFEST["SKL007"]["flawed"]))[0]
    assert f.line().startswith("image--resize: SKL007 error [spec]") and "Fix: " in f.line()


@pytest.mark.parametrize("name,ok", [("a", True), ("pdf-processing", True), ("x" * 64, True), ("x" * 65, False),
                                     ("PDF-Processing", False), ("-pdf", False), ("pdf-", False),
                                     ("pdf--processing", False), ("pdf_processing", False), ("café", True),
                                     ("", False), ("v2-tool", True)])
def test_name_rules_on_spec_examples(tmp_path, name, ok):
    d = tmp_path / (name or "empty")
    d.mkdir()
    (d / "SKILL.md").write_text(f"---\nname: '{name}'\ndescription: Does a thing. Use when asked to do it.\n---\nbody\n")
    errors = [f.rule for f in lint_skill(load_skill(d)) if f.severity == "error"]
    assert (errors == []) == ok, errors


def test_rule_table_covers_ids_in_spec_doc():
    text = (ROOT / "docs/SPEC.md").read_text()
    for rid in RULES_BY_ID:
        if not rid.startswith("SKL2"):
            assert rid in text, rid
