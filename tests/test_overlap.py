import json

from helpers import EXAMPLES, ROOT

from skilltrial.evaluate import skill_docs
from skilltrial.overlap import SIM_FLAG, cosine, detect, format_overlaps, tfidf
from skilltrial.parse import load_skills
from skilltrial.prompts import Prompt, load_prompts
from skilltrial.selector import BM25Selector

PLANTED = {tuple(sorted((p["a"], p["b"]))) for p in json.loads((ROOT / "examples/PLANTED_OVERLAPS.json").read_text())["pairs"]}


def _report():
    docs = skill_docs(load_skills(EXAMPLES))
    best = json.loads((ROOT / "results/tuning_bm25.json").read_text())["best"]
    sel = BM25Selector(docs, best["k1"], best["b"], best["threshold"])
    return detect(docs, sel, load_prompts(ROOT / "examples/triggers"))


def test_finds_every_planted_overlap():
    """Broken case: a detector with thresholds too strict (or no collision signal) misses these pairs."""
    flagged = {tuple(p) for p in _report()["flagged"]}
    assert PLANTED <= flagged, PLANTED - flagged


def test_planted_pairs_rank_first():
    top = {(p["a"], p["b"]) for p in _report()["pairs"][: len(PLANTED)]}
    assert top == PLANTED


def test_planted_pairs_list_colliding_prompts():
    pairs = {(p["a"], p["b"]): p for p in _report()["pairs"]}
    for key in PLANTED:
        assert pairs[key]["colliding_prompts"], key


def test_distinct_skills_not_flagged():
    docs = [("sql-helper", "Writes SQL queries. Use when the user needs a query."),
            ("image-resize", "Resizes photos. Use when shrinking pictures.")]
    rep = detect(docs, BM25Selector(docs, threshold=0.5), [Prompt("x:pos:00", "write a query", "sql-helper", "x")])
    assert rep["flagged"] == []


def test_identical_descriptions_flagged():
    docs = [("a-tool", "Resizes photos for the web."), ("b-tool", "Resizes photos for the web.")]
    v = tfidf(docs)
    assert cosine(v[0], v[1]) > SIM_FLAG
    rep = detect(docs, BM25Selector(docs), [])
    assert rep["flagged"] == [["a-tool", "b-tool"]] and "a-tool <> b-tool" in format_overlaps(rep)
