"""Find skill folders and split SKILL.md into frontmatter and body. Uses yaml.safe_load only."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path

import yaml

SKILL_FILE = "SKILL.md"
SKIP_DIRS = {".git", ".venv", "node_modules", "__pycache__"}
FENCE = re.compile(r"^```.*?^```[^\n]*$", re.M | re.S)
MD_LINK = re.compile(r"(?<!\!)\[[^\]]*\]\(([^)\s]+)\)|!\[[^\]]*\]\(([^)\s]+)\)")
BARE_REF = re.compile(r"(?<![\w/.])((?:scripts|references|assets)/[\w./-]*[\w-])")


@dataclass
class Skill:
    path: Path
    text: str | None = None
    frontmatter: dict | None = None
    fm_text: str = ""
    fm_error: str | None = None
    body: str = ""
    refs: list[str] = field(default_factory=list)

    @property
    def dir_name(self) -> str:
        return self.path.name

    @property
    def has_skill_md(self) -> bool:
        return self.text is not None

    def field(self, key: str):
        return (self.frontmatter or {}).get(key)


def split_frontmatter(text: str) -> tuple[str | None, str]:
    """Return (frontmatter text, body). Frontmatter text is None when the file does not start with '---'."""
    text = text.lstrip("﻿")
    lines = text.split("\n")
    if not lines or lines[0].rstrip() != "---":
        return None, text
    for i in range(1, len(lines)):
        if lines[i].rstrip() == "---":
            return "\n".join(lines[1:i]), "\n".join(lines[i + 1:])
    return None, text


def local_refs(markdown: str) -> list[str]:
    """Local file references in a Markdown text: relative links plus bare scripts/, references/, assets/ paths.
    Fenced code blocks are skipped. External links and pure anchors are not references."""
    text = FENCE.sub("", markdown)
    out: list[str] = []
    for a, b in MD_LINK.findall(text):
        link = (a or b).split("#", 1)[0]
        if not link or re.match(r"^[a-z][a-z0-9+.-]*:", link, re.I):
            continue
        out.append(link)
    out += BARE_REF.findall(text)
    seen: list[str] = []
    for r in out:
        r = r.strip("`'\"")
        if r not in seen:
            seen.append(r)
    return seen


def load_skill(path: Path) -> Skill:
    path = Path(path)
    skill = Skill(path=path)
    md = path / SKILL_FILE
    if not md.is_file():
        return skill
    skill.text = md.read_text(encoding="utf-8", errors="replace")
    fm, body = split_frontmatter(skill.text)
    skill.body = body
    skill.refs = local_refs(body)
    if fm is None:
        skill.fm_error = "SKILL.md does not start with a '---' frontmatter block closed by another '---' line"
        return skill
    skill.fm_text = fm
    try:
        data = yaml.safe_load(fm)
    except yaml.YAMLError as e:
        skill.fm_error = f"frontmatter is not valid YAML: {str(e).splitlines()[0]}"
        return skill
    if not isinstance(data, dict):
        skill.fm_error = f"frontmatter must be a YAML mapping, got {type(data).__name__}"
        return skill
    skill.frontmatter = data
    return skill


def _is_candidate(d: Path) -> bool:
    return any(p.is_file() and p.name.lower() == SKILL_FILE.lower() for p in d.iterdir())


def find_skill_dirs(root: Path) -> list[Path]:
    """Skill folders under root: any folder holding SKILL.md (any case). A skill folder's own subfolders
    are not searched. A root with no skill below it counts as one skill folder only if it holds a SKILL.md."""
    root = Path(root)
    if not root.is_dir():
        return []
    if _is_candidate(root):
        return [root]
    found: list[Path] = []
    for d in sorted(p for p in root.iterdir() if p.is_dir() and p.name not in SKIP_DIRS and not p.name.startswith(".")):
        found += find_skill_dirs(d)
    return found


def load_skills(root: Path) -> list[Skill]:
    return [load_skill(d) for d in find_skill_dirs(root)]
