"""Optional LLM selector. It sees only the skill names and descriptions, like the baseline.

Modes:
- replay: answers come only from recorded files. A missing recording is an error. Tests use this mode.
- record: answers missing from the recordings are fetched from a free OpenAI-compatible provider
  (Groq by default) with the key from an environment variable, then saved. The key is never printed or saved.
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import time
import urllib.error
import urllib.request
from pathlib import Path

from .prompts import NONE

DEFAULT_MODEL = "llama-3.1-8b-instant"
DEFAULT_URL = "https://api.groq.com/openai/v1/chat/completions"
KEY_ENV = "GROQ_API_KEY"
SYSTEM = ("You route user requests to agent skills. You see each skill's name and description. "
          "Answer with the single skill name that should handle the request, or the word none if no skill fits. "
          "Answer with the name only.")


class MissingRecording(LookupError):
    pass


class RecordBlocked(RuntimeError):
    pass


def build_messages(docs: list[tuple[str, str]], text: str) -> list[dict]:
    listing = "\n".join(f"- {n}: {d}" for n, d in docs)
    return [{"role": "system", "content": SYSTEM},
            {"role": "user", "content": f"Skills:\n{listing}\n\nRequest: {text}\n\nSkill name or none:"}]


def recording_key(model: str, messages: list[dict]) -> str:
    return hashlib.sha256(json.dumps({"model": model, "messages": messages}, sort_keys=True).encode()).hexdigest()[:20]


def parse_answer(answer: str, names: list[str]) -> str:
    low = answer.strip().lower()
    for n in sorted(names, key=len, reverse=True):
        if re.search(rf"(?<![a-z0-9-]){re.escape(n)}(?![a-z0-9-])", low):
            return n
    return NONE


def http_post(url: str, payload: dict, key: str | None, timeout: float = 30) -> tuple[int, str]:
    headers = {"Content-Type": "application/json"}
    if key:
        headers["Authorization"] = f"Bearer {key}"
    req = urllib.request.Request(url, data=json.dumps(payload).encode(), headers=headers, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:  # noqa: S310 (fixed https URL)
            return r.status, r.read().decode()
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode(errors="replace")[:300]
    except (urllib.error.URLError, OSError) as e:
        return 0, str(e)[:300]


class LLMSelector:
    kind = "llm"

    def __init__(self, docs, model: str = DEFAULT_MODEL, mode: str = "replay", recordings: Path = Path("fixtures/llm"),
                 url: str = DEFAULT_URL, post=None, sleep=None):
        if mode not in ("replay", "record"):
            raise ValueError(mode)
        self.docs, self.model, self.mode, self.url = docs, model, mode, url
        self.dir = Path(recordings) / re.sub(r"[^a-z0-9.-]+", "-", model.lower())
        self.names = [n for n, _ in docs]
        self.post = post or (lambda url, payload, key: http_post(url, payload, key))
        self.sleep = sleep or time.sleep

    def params(self) -> dict:
        return {"model": self.model, "mode": self.mode}

    def _fetch(self, messages: list[dict]) -> str:
        key = os.environ.get(KEY_ENV)
        payload = {"model": self.model, "messages": messages, "temperature": 0, "max_tokens": 20}
        wait = 2.0
        for _ in range(5):
            status, body = self.post(self.url, payload, key)
            if status == 200:
                return json.loads(body)["choices"][0]["message"]["content"]
            if status == 429:
                self.sleep(wait)
                wait *= 2
                continue
            raise RecordBlocked(f"provider answered {status}: {body[:120]}")
        raise RecordBlocked("provider kept answering 429 after 5 tries")

    def select(self, text: str) -> tuple[str, float]:
        messages = build_messages(self.docs, text)
        path = self.dir / f"{recording_key(self.model, messages)}.json"
        if path.exists():
            answer = json.loads(path.read_text())["answer"]
        elif self.mode == "replay":
            raise MissingRecording(f"no recording for this prompt at {path}")
        else:
            answer = self._fetch(messages)
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(json.dumps({"model": self.model, "request": text, "answer": answer,
                                        "recorded": time.strftime("%Y-%m-%d")}, indent=1) + "\n")
        return parse_answer(answer, self.names), 1.0
