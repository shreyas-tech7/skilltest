"""skilltrial command line. Exit codes:
0 = no findings at the failing level, 1 = findings or a failed check, 2 = usage error, 3 = no skills found or bad input."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from . import __version__
from .budget import budget, format_budgets
from .lint import lint_all, summary
from .parse import load_skills

OK, FINDINGS, USAGE, NO_INPUT = 0, 1, 2, 3


class InputError(Exception):
    pass


def _skills(path: str):
    skills = load_skills(Path(path))
    if not skills:
        raise InputError(f"no skill folders found under {path} (a skill folder holds SKILL.md)")
    return skills


def cmd_lint(a) -> int:
    skills = _skills(a.path)
    findings = lint_all(skills)
    if a.json:
        print(json.dumps([f.__dict__ for f in findings], indent=2))
    else:
        for f in findings:
            print(f.line())
        print(summary(findings, len(skills)))
    fail = [f for f in findings if f.severity == "error" or a.strict]
    return FINDINGS if fail else OK


def cmd_budget(a) -> int:
    rows = [budget(s) for s in _skills(a.path)]
    print(json.dumps(rows, indent=2) if a.json else format_budgets(rows))
    return FINDINGS if a.strict and any(r["flags"] for r in rows) else OK


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="skilltrial", description="pytest for Agent Skills.")
    p.add_argument("--version", action="version", version=f"skilltrial {__version__}")
    sub = p.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("lint", help="check frontmatter and structure against the spec")
    s.add_argument("path")
    s.add_argument("--strict", action="store_true", help="fail on warnings too")
    s.add_argument("--json", action="store_true")
    s.set_defaults(func=cmd_lint)
    s = sub.add_parser("budget", help="estimate tokens (characters / 4) and flag anything over the guidance")
    s.add_argument("path")
    s.add_argument("--strict", action="store_true", help="fail when a skill is over the guidance")
    s.add_argument("--json", action="store_true")
    s.set_defaults(func=cmd_budget)
    return p


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        return args.func(args)
    except InputError as e:
        print(f"skilltrial: error: {e}", file=sys.stderr)
        return NO_INPUT


if __name__ == "__main__":
    sys.exit(main())
