import pytest

from skilltrial.metrics import bootstrap, confusion, per_skill, point, top_confusions
from skilltrial.prompts import NONE

G = ["a", "a", "b", "b", NONE, NONE]
P = ["a", "b", "b", NONE, "a", NONE]


def test_point_by_hand():
    """By hand: tp=2 (a, b). picks=4 (a, b, b, a). positives=4. precision 2/4, recall 2/4, F1 0.5.
    One of two none prompts triggered a skill, so the false trigger rate is 0.5."""
    m = point(G, P)
    assert (m["tp"], m["picks"], m["positives"]) == (2, 4, 4)
    assert m["precision"] == m["recall"] == m["f1"] == 0.5 and m["false_trigger_rate"] == 0.5


def test_perfect_and_empty():
    assert point(["a", NONE], ["a", NONE])["f1"] == 1.0
    m = point(["a"], [NONE])
    assert m["precision"] == 0.0 and m["recall"] == 0.0 and m["f1"] == 0.0


def test_per_skill_and_confusion():
    ps = per_skill(G, P, ["a", "b"])
    assert ps["a"] == {"tp": 1, "fp": 1, "fn": 1, "precision": 0.5, "recall": 0.5, "f1": 0.5}
    conf = confusion(G, P)
    assert conf["a"] == {"a": 1, "b": 1} and conf[NONE] == {NONE: 1, "a": 1}
    assert top_confusions(conf)[0] == ("a", "b", 1)


def test_bootstrap_is_seeded_and_brackets_the_point():
    golds = G * 20
    preds = P * 20
    b1, b2 = bootstrap(golds, preds, n=500, seed=1), bootstrap(golds, preds, n=500, seed=1)
    assert b1 == b2
    for k in ("precision", "recall", "f1"):
        lo, hi = b1[k]
        assert lo <= 0.5 <= hi and hi - lo < 0.4


def test_bootstrap_zero_width_when_perfect():
    assert bootstrap(["a", "b"], ["a", "b"], n=50)["f1"] == [1.0, 1.0]


@pytest.mark.parametrize("bad", [["a"], ["a", "b", "c"]])
def test_length_mismatch_raises(bad):
    with pytest.raises(ValueError):
        point(["a", "b"], bad)
