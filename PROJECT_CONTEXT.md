# PROJECT_CONTEXT

## What it is

skilltrial (repo `skilltest`) is pytest for Agent Skills. It lints `SKILL.md` files against the Agent Skills spec, estimates token budgets, and measures how well each skill description triggers on the right prompts. Everything runs offline.

## Status

See PROGRESS.md and feature_list.json. Branch `claude/build-skilltest`.

## Stack

Python 3.11+, PyYAML (`yaml.safe_load` only), pytest, ruff. Standard library for BM25, bootstrap and PNG drawing. No numpy.

## Commands

- `./init.sh`: venv, install, ruff, all tests offline
- `skilltrial lint <dir>`: spec lint with rule IDs
- `skilltrial budget <dir>`: token estimates (chars / 4)
- `skilltrial trigger <dir> --prompts examples/triggers`: BM25 selector, precision, recall, F1 with intervals
- `skilltrial overlap <dir>`: competing descriptions and colliding prompts
- `skilltrial readme [--check]`: write or check README tables from results/

## Layout

- `src/skilltrial/`: package (parse, lint, budget, prompts, selector, metrics, overlap, llm, readme, cli)
- `examples/skills/`: 12 invented example skills (MIT)
- `examples/flawed/`: one flawed variant per lint rule, made by `scripts/make_flawed.py`
- `examples/triggers/`: trigger prompts per skill and `split.json`
- `results/`: result files. README numbers come only from here
- `tests/`: pytest, with a network guard in `conftest.py`
- `docs/`: spec source, plan, study kit, hand-off

## Rules

- Never type numbers into the README. Run `skilltrial readme`.
- Never change the held-out split, the prompts or the hand counts to make code pass.
- Spec "must" lines are errors. "Should" lines are warnings (spec guidance). The rest is style advice.
- No network in tests. Keys only from env vars. Never commit a key.
- Writing: active voice, no em dashes, no semicolons in prose.

## Skills that fit

superpowers test-driven-development, systematic-debugging, verification-before-completion, requesting-code-review.

## Do not read

`.venv/`, `logs/`, `docs/build/BUILD_PROMPT.md` (only on resume, for the brief), `examples/flawed/` (generated).
