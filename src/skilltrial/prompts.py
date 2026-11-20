"""Trigger prompt sets and the tuning and held-out split.

Each skill has a YAML file with `should_trigger` prompts (gold = that skill) and `should_not_trigger` prompts
(gold = none). The split is a seeded hash per skill and per class, so it never depends on selector results."""

from __future__ import annotations

import hashlib
import json
import math
from dataclasses import dataclass
from pathlib import Path

import yaml

NONE = "none"
SPLIT_SEED = 20261120


@dataclass(frozen=True)
class Prompt:
    id: str
    text: str
    gold: str  # a skill name or "none"
    source: str  # the skill whose file holds the prompt


def load_prompts(folder: Path) -> list[Prompt]:
    out: list[Prompt] = []
    for f in sorted(Path(folder).glob("*.yaml")):
        data = yaml.safe_load(f.read_text(encoding="utf-8"))
        if not isinstance(data, dict) or not isinstance(data.get("skill"), str):
            raise ValueError(f"{f}: needs a mapping with a 'skill' name")
        skill = data["skill"]
        for i, t in enumerate(data.get("should_trigger") or []):
            out.append(Prompt(f"{skill}:pos:{i:02d}", str(t), skill, skill))
        for i, t in enumerate(data.get("should_not_trigger") or []):
            out.append(Prompt(f"{skill}:neg:{i:02d}", str(t), NONE, skill))
    return out


def _key(seed: int, pid: str) -> str:
    return hashlib.sha256(f"{seed}:{pid}".encode()).hexdigest()


def make_split(prompts: list[Prompt], seed: int = SPLIT_SEED) -> dict:
    groups: dict[tuple[str, str], list[str]] = {}
    for p in prompts:
        groups.setdefault((p.source, p.gold == NONE and "neg" or "pos"), []).append(p.id)
    tuning, heldout = [], []
    for _, ids in sorted(groups.items()):
        ids = sorted(ids, key=lambda i: _key(seed, i))
        k = math.ceil(len(ids) / 2)
        tuning += ids[:k]
        heldout += ids[k:]
    return {"seed": seed, "tuning": sorted(tuning), "heldout": sorted(heldout)}


def load_split(path: Path) -> dict:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def subset(prompts: list[Prompt], split: dict, name: str) -> list[Prompt]:
    if name == "all":
        return list(prompts)
    ids = set(split[name])
    return [p for p in prompts if p.id in ids]
