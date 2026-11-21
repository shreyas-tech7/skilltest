import json

import pytest
from helpers import EXAMPLES, MANIFEST, ROOT

from skilltrial.budget import NOTE, budget, est_tokens, format_budgets
from skilltrial.parse import load_skill, load_skills

HAND = json.loads((ROOT / "tests/fixtures/hand_counts.json").read_text())


def test_estimate_is_ceil_of_chars_over_four():
    assert [est_tokens(n) for n in (0, 1, 4, 5, 8, 401)] == [0, 1, 1, 2, 2, 101]


@pytest.mark.parametrize("skill", sorted(HAND))
def test_budget_matches_hand_counts(skill):
    """Broken case: a code change to how chars are counted (for example, counting the frontmatter in the body)
    makes these differ from the wc counts in scripts/hand_count.sh."""
    got = budget(load_skill(EXAMPLES / skill))
    want = HAND[skill]
    assert {k: got[k] for k in want} == want


def test_hand_counts_cover_all_examples():
    assert sorted(HAND) == sorted(s.dir_name for s in load_skills(EXAMPLES))


def test_small_skill_counted_by_enumeration(tmp_path):
    """A tiny skill whose counts are written out by hand in this docstring:
    name 'ab' (2) + description 'Do x. Use when y.' (17) = 19 chars = 5 tokens. Body 'hi\\n' = 3 chars = 1 token."""
    d = tmp_path / "ab"
    d.mkdir()
    (d / "SKILL.md").write_text("---\nname: ab\ndescription: Do x. Use when y.\n---\nhi\n")
    b = budget(load_skill(d))
    assert (b["metadata_chars"], b["metadata_tokens"], b["body_chars"], b["body_tokens"], b["lines"]) == (19, 5, 3, 1, 5)


def test_flags_over_guidance():
    assert any("body" in f for f in budget(load_skill(ROOT / MANIFEST["SKL102"]["flawed"]))["flags"])
    assert any("metadata" in f for f in budget(load_skill(ROOT / MANIFEST["SKL103"]["flawed"]))["flags"])
    assert any("lines" in f for f in budget(load_skill(ROOT / MANIFEST["SKL101"]["flawed"]))["flags"])
    assert all(not budget(s)["flags"] for s in load_skills(EXAMPLES))


def test_report_says_counts_are_estimates():
    text = format_budgets([budget(s) for s in load_skills(EXAMPLES)])
    assert text.startswith(NOTE) and "estimate" in NOTE
