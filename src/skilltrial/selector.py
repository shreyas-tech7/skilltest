"""Offline baseline selector: BM25 over each skill's name and description, and nothing else.
It picks the top skill when its score clears a threshold, else "none"."""

from __future__ import annotations

import math
import re
from collections import Counter

from .prompts import NONE

STOP = set("""a about after all also an and any are as at be been before but by can could do does
doing for from get give had has have help how i if in into is it its just like make me my need of on or our
please so some than that the their them then there these they this to up us use using want was we what when
where which while who why will with without would you your""".split())


def stem(w: str) -> str:
    if w.endswith("s") and not w.endswith("ss") and len(w) > 3:
        w = w[:-1]
    for suf in ("ing", "ed"):
        if w.endswith(suf) and len(w) - len(suf) >= 4:
            w = w[: -len(suf)]
            break
    if w.endswith("e") and len(w) > 4:
        w = w[:-1]
    return w


def tokens(text: str) -> list[str]:
    return [stem(w) for w in re.findall(r"[a-z0-9]+", text.lower()) if w not in STOP]


class BM25Selector:
    kind = "bm25"

    def __init__(self, skills: list[tuple[str, str]], k1: float = 1.2, b: float = 0.75, threshold: float = 1.0):
        self.names = [n for n, _ in skills]
        self.docs = [Counter(tokens(n.replace("-", " ")) + tokens(d)) for n, d in skills]
        self.lens = [sum(c.values()) for c in self.docs]
        self.avg = sum(self.lens) / len(self.lens) if self.lens else 0.0
        df = Counter(t for c in self.docs for t in c)
        n = len(self.docs)
        self.idf = {t: math.log((n - k + 0.5) / (k + 0.5) + 1) for t, k in df.items()}
        self.k1, self.b, self.threshold = k1, b, threshold

    def params(self) -> dict:
        return {"k1": self.k1, "b": self.b, "threshold": self.threshold}

    def scores(self, text: str) -> list[tuple[str, float]]:
        q = tokens(text)
        out = []
        for name, doc, dl in zip(self.names, self.docs, self.lens, strict=True):
            s = 0.0
            for t in q:
                tf = doc.get(t, 0)
                if tf:
                    s += self.idf[t] * tf * (self.k1 + 1) / (tf + self.k1 * (1 - self.b + self.b * dl / self.avg))
            out.append((name, s))
        return sorted(out, key=lambda x: (-x[1], x[0]))

    def select(self, text: str) -> tuple[str, float]:
        name, score = self.scores(text)[0]
        return (name, score) if score > self.threshold else (NONE, score)
