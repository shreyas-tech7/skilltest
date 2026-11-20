"""The skills-ref comparison and the skill-scanner record exist and say what they should."""

import json

from helpers import ROOT

CMP = json.loads((ROOT / "results/skills_ref_compare.json").read_text())


def test_compare_covers_examples_and_every_flawed_variant():
    manifest = json.loads((ROOT / "examples/flawed/MANIFEST.json").read_text())
    assert CMP["n"] == 12 + len(manifest) and CMP["skills_ref_version"].startswith("agentskills")


def test_clean_examples_valid_in_both():
    for r in CMP["rows"]:
        if r["planted_rule"] is None:
            assert r["skills_ref_valid"] and r["skilltrial_valid"], r["skill"]


def test_disagreements_are_listed_and_explained():
    assert CMP["agree"] + len(CMP["disagree"]) == CMP["n"]
    doc = (ROOT / "docs/SKILLS_REF.md").read_text()
    for r in CMP["disagree"]:
        assert r["planted_rule"] in doc


def test_security_checks_record_max_severity():
    text = (ROOT / "docs/SECURITY_CHECKS.md").read_text()
    assert "Max severity" in text and "skill-scanner" in text
