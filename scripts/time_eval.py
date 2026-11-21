"""Time the lint and trigger steps on 2 cores and write results/timing.json.
Run: taskset -c 0,1 .venv/bin/python scripts/time_eval.py"""

import datetime as dt
import json
import os
import platform
import statistics
import time
from pathlib import Path

from skilltrial.evaluate import predict, skill_docs
from skilltrial.lint import lint_all
from skilltrial.parse import load_skills
from skilltrial.prompts import load_prompts
from skilltrial.selector import BM25Selector

ROOT = Path(__file__).resolve().parent.parent
REPEATS = 5


def cpu_model() -> str:
    for line in Path("/proc/cpuinfo").read_text().splitlines():
        if line.startswith("model name"):
            return line.split(":", 1)[1].strip()
    return platform.processor() or "unknown"


def timed(fn) -> float:
    runs = []
    for _ in range(REPEATS):
        t = time.perf_counter()
        fn()
        runs.append(time.perf_counter() - t)
    return statistics.median(runs)


def main() -> None:
    skills_dir = ROOT / "examples/skills"
    prompts = load_prompts(ROOT / "examples/triggers")
    best = json.loads((ROOT / "results/tuning_bm25.json").read_text())["best"]
    lint_s = timed(lambda: lint_all(load_skills(skills_dir)))
    skills = load_skills(skills_dir)
    sel = BM25Selector(skill_docs(skills), best["k1"], best["b"], best["threshold"])
    trig_s = timed(lambda: predict(sel, prompts))
    out = {
        "date": dt.date.today().isoformat(),
        "cpu": cpu_model(),
        "cores_used": len(os.sched_getaffinity(0)),
        "python": platform.python_version(),
        "repeats": REPEATS,
        "lint_12_skills_ms": round(1000 * lint_s, 2),
        "lint_per_skill_ms": round(1000 * lint_s / len(skills), 3),
        "trigger_prompts": len(prompts),
        "trigger_all_ms": round(1000 * trig_s, 2),
        "trigger_per_prompt_ms": round(1000 * trig_s / len(prompts), 4),
        "cost_usd": 0.0,
        "cost_note": "BM25 and lint run locally. No API calls, so the cost is zero.",
    }
    (ROOT / "results/timing.json").write_text(json.dumps(out, indent=1) + "\n")
    print(out)


if __name__ == "__main__":
    main()
