"""Run a selector over trigger prompts, tune the BM25 baseline on the tuning set only, and build result files."""

from __future__ import annotations

import datetime as dt
import json
from pathlib import Path

from .metrics import BOOT_N, BOOT_SEED, bootstrap, confusion, per_skill, point, top_confusions
from .parse import Skill
from .prompts import Prompt
from .selector import BM25Selector

GRID_K1 = [0.6, 0.9, 1.2, 1.5, 2.0]
GRID_B = [0.0, 0.25, 0.5, 0.75, 1.0]
GRID_T = [round(0.25 * i, 2) for i in range(0, 33)]  # 0.0 to 8.0


def skill_docs(skills: list[Skill]) -> list[tuple[str, str]]:
    out = []
    for s in skills:
        name = s.field("name") if isinstance(s.field("name"), str) else s.dir_name
        desc = s.field("description") if isinstance(s.field("description"), str) else ""
        out.append((name, desc))
    return out


def predict(selector, prompts: list[Prompt]) -> list[dict]:
    rows = []
    for p in prompts:
        pred, score = selector.select(p.text)
        rows.append({"id": p.id, "gold": p.gold, "pred": pred, "score": round(score, 4)})
    return rows


def tune(skills: list[Skill], tuning: list[Prompt]) -> dict:
    """Grid search on the tuning set. Best micro F1 wins. Ties go to the earliest grid point."""
    docs = skill_docs(skills)
    golds = [p.gold for p in tuning]
    best, grid = None, []
    for k1 in GRID_K1:
        for b in GRID_B:
            sel = BM25Selector(docs, k1, b, 0.0)
            ranked = [sel.select(p.text) for p in tuning]
            for t in GRID_T:
                preds = [n if s > t else "none" for (n, s) in ranked]
                f1 = point(golds, preds)["f1"]
                grid.append({"k1": k1, "b": b, "threshold": t, "f1": round(f1, 4)})
                if best is None or f1 > best["f1"] + 1e-12:
                    best = {"k1": k1, "b": b, "threshold": t, "f1": f1}
    return {"selector": "bm25", "tuned_on": "tuning", "skills": sorted(n for n, _ in docs), "n_prompts": len(tuning),
            "best": best,
            "grid_points": len(grid), "grid": grid}


def result(selector, prompts: list[Prompt], split: str, skills: list[str], model: str = "none (BM25, offline)",
           boot_seed: int = BOOT_SEED) -> dict:
    rows = predict(selector, prompts)
    golds, preds = [r["gold"] for r in rows], [r["pred"] for r in rows]
    m = point(golds, preds)
    ci = bootstrap(golds, preds, BOOT_N, boot_seed)
    conf = confusion(golds, preds)
    return {
        "split": split,
        "selector": selector.kind,
        "model": model,
        "params": selector.params(),
        "date": dt.date.today().isoformat(),
        "bootstrap": {"n": BOOT_N, "seed": boot_seed, "interval": "percentile 95%"},
        "n_prompts": len(rows),
        "counts": {k: m[k] for k in ("tp", "picks", "positives", "none_prompts", "false_triggers")},
        "metrics": {k: {"value": round(m[k], 4), "ci95": [round(x, 4) for x in ci[k]]}
                    for k in ("precision", "recall", "f1", "false_trigger_rate")},
        "per_skill": per_skill(golds, preds, skills),
        "confusion": conf,
        "top_confusions": top_confusions(conf, 8),
        "predictions": rows,
    }


def same_result(a: dict, b: dict) -> bool:
    """Equal apart from the run date."""
    strip = lambda d: {k: v for k, v in d.items() if k != "date"}  # noqa: E731
    return json.dumps(strip(a), sort_keys=True) == json.dumps(strip(b), sort_keys=True)


def write_json(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=1) + "\n", encoding="utf-8")
