"""Write the README tables from the results files, so nobody types a number. `check_readme` reports drift."""

from __future__ import annotations

import json
import re
from pathlib import Path

from .budget import NOTE, budget
from .lint import lint_all, summary
from .parse import load_skills

BLOCK = re.compile(r"(<!-- BEGIN:(\w+) -->\n)(.*?)(<!-- END:\2 -->)", re.S)


def _j(root: Path, rel: str) -> dict:
    return json.loads((root / rel).read_text(encoding="utf-8"))


def _ci(m: dict) -> str:
    return f"{m['value']:.3f} ({m['ci95'][0]:.3f} to {m['ci95'][1]:.3f})"


def block_results(root: Path) -> str:
    rows = [("Tuning", "results/trigger_bm25_tuning.json"), ("Held-out", "results/trigger_bm25_heldout.json"),
            ("All", "results/trigger_bm25_all.json"), ("Second split: tuning", "results/seed2/trigger_bm25_tuning.json"),
            ("Second split: held-out", "results/seed2/trigger_bm25_heldout.json")]
    first = _j(root, rows[1][1])
    second = _j(root, rows[4][1])
    out = [f"Run date {first['date']}. Selector: BM25 baseline, offline, no model. "
           f"Tuned on the tuning set only: k1 {first['params']['k1']}, b {first['params']['b']}, "
           f"threshold {first['params']['threshold']} (split seed {first['split_seed']}). "
           f"The second split (seed {second['split_seed']}) was tuned again on its own tuning set: "
           f"k1 {second['params']['k1']}, b {second['params']['b']}, threshold {second['params']['threshold']}. "
           f"Intervals: {first['bootstrap']['interval']} bootstrap over prompts, "
           f"{first['bootstrap']['n']} resamples, seed {first['bootstrap']['seed']}.", "",
           "| Set | Prompts (skill / none) | Precision | Recall | F1 | False trigger rate on none prompts |",
           "| --- | --- | --- | --- | --- | --- |"]
    for label, rel in rows:
        r = _j(root, rel)
        m, c = r["metrics"], r["counts"]
        out.append(f"| {label} | {r['n_prompts']} ({c['positives']} / {c['none_prompts']}) | {_ci(m['precision'])} | "
                   f"{_ci(m['recall'])} | {_ci(m['f1'])} | {_ci(m['false_trigger_rate'])} |")
    llm = sorted(root.glob("results/trigger_llm_*.json"))
    if llm:
        for p in llm:
            r = json.loads(p.read_text())
            out.append(f"| LLM {r['model']} ({r['date']}), {r['split']} | {r['n_prompts']} | {_ci(r['metrics']['precision'])} "
                       f"| {_ci(r['metrics']['recall'])} | {_ci(r['metrics']['f1'])} | "
                       f"{_ci(r['metrics']['false_trigger_rate'])} |")
    else:
        out += ["", "LLM selector: not reported. Record mode could not run on "
                f"{first['date']} (no provider key, and the proxy refused api.groq.com). See BLOCKERS.md B3."]
    return "\n".join(out) + "\n"


def block_confusion(root: Path) -> str:
    r = _j(root, "results/trigger_bm25_heldout.json")
    out = ["| Gold | Picked | Prompts |", "| --- | --- | --- |"]
    out += [f"| {g} | {p} | {n} |" for g, p, n in r["top_confusions"][:6]]
    out += ["", "| Skill | Precision | Recall | F1 |", "| --- | --- | --- | --- |"]
    for s, v in r["per_skill"].items():
        fmt = lambda x: "n/a" if x is None else f"{x:.2f}"  # noqa: E731
        out.append(f"| {s} | {fmt(v['precision'])} ({v['tp']} of {v['tp'] + v['fp']}) | "
                   f"{fmt(v['recall'])} ({v['tp']} of {v['tp'] + v['fn']}) | {v['f1']:.2f} |")
    return "\n".join(out) + "\n"


def block_overlap(root: Path) -> str:
    rep = _j(root, "results/overlap.json")
    planted = {tuple(sorted((p["a"], p["b"]))) for p in _j(root, "examples/PLANTED_OVERLAPS.json")["pairs"]}
    flagged = {tuple(p) for p in rep["flagged"]}
    t = rep["thresholds"]
    out = [f"Thresholds fixed before the first run: description similarity {t['similarity']} or more, or "
           f"{t['collide_count']} or more colliding prompts (second score at least {t['collide_ratio']} of the first). "
           f"Planted pairs found: {len(planted & flagged)} of {len(planted)}. "
           f"Other flagged pairs: {len(flagged - planted)}.", "",
           "| Pair | Planted | Similarity | Colliding prompts | Shared terms |", "| --- | --- | --- | --- | --- |"]
    for p in rep["pairs"]:
        if p["flagged"]:
            key = (p["a"], p["b"])
            out.append(f"| {p['a']} and {p['b']} | {'yes' if key in planted else 'no'} | {p['similarity']:.2f} | "
                       f"{len(p['colliding_prompts'])} | {', '.join(p['shared_terms'][:6])} |")
    return "\n".join(out) + "\n"


def lint_text(root: Path) -> str:
    skills = load_skills(root / "examples/skills")
    f = lint_all(skills)
    flawed = load_skills(root / "examples/flawed")
    ff = lint_all(flawed)
    lines = ["$ skilltrial lint examples/skills"] + [x.line() for x in f] + [summary(f, len(skills)), "",
             "$ skilltrial lint examples/flawed   (first 6 lines)"] + [x.line() for x in ff[:6]] + ["...",
             summary(ff, len(flawed))]
    return "\n".join(lines) + "\n"


def block_lint(root: Path) -> str:
    return "```text\n" + lint_text(root) + "```\n"


def block_budget(root: Path) -> str:
    rows = [budget(s) for s in load_skills(root / "examples/skills")]
    out = [NOTE + " The numbers match an independent count with `wc -m` (scripts/hand_count.sh).", "",
           "| Skill | Metadata tokens | Body tokens | Lines | Referenced file tokens | Flags |",
           "| --- | --- | --- | --- | --- | --- |"]
    out += [f"| {r['skill']} | {r['metadata_tokens']} | {r['body_tokens']} | {r['lines']} | {r['files_tokens']} | "
            f"{'; '.join(r['flags']) or 'none'} |" for r in rows]
    return "\n".join(out) + "\n"


def block_skillsref(root: Path) -> str:
    c = _j(root, "results/skills_ref_compare.json")
    clean = sum(r["planted_rule"] is None for r in c["rows"])
    return (f"skills-ref ({c['skills_ref_version']}, run {c['date']}) and skilltrial agree on {c['agree']} of {c['n']} "
            f"skills ({clean} clean examples and every flawed variant). They differ on {len(c['disagree'])}: "
            f"{', '.join(r['planted_rule'] for r in c['disagree'])}. See [docs/SKILLS_REF.md](docs/SKILLS_REF.md).\n")


def block_cost(root: Path) -> str:
    t = _j(root, "results/timing.json")
    n = len(load_skills(root / "examples/skills"))
    return (f"| Task | Time ({t['cores_used']} cores, {t['cpu']}, Python {t['python']}, {t['date']}, median of "
            f"{t['repeats']}) | Cost |\n| --- | --- | --- |\n"
            f"| Lint the {n} example skills | {t['lint_12_skills_ms']} ms "
            f"({t['lint_per_skill_ms']} ms per skill) | "
            f"${t['cost_usd']:.2f} |\n"
            f"| Select a skill for {t['trigger_prompts']} prompts | {t['trigger_all_ms']} ms "
            f"({t['trigger_per_prompt_ms']} ms per prompt) | ${t['cost_usd']:.2f} |\n\n{t['cost_note']}\n")


def block_headline(root: Path) -> str:
    h = _j(root, "results/trigger_bm25_heldout.json")
    rep = _j(root, "results/overlap.json")
    planted = {tuple(sorted((p["a"], p["b"]))) for p in _j(root, "examples/PLANTED_OVERLAPS.json")["pairs"]}
    found = len(planted & {tuple(p) for p in rep["flagged"]})
    return (f"Held-out trigger F1 {h['metrics']['f1']['value']:.3f} (95% CI {h['metrics']['f1']['ci95'][0]:.3f} to "
            f"{h['metrics']['f1']['ci95'][1]:.3f}) for the offline BM25 baseline on {h['n_prompts']} synthetic prompts. "
            f"Overlaps found among the ones planted for this test: {found} of {len(planted)}.\n")


def block_setup(root: Path) -> str:
    a = _j(root, "results/trigger_bm25_all.json")
    n_sk = len(a["per_skill"])
    pos, none = a["counts"]["positives"], a["counts"]["none_prompts"]
    return (f"There are {n_sk} example skills with {pos // n_sk} should-trigger prompts and {none // n_sk} should-not "
            f"prompts each, {a['n_prompts']} in all.\n")


def block_size(root: Path) -> str:
    a = _j(root, "results/trigger_bm25_all.json")
    h = _j(root, "results/trigger_bm25_heldout.json")
    return (f"- {a['n_prompts']} prompts is small. The held-out set has {h['n_prompts']} prompts and only "
            f"{h['counts']['none_prompts']} none prompts, so the false trigger rate has a wide interval.\n")


BLOCKS = {"setup": block_setup, "size": block_size, "headline": block_headline, "results": block_results,
          "confusion": block_confusion, "overlap": block_overlap, "lint": block_lint, "budget": block_budget,
          "skillsref": block_skillsref,
          "cost": block_cost}


def render(root: Path, text: str) -> str:
    return BLOCK.sub(lambda m: m.group(1) + BLOCKS[m.group(2)](root) + m.group(4), text)


def write_readme(root: Path) -> None:
    p = root / "README.md"
    p.write_text(render(root, p.read_text(encoding="utf-8")), encoding="utf-8")
    (root / "results/lint_examples.txt").write_text(lint_text(root), encoding="utf-8")


def check_readme(root: Path) -> list[str]:
    text = (root / "README.md").read_text(encoding="utf-8")
    found = {m.group(2): m.group(3) for m in BLOCK.finditer(text)}
    bad = [f"missing block {k}" for k in BLOCKS if k not in found]
    bad += [f"block {k} differs" for k, v in found.items() if k in BLOCKS and v != BLOCKS[k](root)]
    lint_file = root / "results/lint_examples.txt"
    if not lint_file.exists() or lint_file.read_text(encoding="utf-8") != lint_text(root):
        bad.append("results/lint_examples.txt differs")
    return bad
