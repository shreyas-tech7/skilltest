"""Overlap detector: flags pairs of skills whose descriptions compete.

Two signals, with thresholds fixed before the first run:
1. Description similarity: cosine of TF-IDF vectors over name and description tokens. Flag at SIM_FLAG or more.
2. Colliding prompts: prompts where both skills clear the selector threshold and the second score is at least
   COLLIDE_RATIO of the first. Flag at COLLIDE_FLAG or more colliding prompts.
"""

from __future__ import annotations

import math
from collections import Counter
from itertools import combinations

from .prompts import Prompt
from .selector import BM25Selector, tokens

SIM_FLAG = 0.20
COLLIDE_RATIO = 0.8
COLLIDE_FLAG = 2


def tfidf(docs: list[tuple[str, str]]) -> list[dict[str, float]]:
    bags = [Counter(tokens(n.replace("-", " ")) + tokens(d)) for n, d in docs]
    n = len(bags)
    df = Counter(t for b in bags for t in b)
    vecs = []
    for b in bags:
        v = {t: c * (math.log((1 + n) / (1 + df[t])) + 1) for t, c in b.items()}
        norm = math.sqrt(sum(x * x for x in v.values())) or 1.0
        vecs.append({t: x / norm for t, x in v.items()})
    return vecs


def cosine(a: dict[str, float], b: dict[str, float]) -> float:
    return sum(x * b.get(t, 0.0) for t, x in a.items())


def collisions(selector: BM25Selector, prompts: list[Prompt]) -> dict[tuple[str, str], list[dict]]:
    out: dict[tuple[str, str], list[dict]] = {}
    for p in prompts:
        (n1, s1), (n2, s2) = selector.scores(p.text)[:2]
        if s2 > selector.threshold and s2 >= COLLIDE_RATIO * s1:
            key = tuple(sorted((n1, n2)))
            out.setdefault(key, []).append({"id": p.id, "text": p.text, "gold": p.gold,
                                            "scores": {n1: round(s1, 3), n2: round(s2, 3)}})
    return out


def detect(docs: list[tuple[str, str]], selector: BM25Selector, prompts: list[Prompt]) -> dict:
    vecs = tfidf(docs)
    names = [n for n, _ in docs]
    coll = collisions(selector, prompts)
    pairs = []
    for i, j in combinations(range(len(docs)), 2):
        key = tuple(sorted((names[i], names[j])))
        sim = cosine(vecs[i], vecs[j])
        shared = sorted(set(vecs[i]) & set(vecs[j]))
        hits = coll.get(key, [])
        flagged = sim >= SIM_FLAG or len(hits) >= COLLIDE_FLAG
        pairs.append({"a": key[0], "b": key[1], "similarity": round(sim, 4), "shared_terms": shared,
                      "colliding_prompts": hits, "flagged": flagged})
    pairs.sort(key=lambda p: (-p["flagged"], -p["similarity"], p["a"], p["b"]))
    return {"thresholds": {"similarity": SIM_FLAG, "collide_ratio": COLLIDE_RATIO, "collide_count": COLLIDE_FLAG},
            "selector_params": selector.params(), "n_prompts": len(prompts),
            "flagged": [[p["a"], p["b"]] for p in pairs if p["flagged"]], "pairs": pairs}


def format_overlaps(rep: dict, top: int = 5) -> str:
    lines = [f"{len(rep['flagged'])} competing pairs (similarity >= {rep['thresholds']['similarity']} "
             f"or >= {rep['thresholds']['collide_count']} colliding prompts)"]
    for p in rep["pairs"]:
        if not p["flagged"]:
            continue
        lines.append(f"- {p['a']} <> {p['b']}: similarity {p['similarity']:.2f}, "
                     f"{len(p['colliding_prompts'])} colliding prompts, shared terms: {', '.join(p['shared_terms'][:8])}")
        for c in p["colliding_prompts"][:top]:
            lines.append(f"    {c['id']} (gold {c['gold']}): {c['text']}")
    return "\n".join(lines)
