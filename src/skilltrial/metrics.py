"""Trigger metrics: micro precision, recall and F1 over skill picks, the false trigger rate on "none" prompts,
per-skill scores, a confusion table, and percentile bootstrap intervals over prompts."""

from __future__ import annotations

import random

from .prompts import NONE

BOOT_N = 2000
BOOT_SEED = 20261120


def _ratio(k: int, n: int) -> float | None:
    return k / n if n else None


def counts(golds: list[str], preds: list[str]) -> dict:
    tp = sum(p == g and g != NONE for g, p in zip(golds, preds, strict=True))
    picks = sum(p != NONE for p in preds)
    pos = sum(g != NONE for g in golds)
    none_n = len(golds) - pos
    false_trig = sum(p != NONE and g == NONE for g, p in zip(golds, preds, strict=True))
    return {"tp": tp, "picks": picks, "positives": pos, "none_prompts": none_n, "false_triggers": false_trig}


def point(golds: list[str], preds: list[str]) -> dict:
    c = counts(golds, preds)
    p, r = _ratio(c["tp"], c["picks"]), _ratio(c["tp"], c["positives"])
    f1 = 2 * p * r / (p + r) if p and r else 0.0
    return {"precision": p or 0.0, "recall": r or 0.0, "f1": f1,
            "false_trigger_rate": _ratio(c["false_triggers"], c["none_prompts"]) or 0.0, **c}


def bootstrap(golds: list[str], preds: list[str], n: int = BOOT_N, seed: int = BOOT_SEED) -> dict:
    rng = random.Random(seed)
    idx = range(len(golds))
    samples = {k: [] for k in ("precision", "recall", "f1", "false_trigger_rate")}
    for _ in range(n):
        pick = rng.choices(idx, k=len(golds))
        m = point([golds[i] for i in pick], [preds[i] for i in pick])
        for k in samples:
            samples[k].append(m[k])
    out = {}
    for k, v in samples.items():
        v.sort()
        out[k] = [v[int(0.025 * (n - 1))], v[int(round(0.975 * (n - 1)))]]
    return out


def per_skill(golds: list[str], preds: list[str], skills: list[str]) -> dict:
    out = {}
    for s in skills:
        tp = sum(g == s and p == s for g, p in zip(golds, preds, strict=True))
        fp = sum(p == s and g != s for g, p in zip(golds, preds, strict=True))
        fn = sum(g == s and p != s for g, p in zip(golds, preds, strict=True))
        pr, rc = _ratio(tp, tp + fp), _ratio(tp, tp + fn)
        f1 = 2 * pr * rc / (pr + rc) if pr and rc else 0.0
        out[s] = {"tp": tp, "fp": fp, "fn": fn, "precision": pr, "recall": rc, "f1": f1}
    return out


def confusion(golds: list[str], preds: list[str]) -> dict:
    """gold -> predicted -> count, for every pair that happened."""
    out: dict[str, dict[str, int]] = {}
    for g, p in zip(golds, preds, strict=True):
        out.setdefault(g, {})
        out[g][p] = out[g].get(p, 0) + 1
    return {g: dict(sorted(v.items())) for g, v in sorted(out.items())}


def top_confusions(conf: dict, k: int = 5) -> list[tuple[str, str, int]]:
    pairs = [(g, p, n) for g, row in conf.items() for p, n in row.items() if g != p]
    return sorted(pairs, key=lambda x: (-x[2], x[0], x[1]))[:k]
