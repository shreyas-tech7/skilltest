import subprocess
import sys

import pytest
from helpers import EXAMPLES, ROOT

from skilltrial.parse import load_skills
from skilltrial.prompts import NONE, load_prompts, load_split, make_split, subset

TRIG = ROOT / "examples" / "triggers"
PROMPTS = load_prompts(TRIG)
SPLIT = load_split(TRIG / "split.json")


def test_twelve_skills_ten_positive_each():
    names = sorted(s.dir_name for s in load_skills(EXAMPLES))
    for n in names:
        assert sum(p.gold == n for p in PROMPTS) == 10, n
        assert sum(p.source == n and p.gold == NONE for p in PROMPTS) == 5, n
    assert len(PROMPTS) == 180 and len({p.text for p in PROMPTS}) == 180


def test_split_is_a_partition():
    t, h = set(SPLIT["tuning"]), set(SPLIT["heldout"])
    assert not t & h and t | h == {p.id for p in PROMPTS}
    assert len(subset(PROMPTS, SPLIT, "heldout")) == len(h) and len(subset(PROMPTS, SPLIT, "all")) == 180


def test_split_balances_every_skill():
    held = subset(PROMPTS, SPLIT, "heldout")
    for n in {p.source for p in PROMPTS}:
        assert sum(p.gold == n for p in held) == 5
        assert sum(p.source == n and p.gold == NONE for p in held) == 2


def test_split_depends_only_on_ids_and_seed():
    assert make_split(PROMPTS, SPLIT["seed"]) == SPLIT
    assert make_split(PROMPTS, SPLIT["seed"] + 1) != SPLIT


def test_committed_split_matches_the_script():
    proc = subprocess.run([sys.executable, str(ROOT / "scripts/make_split.py"), "--check"], capture_output=True,
                          text=True, timeout=60)
    assert proc.returncode == 0, proc.stdout


@pytest.mark.parametrize("text, why", [
    ("skill: [unclosed\n", "not valid YAML"),
    ("skill: csv-cleanup\nshould_triger:\n- Clean this CSV\n", "unknown key"),
    ("skill: csv-cleanup\nshould_trigger: Clean this CSV\n", "must be a list"),
])
def test_bad_prompt_file_names_the_file(tmp_path, text, why):
    """Broken cases: a typo in a key used to drop prompts silently, and bad YAML crashed with a traceback."""
    (tmp_path / "bad.yaml").write_text(text)
    with pytest.raises(ValueError, match=why) as e:
        load_prompts(tmp_path)
    assert "bad.yaml" in str(e.value)
