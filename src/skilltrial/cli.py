"""skilltrial command line. Exit codes:
0 = no findings at the failing level, 1 = findings or a failed check, 2 = usage error, 3 = no skills found or bad input."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from . import __version__
from .budget import budget, format_budgets
from .evaluate import result, same_result, skill_docs, tune, write_json
from .lint import lint_all, summary
from .overlap import detect, format_overlaps
from .parse import load_skills
from .prompts import load_prompts, load_split, make_split, subset
from .selector import BM25Selector

SPLITS = ("tuning", "heldout", "all")
SEED2 = 20261121
MIN_PROMPTS = 30

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


def _prompts(a):
    folder = Path(a.prompts) if a.prompts else Path(a.path).parent / "triggers"
    if not folder.is_dir():
        raise InputError(f"no prompt folder at {folder} (pass --prompts)")
    try:
        prompts = load_prompts(folder)
    except (ValueError, OSError) as e:
        raise InputError(str(e)) from e
    if not prompts:
        raise InputError(f"no prompts in {folder}")
    split_file = folder / "split.json"
    split = load_split(split_file) if split_file.exists() else make_split(prompts)
    return prompts, split


def _selector(docs, params_file: Path | None):
    """Use tuned settings only for the exact skill set they were tuned on. Other skills get the defaults."""
    if params_file and params_file.exists():
        tuned = json.loads(params_file.read_text())
        if tuned.get("skills") == sorted(n for n, _ in docs):
            b = tuned["best"]
            return BM25Selector(docs, b["k1"], b["b"], b["threshold"])
        print(f"skilltrial: {params_file} was tuned on other skills, so this run is untuned "
              "(BM25 defaults). Run with --write to tune on your own prompts.", file=sys.stderr)
    return BM25Selector(docs)


def _trigger_files(skills, prompts, split, seed_tag: str = "") -> dict[str, dict]:
    """Tune on the tuning set only, then score every split with the tuned selector."""
    docs = skill_docs(skills)
    names = [n for n, _ in docs]
    tuned = tune(skills, subset(prompts, split, "tuning"))
    b = tuned["best"]
    sel = BM25Selector(docs, b["k1"], b["b"], b["threshold"])
    files = {f"{seed_tag}tuning_bm25.json": {**tuned, "split_seed": split["seed"]}}
    for s in SPLITS:
        files[f"{seed_tag}trigger_bm25_{s}.json"] = {**result(sel, subset(prompts, split, s), s, names),
                                                     "split_seed": split["seed"]}
    return files


def _all_result_files(skills, prompts, split) -> dict[str, dict]:
    files = _trigger_files(skills, prompts, split)
    files.update(_trigger_files(skills, prompts, make_split(prompts, SEED2), "seed2/"))
    return files


def _compare(results: Path, files: dict[str, dict]) -> list[str]:
    bad = []
    for name, data in files.items():
        p = results / name
        if not p.exists() or not same_result(json.loads(p.read_text()), data):
            bad.append(name)
    return bad


def cmd_trigger(a) -> int:
    skills = _skills(a.path)
    prompts, split = _prompts(a)
    results = Path(a.results)
    if a.write or a.check:
        files = _all_result_files(skills, prompts, split)
        if a.check:
            bad = _compare(results, files)
            print("trigger results match the committed files" if not bad else f"results differ: {', '.join(bad)}")
            return FINDINGS if bad else OK
        for name, data in files.items():
            write_json(results / name, data)
        print(f"wrote {len(files)} result files to {results}")
        return OK
    docs = skill_docs(skills)
    sel = _selector(docs, results / "tuning_bm25.json" if not a.untuned else None)
    r = result(sel, subset(prompts, split, a.split), a.split, [n for n, _ in docs])
    if r["n_prompts"] < MIN_PROMPTS:
        print(f"skilltrial: only {r['n_prompts']} prompts in split {a.split}, too few prompts for a useful interval. "
              "Add prompts or use --split all.", file=sys.stderr)
    if a.json:
        print(json.dumps(r, indent=1))
    else:
        print(f"split {a.split}: {r['n_prompts']} prompts, selector bm25 {sel.params()}")
        for k, v in r["metrics"].items():
            print(f"  {k:<19} {v['value']:.3f}  95% CI {v['ci95'][0]:.3f} to {v['ci95'][1]:.3f}")
        for g, p, n in r["top_confusions"][:5]:
            print(f"  confused: gold {g} -> picked {p} ({n})")
    return FINDINGS if a.min_f1 is not None and r["metrics"]["f1"]["value"] < a.min_f1 else OK


def cmd_overlap(a) -> int:
    skills = _skills(a.path)
    prompts, _ = _prompts(a)
    docs = skill_docs(skills)
    rep = detect(docs, _selector(docs, Path(a.results) / "tuning_bm25.json"), prompts)
    out = Path(a.results) / "overlap.json"
    if a.check:
        ok = out.exists() and same_result(json.loads(out.read_text()), rep)
        print("overlap results match the committed file" if ok else "overlap results differ")
        return OK if ok else FINDINGS
    if a.write:
        write_json(out, rep)
    print(json.dumps(rep, indent=1) if a.json else format_overlaps(rep))
    return FINDINGS if a.fail_on_overlap and rep["flagged"] else OK


def cmd_readme(a) -> int:
    from .readme import check_readme, write_readme

    root = Path(a.root)
    if a.check:
        bad = check_readme(root)
        print("README matches the results files" if not bad else "README is out of date: " + "; ".join(bad))
        return FINDINGS if bad else OK
    write_readme(root)
    print("README tables written from results/")
    return OK


def cmd_llm(a) -> int:
    from .llm import LLMSelector, MissingRecording, RecordBlocked

    skills = _skills(a.path)
    prompts, split = _prompts(a)
    docs = skill_docs(skills)
    sel = LLMSelector(docs, a.model, a.mode, Path(a.recordings))
    try:
        r = result(sel, subset(prompts, split, a.split), a.split, [n for n, _ in docs], model=a.model)
    except (MissingRecording, RecordBlocked) as e:
        print(f"skilltrial: llm selector could not run: {e}", file=sys.stderr)
        return NO_INPUT
    if a.write:
        write_json(Path(a.results) / f"trigger_llm_{a.split}.json", r)
    for k, v in r["metrics"].items():
        print(f"  {k:<19} {v['value']:.3f}  95% CI {v['ci95'][0]:.3f} to {v['ci95'][1]:.3f}")
    return OK


def _add_prompt_args(s) -> None:
    s.add_argument("--prompts", help="folder of trigger prompt YAML files (default: <path>/../triggers)")
    s.add_argument("--results", default="results", help="results folder (default: results)")


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
    s = sub.add_parser("trigger", help="run the BM25 selector over the trigger prompts and report P, R, F1")
    s.add_argument("path")
    _add_prompt_args(s)
    s.add_argument("--split", choices=SPLITS, default="heldout")
    s.add_argument("--min-f1", type=float, help="exit 1 when F1 is below this")
    s.add_argument("--untuned", action="store_true", help="use default BM25 settings, not results/tuning_bm25.json")
    s.add_argument("--write", action="store_true", help="tune on the tuning set and write every result file")
    s.add_argument("--check", action="store_true", help="exit 1 when a fresh run differs from the result files")
    s.add_argument("--json", action="store_true")
    s.set_defaults(func=cmd_trigger)
    s = sub.add_parser("overlap", help="flag skills whose descriptions compete and list colliding prompts")
    s.add_argument("path")
    _add_prompt_args(s)
    s.add_argument("--fail-on-overlap", action="store_true", help="exit 1 when any pair is flagged")
    s.add_argument("--write", action="store_true", help="write results/overlap.json")
    s.add_argument("--check", action="store_true", help="exit 1 when a fresh run differs from results/overlap.json")
    s.add_argument("--json", action="store_true")
    s.set_defaults(func=cmd_overlap)
    s = sub.add_parser("llm", help="optional LLM selector, replay or record mode")
    s.add_argument("path")
    _add_prompt_args(s)
    s.add_argument("--mode", choices=("replay", "record"), default="replay")
    s.add_argument("--model", default="llama-3.1-8b-instant")
    s.add_argument("--recordings", default="fixtures/llm")
    s.add_argument("--split", choices=SPLITS, default="all")
    s.add_argument("--write", action="store_true", help="write results/trigger_llm_<split>.json")
    s.set_defaults(func=cmd_llm)
    s = sub.add_parser("readme", help="write the README tables from the results files")
    s.add_argument("--root", default=".")
    s.add_argument("--check", action="store_true", help="exit 1 when the README differs from the results")
    s.set_defaults(func=cmd_readme)
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
