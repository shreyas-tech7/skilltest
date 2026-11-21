"""Write docs/index.html, a static results page that opens from disk with no server.
Every number comes from the results files. Run: .venv/bin/python scripts/make_site.py
Add --check to compare without writing."""

import html
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RUNS = [("Tuning", "trigger_bm25_tuning.json"), ("Held-out", "trigger_bm25_heldout.json"),
        ("Second split, held-out", "seed2/trigger_bm25_heldout.json")]


def load(rel: str) -> dict:
    return json.loads((ROOT / rel).read_text())


def ci(m: dict) -> str:
    return f"{m['value']:.3f} <small>(CI {m['ci95'][0]:.3f} to {m['ci95'][1]:.3f})</small>"


def render() -> str:
    runs = [(name, load(f"results/{f}")) for name, f in RUNS]
    rows = [("Precision", "precision"), ("Recall", "recall"), ("F1", "f1"), ("False trigger rate", "false_trigger_rate")]
    head = "".join(f"<th>{n}<br><small>{d['n_prompts']} prompts, split seed {d['split_seed']}</small></th>"
                   for n, d in runs)
    body = "".join(f"<tr><th scope=row>{label}</th>" + "".join(f"<td>{ci(d['metrics'][k])}</td>" for _, d in runs)
                   + "</tr>" for label, k in rows)
    held = runs[1][1]
    p = held["params"]
    skills = "".join(f"<tr><th scope=row>{html.escape(s)}</th><td>{v['precision']:.2f}</td><td>{v['recall']:.2f}</td>"
                     f"<td>{v['f1']:.2f}</td></tr>" for s, v in sorted(held["per_skill"].items()))
    conf = "".join(f"<tr><td>{html.escape(g)}</td><td>{html.escape(pr)}</td><td>{n}</td></tr>"
                   for g, pr, n in held["top_confusions"])
    rep = load("results/overlap.json")
    planted = {tuple(sorted((x["a"], x["b"]))) for x in load("examples/PLANTED_OVERLAPS.json")["pairs"]}
    ov = "".join(f"<tr><td>{html.escape(x['a'])} and {html.escape(x['b'])}</td><td>{x['similarity']:.2f}</td>"
                 f"<td>{len(x['colliding_prompts'])}</td>"
                 f"<td>{'planted' if tuple(sorted((x['a'], x['b']))) in planted else 'not planted'}</td></tr>"
                 for x in rep["pairs"] if x["flagged"])
    lint = html.escape((ROOT / "results" / "lint_examples.txt").read_text())
    page = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>skilltrial results</title>
<style>
:root {{ --bg: #f6f7fa; --fg: #182030; --muted: #5a6478; --line: #d4d9e2; --accent: #1f7a62; }}
@media (prefers-color-scheme: dark) {{ :root {{ --bg: #141a28; --fg: #e8ecf4; --muted: #a0aabe;
  --line: #313a4e; --accent: #6ec4aa; }} }}
body {{ background: var(--bg); color: var(--fg); font: 16px/1.5 system-ui, sans-serif; margin: 0 auto;
  max-width: 980px; padding: 24px 16px; }}
table {{ border-collapse: collapse; width: 100%; display: block; overflow-x: auto; }}
th, td {{ border-bottom: 1px solid var(--line); padding: 6px 8px; text-align: left; vertical-align: top; }}
small, .muted {{ color: var(--muted); }}
pre {{ white-space: pre-wrap; border: 1px solid var(--line); padding: 12px; font-size: 13px; }}
a {{ color: var(--accent); }}
</style>
</head>
<body>
<h1>skilltrial</h1>
<p>skilltrial tests Agent Skills before you ship them. It lints SKILL.md against the spec, estimates the token
budget, measures whether the description makes the right skill trigger, and flags skills that compete.</p>
<p>A <b>false trigger</b> is a prompt that should load no skill, where the selector picked one anyway. That skill's
body then fills the context window for nothing.</p>
<h2>Trigger results</h2>
<table><thead><tr><th>Metric</th>{head}</tr></thead><tbody>{body}</tbody></table>
<p class="muted">Selector: {html.escape(held['model'])}. Parameters tuned on the tuning set only: k1 {p['k1']},
b {p['b']}, threshold {p['threshold']}. Run date {held['date']}. CI is a 95% percentile bootstrap interval with
{held['bootstrap']['n']} resamples. The prompts are synthetic and written for this repo.</p>
<h2>Per skill, held-out</h2>
<table><thead><tr><th>Skill</th><th>Precision</th><th>Recall</th><th>F1</th></tr></thead><tbody>{skills}</tbody>
</table>
<h2>Most common mistakes, held-out</h2>
<table><thead><tr><th>Should pick</th><th>Picked</th><th>Count</th></tr></thead><tbody>{conf}</tbody></table>
<h2>Overlapping skills</h2>
<table><thead><tr><th>Pair</th><th>Description similarity</th><th>Colliding prompts</th><th>Planted</th></tr>
</thead><tbody>{ov}</tbody></table>
<h2>Lint output on the examples</h2>
<pre>{lint}</pre>
<p class="muted">Written by scripts/make_site.py from the results folder. See the <a href="../README.md">README</a>.</p>
</body>
</html>
"""
    return page


def main(argv: list[str]) -> int:
    out = ROOT / "docs" / "index.html"
    page = render()
    if "--check" in argv:
        ok = out.exists() and out.read_text(encoding="utf-8") == page
        print("docs/index.html matches the results files" if ok else "docs/index.html is stale: run scripts/make_site.py")
        return 0 if ok else 1
    out.write_text(page, encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
