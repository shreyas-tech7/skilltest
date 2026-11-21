"""Lint rules for Agent Skills. Spec "must" lines are errors. Spec "should" lines are warnings
labeled spec guidance. Rules the spec does not state are warnings labeled style advice."""

from __future__ import annotations

import re
from collections.abc import Callable
from dataclasses import dataclass

from .budget import BODY_GUIDE, LINES_GUIDE, METADATA_GUIDE, est_tokens, line_count, metadata_chars, resolve_ref
from .parse import SKILL_FILE, Skill, local_refs

SPEC_FIELDS = ("name", "description", "license", "compatibility", "metadata", "allowed-tools")
WHEN_CUE = re.compile(r"\bwhen\b|\bwhenever\b|\buse (it |this )?(for|if|to|on|with)\b|\bif the user\b", re.I)
TEXT_SUFFIXES = {".md", ".txt", ".markdown", ".rst"}


@dataclass(frozen=True)
class Rule:
    id: str
    severity: str  # "error" or "warning"
    source: str  # "spec", "spec guidance" or "style advice"
    summary: str
    hint: str
    check: Callable[[Skill], list[str]]


@dataclass(frozen=True)
class Finding:
    rule: str
    severity: str
    source: str
    skill: str
    message: str
    hint: str

    def line(self) -> str:
        return f"{self.skill}: {self.rule} {self.severity} [{self.source}] {self.message}. Fix: {self.hint}"


def _name(s: Skill):
    return s.field("name")


def _str_name(s: Skill) -> str | None:
    n = _name(s)
    return n if isinstance(n, str) and n else None


def _desc(s: Skill) -> str | None:
    d = s.field("description")
    return d if isinstance(d, str) and d.strip() else None


def _name_ok_char(ch: str) -> bool:
    return ch == "-" or ch.isdigit() or ch.islower()


def c_name_missing(s):
    return ["name is missing"] if _name(s) is None else []


def c_name_length(s):
    n = _name(s)
    if isinstance(n, str) and not 1 <= len(n) <= 64:
        return [f"name has {len(n)} characters, the spec allows 1 to 64"]
    return []


def c_name_charset(s):
    n = _name(s)
    if n is None:
        return []
    if not isinstance(n, str):
        return [f"name must be a string, got {type(n).__name__}"]
    bad = sorted({ch for ch in n if not _name_ok_char(ch)})
    return [f"name {n!r} has characters the spec does not allow: {''.join(bad)!r}"] if bad else []


def c_name_edge(s):
    n = _str_name(s)
    return [f"name {n!r} starts or ends with a hyphen"] if n and (n[0] == "-" or n[-1] == "-") else []


def c_name_double(s):
    n = _str_name(s)
    return [f"name {n!r} has consecutive hyphens"] if n and "--" in n else []


def c_name_dir(s):
    n = _str_name(s)
    return [f"name {n!r} does not match the directory {s.dir_name!r}"] if n and n != s.dir_name else []


def c_desc_missing(s):
    d = s.field("description")
    if d is None:
        return ["description is missing"]
    if not isinstance(d, str):
        return [f"description must be a string, got {type(d).__name__}"]
    return ["description is empty"] if not d.strip() else []


def c_desc_long(s):
    d = s.field("description")
    return [f"description has {len(d)} characters, the spec allows 1024"] if isinstance(d, str) and len(d) > 1024 else []


def c_compat(s):
    if "compatibility" not in (s.frontmatter or {}):
        return []
    c = s.field("compatibility")
    if not isinstance(c, str):
        return [f"compatibility must be a string, got {type(c).__name__}"]
    if not 1 <= len(c) <= 500:
        return [f"compatibility has {len(c)} characters, the spec allows 1 to 500"]
    return []


def c_metadata(s):
    if "metadata" not in (s.frontmatter or {}):
        return []
    m = s.field("metadata")
    if not isinstance(m, dict):
        return [f"metadata must be a map, got {type(m).__name__}"]
    bad = [str(k) for k, v in m.items() if not isinstance(k, str) or not isinstance(v, str)]
    return [f"metadata keys and values must be strings, check: {', '.join(bad)}"] if bad else []


def c_allowed_tools(s):
    if "allowed-tools" not in (s.frontmatter or {}):
        return []
    t = s.field("allowed-tools")
    return [] if isinstance(t, str) else [f"allowed-tools must be a space-separated string, got {type(t).__name__}"]


def c_lines(s):
    n = line_count(s.text or "")
    return [f"SKILL.md has {n} lines, the spec suggests under {LINES_GUIDE}"] if n > LINES_GUIDE else []


def c_body_budget(s):
    t = est_tokens(len(s.body))
    return [f"body is about {t} tokens, the spec suggests under {BODY_GUIDE}"] if t > BODY_GUIDE else []


def c_meta_budget(s):
    t = est_tokens(metadata_chars(s))
    return [f"name and description are about {t} tokens, the spec suggests about {METADATA_GUIDE}"] if t > METADATA_GUIDE else []


def c_ref_depth(s):
    out = []
    for ref in s.refs:
        p = resolve_ref(s, ref)
        if p is None or not p.is_file() or p.suffix.lower() not in TEXT_SUFFIXES:
            continue
        inner = local_refs(p.read_text(encoding="utf-8", errors="replace"))
        if inner:
            out.append(f"{ref} references {', '.join(inner)}, so the chain is more than one level deep")
    return out


def c_desc_when(s):
    d = _desc(s)
    return ["description does not say when to use the skill"] if d and not WHEN_CUE.search(d) else []


def c_ref_outside(s):
    return [f"reference {r!r} is absolute or leaves the skill folder" for r in s.refs if resolve_ref(s, r) is None]


def c_unknown_field(s):
    extra = [str(k) for k in (s.frontmatter or {}) if k not in SPEC_FIELDS]
    return [f"frontmatter field {k!r} is not in the spec" for k in extra]


def c_desc_short(s):
    d = _desc(s)
    return [f"description has only {len(d.strip())} characters"] if d and len(d.strip()) < 40 else []


def c_ref_missing(s):
    out = []
    for r in s.refs:
        p = resolve_ref(s, r)
        if p is not None and not p.exists():
            out.append(f"reference {r!r} points to a file that does not exist")
    return out


def c_body_empty(s):
    return ["body is empty"] if not s.body.strip() else []


RULES: list[Rule] = [
    Rule("SKL001", "error", "spec", "SKILL.md is missing", f"add a file named exactly {SKILL_FILE}", lambda s: []),
    Rule("SKL002", "error", "spec", "frontmatter is missing or invalid",
         "start SKILL.md with a YAML mapping between two '---' lines", lambda s: []),
    Rule("SKL003", "error", "spec", "name is missing", "add a name field that matches the folder name", c_name_missing),
    Rule("SKL004", "error", "spec", "name is too long or empty", "shorten the name to 64 characters or fewer",
         c_name_length),
    Rule("SKL005", "error", "spec", "name has characters outside a-z, 0-9 and hyphen",
         "use lowercase letters, digits and hyphens only", c_name_charset),
    Rule("SKL006", "error", "spec", "name starts or ends with a hyphen", "remove the leading or trailing hyphen",
         c_name_edge),
    Rule("SKL007", "error", "spec", "name has consecutive hyphens", "use single hyphens between words", c_name_double),
    Rule("SKL008", "error", "spec", "name does not match the directory",
         "rename the folder or the name so they match", c_name_dir),
    Rule("SKL009", "error", "spec", "description is missing or empty",
         "add a description that says what the skill does and when to use it", c_desc_missing),
    Rule("SKL010", "error", "spec", "description is over 1024 characters", "cut the description to 1024 characters",
         c_desc_long),
    Rule("SKL011", "error", "spec", "compatibility is empty or over 500 characters",
         "remove the field or keep it between 1 and 500 characters", c_compat),
    Rule("SKL012", "error", "spec", "metadata is not a map of strings",
         "make metadata a map with string keys and quoted string values", c_metadata),
    Rule("SKL013", "error", "spec", "allowed-tools is not a string",
         "write allowed-tools as one space-separated string, not a list", c_allowed_tools),
    Rule("SKL101", "warning", "spec guidance", "SKILL.md is over 500 lines",
         "move detail into references/ files", c_lines),
    Rule("SKL102", "warning", "spec guidance", "body is over the 5000 token guidance",
         "move detail into references/ files that load on demand", c_body_budget),
    Rule("SKL103", "warning", "spec guidance", "metadata is over the 100 token guidance",
         "shorten the description, it loads for every skill at startup", c_meta_budget),
    Rule("SKL104", "warning", "spec guidance", "file references go more than one level deep",
         "link every file directly from SKILL.md", c_ref_depth),
    Rule("SKL105", "warning", "spec guidance", "description does not say when to use the skill",
         "add a 'Use when ...' sentence with the words users type", c_desc_when),
    Rule("SKL106", "warning", "spec guidance", "a file reference is absolute or leaves the skill folder",
         "use a relative path from the skill root", c_ref_outside),
    Rule("SKL201", "warning", "style advice", "frontmatter has a field the spec does not define",
         "move custom fields under metadata", c_unknown_field),
    Rule("SKL202", "warning", "style advice", "description is very short",
         "say what the skill does, on what input, and when to use it", c_desc_short),
    Rule("SKL203", "warning", "style advice", "a referenced file does not exist",
         "add the file or fix the path", c_ref_missing),
    Rule("SKL204", "warning", "style advice", "body is empty", "add the instructions the agent should follow",
         c_body_empty),
]
RULES_BY_ID = {r.id: r for r in RULES}


def _finding(rule: Rule, skill: Skill, message: str) -> Finding:
    return Finding(rule.id, rule.severity, rule.source, skill.dir_name, message, rule.hint)


def lint_skill(skill: Skill) -> list[Finding]:
    if not skill.has_skill_md:
        found = [p.name for p in skill.path.iterdir() if p.name.lower() == SKILL_FILE.lower()]
        msg = f"no {SKILL_FILE} in the folder" + (f" (found {found[0]}, the name is case sensitive)" if found else "")
        return [_finding(RULES_BY_ID["SKL001"], skill, msg)]
    if skill.frontmatter is None:
        return [_finding(RULES_BY_ID["SKL002"], skill, skill.fm_error or "frontmatter is invalid")]
    out = []
    for rule in RULES[2:]:
        out += [_finding(rule, skill, m) for m in rule.check(skill)]
    return out


def lint_all(skills: list[Skill]) -> list[Finding]:
    return [f for s in skills for f in lint_skill(s)]


def summary(findings: list[Finding], n_skills: int) -> str:
    e = sum(f.severity == "error" for f in findings)
    w = len(findings) - e
    return f"{n_skills} skills checked: {e} errors, {w} warnings"
