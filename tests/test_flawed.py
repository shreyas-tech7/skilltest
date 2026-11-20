import subprocess
import sys

from helpers import MANIFEST, ROOT

from skilltrial.lint import RULES


def test_every_rule_has_a_flawed_variant():
    assert sorted(MANIFEST) == sorted(r.id for r in RULES)


def test_every_fixed_counterpart_exists():
    for v in MANIFEST.values():
        assert (ROOT / v["flawed"]).is_dir() and (ROOT / v["fixed"] / "SKILL.md").is_file()


def test_committed_variants_match_the_script():
    proc = subprocess.run([sys.executable, str(ROOT / "scripts/make_flawed.py"), "--check"], capture_output=True,
                          text=True, timeout=60)
    assert proc.returncode == 0, proc.stdout
