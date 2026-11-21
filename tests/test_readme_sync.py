import json
import re

from helpers import ROOT

from skilltrial.readme import BLOCK, BLOCKS, check_readme

README = (ROOT / "README.md").read_text()


def test_readme_blocks_match_results():
    assert check_readme(ROOT) == []


def test_every_block_is_in_the_readme():
    assert sorted(m.group(2) for m in BLOCK.finditer(README)) == sorted(BLOCKS)


def test_drift_is_caught(tmp_path):
    """Broken case: someone edits a number in the README by hand. check_readme must report it."""
    import shutil

    for rel in ("README.md", "results", "examples"):
        src = ROOT / rel
        (shutil.copytree if src.is_dir() else shutil.copy)(src, tmp_path / rel)
    p = tmp_path / "README.md"
    p.write_text(p.read_text().replace("Held-out trigger F1 0.", "Held-out trigger F1 9.", 1))
    assert "block headline differs" in check_readme(tmp_path)


def _prose_outside_blocks() -> str:
    text = BLOCK.sub("", README)
    text = re.sub(r"```.*?```", "", text, flags=re.S)
    text = re.sub(r"`[^`\n]*`", "", text)
    text = re.sub(r"\(http[^)]*\)|\(docs/[^)]*\)", "", text)
    lines = [re.sub(r"^\s*\d+\. ", "", ln) for ln in text.splitlines() if not ln.lstrip().startswith(("|", "#", "[!["))]
    text = "\n".join(lines)
    return re.sub(r"v\d+\.\d+\.\d+(-rc\d+)?|SKL\d{3}|\bF1\b|Copyright \(c\) \d{4}|95%", "", text)


def test_no_typed_numbers_outside_generated_blocks():
    nums = re.findall(r"\b\d+(?:\.\d+)?\b", _prose_outside_blocks())
    assert set(nums) <= {"4"}, nums  # 4: "characters divided by 4", the estimate rule


def test_headline_matches_heldout_file():
    h = json.loads((ROOT / "results/trigger_bm25_heldout.json").read_text())
    assert f"Held-out trigger F1 {h['metrics']['f1']['value']:.3f}" in README
