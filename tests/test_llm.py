"""LLM selector, offline only. A fake transport stands in for the provider. No test opens a network connection."""

import json

import pytest
from helpers import EXAMPLES, ROOT

from skilltrial.cli import NO_INPUT, OK, main
from skilltrial.evaluate import skill_docs
from skilltrial.llm import LLMSelector, MissingRecording, RecordBlocked, build_messages, parse_answer
from skilltrial.parse import load_skills

DOCS = skill_docs(load_skills(EXAMPLES))
NAMES = [n for n, _ in DOCS]


def fake_post(answer="sql-helper", status=200):
    calls = []

    def post(url, payload, key):
        calls.append(payload)
        return status, json.dumps({"choices": [{"message": {"content": answer}}]})
    post.calls = calls
    return post


def test_prompt_shows_only_names_and_descriptions():
    msg = build_messages(DOCS, "write a query")[1]["content"]
    for n, d in DOCS:
        assert f"- {n}: {d}" in msg
    assert "Use the" not in msg.split("Request:")[0].split("Skills:")[0]


@pytest.mark.parametrize("answer,want", [("sql-helper", "sql-helper"), ("  SQL-Helper.", "sql-helper"),
                                         ("none", "none"), ("I think image-resize", "image-resize"),
                                         ("something else", "none"), ("release-notes-ish", "none")])
def test_parse_answer(answer, want):
    assert parse_answer(answer, NAMES) == want


def test_replay_without_recording_raises(tmp_path):
    """Broken case: replay mode must never reach the network. A missing recording is an error."""
    sel = LLMSelector(DOCS, mode="replay", recordings=tmp_path, post=fake_post())
    with pytest.raises(MissingRecording):
        sel.select("write a query")
    assert sel.post.calls == []


def test_record_then_replay(tmp_path):
    post = fake_post("sql-helper")
    rec = LLMSelector(DOCS, mode="record", recordings=tmp_path, post=post)
    assert rec.select("write a query")[0] == "sql-helper" and len(post.calls) == 1
    files = list(tmp_path.rglob("*.json"))
    assert len(files) == 1 and "Bearer" not in files[0].read_text()
    rep = LLMSelector(DOCS, mode="replay", recordings=tmp_path, post=fake_post("wrong"))
    assert rep.select("write a query")[0] == "sql-helper" and rep.post.calls == []


def test_record_retries_429_then_blocks(tmp_path):
    waits = []
    sel = LLMSelector(DOCS, mode="record", recordings=tmp_path, post=fake_post(status=429), sleep=waits.append)
    with pytest.raises(RecordBlocked):
        sel.select("x")
    assert waits == [2.0, 4.0, 8.0, 16.0, 32.0]


def test_record_403_blocks(tmp_path):
    sel = LLMSelector(DOCS, mode="record", recordings=tmp_path, post=fake_post(status=403))
    with pytest.raises(RecordBlocked, match="403"):
        sel.select("x")


def test_cli_replay_missing_is_3(tmp_path):
    args = ["llm", str(EXAMPLES), "--prompts", str(ROOT / "examples/triggers"), "--recordings", str(tmp_path)]
    assert main(args) == NO_INPUT


def test_cli_replay_with_fake_recordings(tmp_path, monkeypatch):
    """Recordings made by a fake model that always answers 'none'. These numbers are test-only, never in the README."""
    from skilltrial import llm

    monkeypatch.setattr(llm, "http_post", lambda url, payload, key, timeout=30: (200, json.dumps(
        {"choices": [{"message": {"content": "none"}}]})))
    base = ["llm", str(EXAMPLES), "--prompts", str(ROOT / "examples/triggers"), "--recordings", str(tmp_path),
            "--results", str(tmp_path / "res"), "--split", "heldout"]
    assert main(base + ["--mode", "record"]) == OK
    assert main(base + ["--write"]) == OK
    r = json.loads((tmp_path / "res" / "trigger_llm_heldout.json").read_text())
    assert r["selector"] == "llm" and r["metrics"]["recall"]["value"] == 0.0
