from skilltrial.prompts import NONE
from skilltrial.selector import BM25Selector, stem, tokens

SK = [("image-resize", "Resizes images and photos. Use when shrinking pictures."),
      ("sql-helper", "Writes SQL queries for databases. Use when the user needs a query.")]


def test_tokens_drop_stopwords_and_stem():
    assert tokens("Resizing the Images") == ["resiz", "imag"]
    assert stem("resize") == stem("resizing") == stem("resized") == "resiz"
    assert stem("class") == "class"


def test_selector_uses_only_names_and_descriptions():
    sel = BM25Selector(SK, threshold=0.5)
    assert sel.select("please resize this photo")[0] == "image-resize"
    assert sel.select("write a query for my database")[0] == "sql-helper"


def test_threshold_gives_none():
    sel = BM25Selector(SK, threshold=0.5)
    assert sel.select("what is the weather today")[0] == NONE


def test_scores_are_sorted_and_deterministic():
    sel = BM25Selector(SK)
    s = sel.scores("resize")
    assert s[0][0] == "image-resize" and s[0][1] > s[1][1] == 0.0
    assert BM25Selector(SK).scores("sql query") == BM25Selector(SK).scores("sql query")
