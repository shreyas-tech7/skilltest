"""Token budget estimates. Tokens are estimated as ceil(characters / 4). No tokenizer is used,
so every count here is an estimate."""

from __future__ import annotations

import math
from pathlib import Path

from .parse import Skill

METADATA_GUIDE = 100
BODY_GUIDE = 5000
LINES_GUIDE = 500
NOTE = "Token counts are estimates: ceil(characters / 4). No tokenizer is used."


def est_tokens(chars: int) -> int:
    return math.ceil(chars / 4)


def metadata_chars(skill: Skill) -> int:
    n = skill.field("name")
    d = skill.field("description")
    return (len(n) if isinstance(n, str) else 0) + (len(d) if isinstance(d, str) else 0)


def line_count(text: str) -> int:
    return len(text.splitlines())


def resolve_ref(skill: Skill, ref: str) -> Path | None:
    """The referenced path when it stays inside the skill folder, else None."""
    if ref.startswith(("/", "\\")) or (len(ref) > 1 and ref[1] == ":"):
        return None
    root = skill.path.resolve()
    target = (root / ref).resolve()
    return target if target == root or root in target.parents else None


def file_chars(path: Path) -> tuple[int, bool]:
    """(characters, is_text). A file that is not UTF-8 text counts its bytes."""
    data = path.read_bytes()
    try:
        return len(data.decode("utf-8")), True
    except UnicodeDecodeError:
        return len(data), False


def budget(skill: Skill) -> dict:
    meta = metadata_chars(skill)
    body = len(skill.body)
    files = []
    for ref in skill.refs:
        p = resolve_ref(skill, ref)
        if p is None or not p.is_file():
            continue
        chars, is_text = file_chars(p)
        files.append({"path": ref, "chars": chars, "tokens": est_tokens(chars), "text": is_text})
    lines = line_count(skill.text or "")
    flags = []
    if est_tokens(meta) > METADATA_GUIDE:
        flags.append(f"metadata {est_tokens(meta)} tokens is over the {METADATA_GUIDE} token guidance")
    if est_tokens(body) > BODY_GUIDE:
        flags.append(f"body {est_tokens(body)} tokens is over the {BODY_GUIDE} token guidance")
    if lines > LINES_GUIDE:
        flags.append(f"SKILL.md has {lines} lines, over the {LINES_GUIDE} line guidance")
    return {
        "skill": skill.dir_name,
        "metadata_chars": meta,
        "metadata_tokens": est_tokens(meta),
        "body_chars": body,
        "body_tokens": est_tokens(body),
        "lines": lines,
        "files": files,
        "files_tokens": sum(f["tokens"] for f in files),
        "flags": flags,
    }


def format_budgets(rows: list[dict]) -> str:
    out = [NOTE, "", f"{'skill':<22} {'meta':>5} {'body':>5} {'lines':>5} {'files':>5}  flags"]
    for r in rows:
        out.append(f"{r['skill']:<22} {r['metadata_tokens']:>5} {r['body_tokens']:>5} {r['lines']:>5} "
                   f"{r['files_tokens']:>5}  {'; '.join(r['flags']) or 'ok'}")
    return "\n".join(out)
