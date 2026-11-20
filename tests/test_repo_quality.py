"""Part 1 sections 9 to 12 (quality bar, study kit, release), checked by code."""

import json
import re
import struct
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent

REQUIRED = ["LICENSE", "CHANGELOG.md", "CONTRIBUTING.md", ".github/ISSUE_TEMPLATE/bug_report.md",
            ".github/ISSUE_TEMPLATE/feature_request.md", ".github/workflows/ci.yml", ".github/workflows/record.yml",
            "docs/GITHUB_ABOUT.md", "docs/topics.txt", "docs/social-preview.png", "docs/index.html", "docs/DEMO.md",
            "docs/PROPOSALS.md", "docs/build/BUILD_PROMPT.md", ".env.example", ".pre-commit-config.yaml",
            "action.yml", ".pre-commit-hooks.yaml"]
BANNED = ["it is important to note", "testament", "not just", "pivotal", "seamless", "delve"]


def test_required_files_exist():
    assert [f for f in REQUIRED if not (ROOT / f).is_file()] == []


def test_license_is_mit_for_shreyas():
    text = (ROOT / "LICENSE").read_text()
    assert text.startswith("MIT License") and "Copyright (c) 2026 Shreyas" in text


def test_social_preview_size():
    data = (ROOT / "docs/social-preview.png").read_bytes()
    assert data[:8] == b"\x89PNG\r\n\x1a\n"
    assert struct.unpack(">II", data[16:24]) == (1280, 640)


def test_topics_are_valid():
    topics = (ROOT / "docs/topics.txt").read_text().split()
    assert 5 <= len(topics) <= 20
    assert all(re.fullmatch(r"[a-z0-9][a-z0-9-]{0,24}", t) for t in topics)


def test_about_description_is_short():
    m = re.search(r"^> (.+)$", (ROOT / "docs/GITHUB_ABOUT.md").read_text(), flags=re.M)
    assert m and len(m.group(1)) < 350


def test_ci_workflow_follows_the_rules():
    ci = (ROOT / ".github/workflows/ci.yml").read_text()
    for need in ("workflow_dispatch", "pull_request", "cancel-in-progress: true", "paths-ignore",
                 'python-version: "3.11"', "./init.sh", "timeout-minutes: 5", "make_site.py --check",
                 "make_social_preview.py --check", "check_links.py", "uses: ./"):
        assert need in ci, need
    record = (ROOT / ".github/workflows/record.yml").read_text()
    assert "workflow_dispatch" in record and "push:" not in record and "pull_request" not in record


@pytest.mark.parametrize("script", ["make_site.py", "make_social_preview.py"])
def test_generated_pages_match_the_results(script):
    proc = subprocess.run([sys.executable, str(ROOT / "scripts" / script), "--check"], capture_output=True, text=True,
                          timeout=60)
    assert proc.returncode == 0, proc.stdout


def test_site_shows_the_heldout_numbers():
    held = json.loads((ROOT / "results/trigger_bm25_heldout.json").read_text())
    page = (ROOT / "docs/index.html").read_text()
    assert f"{held['metrics']['f1']['value']:.3f}" in page and "synthetic" in page


def test_demo_is_a_real_transcript():
    demo = (ROOT / "docs/DEMO.md").read_text()
    assert "written by `scripts/make_demo.sh`" in demo and demo.count("(exit code ") >= 5
    assert "README matches the results files" in demo


def _prose(text: str) -> str:
    text = re.sub(r"```.*?```", "", text, flags=re.S)
    text = re.sub(r"`[^`\n]*`", "", text)
    text = re.sub(r"<!--.*?-->", "", text, flags=re.S)
    return "\n".join(ln for ln in text.splitlines() if not ln.lstrip().startswith(("|", ">")))


def _docs() -> list[Path]:
    skip = {"BUILD_PROMPT.md", "DEMO.md"}
    files = [ROOT / "README.md", ROOT / "CONTRIBUTING.md", ROOT / "CHANGELOG.md", ROOT / "examples/README.md"]
    files += sorted(ROOT.glob("docs/**/*.md"))
    files += [ROOT / f for f in ("DECISIONS.md", "HANDOVER.md", "BLOCKERS.md") if (ROOT / f).exists()]
    return [f for f in files if f.name not in skip]


@pytest.mark.parametrize("path", _docs(), ids=lambda p: str(p.relative_to(ROOT)))
def test_writing_rules(path):
    """No em dashes, no dashes as punctuation, no semicolons in prose, no listed filler words."""
    prose = _prose(path.read_text(encoding="utf-8"))
    assert "—" not in prose and "–" not in prose, "em or en dash"
    assert " - " not in prose.replace("\n- ", "\n"), "dash as punctuation"
    assert ";" not in prose, "semicolon"
    low = prose.lower()
    assert [w for w in BANNED if w in low] == []


def test_link_checker_passes():
    proc = subprocess.run([sys.executable, str(ROOT / "scripts/check_links.py")], capture_output=True, text=True,
                          timeout=60)
    assert proc.returncode == 0, proc.stdout[-2000:]


def test_readme_parts_in_order():
    text = (ROOT / "README.md").read_text()
    parts = ["**Status:**", "## The problem", "```mermaid", "## Results", "## Cost per task",
             "## 10-minute run guide", "## Limits", "## Glossary", "## Related work", "## How this was built"]
    pos = [text.find(p) for p in parts]
    assert -1 not in pos, [p for p, i in zip(parts, pos, strict=True) if i == -1]
    assert pos == sorted(pos), parts
    assert "actions/workflows/ci.yml/badge.svg" in text.split("**Status:**")[0]
    assert "95%" in text.split("## Results")[1].split("## Cost per task")[0]
    assert "not done yet" in text.split("## How this was built")[1]


STUDY = ["docs/WALKTHROUGH.md", "docs/INTERVIEW_QA.md", "DECISIONS.md"]


def test_study_kit_exists():
    assert [f for f in STUDY if not (ROOT / f).is_file()] == []


def test_study_interview_qa_covers_the_points():
    qa = (ROOT / "docs/INTERVIEW_QA.md").read_text().lower()
    assert qa.count("\n## ") >= 12
    for point in ("progressive disclosure", "precision and recall", "false trigger"):
        assert point in qa, point
    assert "src/skilltrial/" in qa and "results/" in qa


def test_study_qa_cites_real_paths():
    qa = (ROOT / "docs/INTERVIEW_QA.md").read_text()
    paths = set(re.findall(r"`((?:src|results|scripts|tests|examples|docs)/[^`\s]+?)/?`", qa))
    assert paths and [p for p in paths if not (ROOT / p).exists()] == []


def test_study_walkthrough_tours_every_file():
    text = (ROOT / "docs/WALKTHROUGH.md").read_text()
    tracked = subprocess.run(["git", "-C", str(ROOT), "ls-files"], capture_output=True, text=True,
                             timeout=30).stdout.split()
    skip = ("examples/skills/", "examples/flawed/", "examples/triggers/", "tests/fixtures/", ".github/ISSUE_TEMPLATE/")
    names = {Path(f).name for f in tracked if not f.startswith(skip)}
    names |= {"WALKTHROUGH.md", "INTERVIEW_QA.md", "RELEASE_CHECK.md", "HUMAN_STEPS.md", "COWORK_PROMPT.md"}
    assert sorted(n for n in names if n not in text) == []
