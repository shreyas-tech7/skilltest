# Contributing

Thanks for looking. This is a small tool, so the rules are short.

## Setup

```bash
./init.sh
source .venv/bin/activate
```

`init.sh` makes the virtual environment, installs the package, runs ruff and runs every test offline. Run it before and after every change.

## Rules

- Every lint rule needs a failing example and a passing example in `tests/test_lint_rules.py`, plus a flawed variant made by `scripts/make_flawed.py`. The coverage tests fail until both exist.
- A rule that comes from a "must" in the spec is an error. A rule from a "should" is a warning marked spec guidance. Anything else is a warning marked style advice. Say which line of the spec a new rule comes from in `docs/SPEC.md`.
- Never edit the tuning and held-out split in `examples/triggers/split.json` to make a number look better. Never tune the selector on held-out prompts.
- Never type a number into the README. Run `skilltrial trigger examples/skills --write`, `skilltrial overlap examples/skills --write`, then `skilltrial readme`.
- Tests never touch the network. `tests/conftest.py` blocks sockets, and the LLM selector tests use a fake transport.
- Run `gitleaks git --pre-commit --redact --staged --verbose` before you commit. The pre-commit config runs it too.

## Adding a lint rule

1. Add the rule to the `RULES` table in `src/skilltrial/lint.py` with an ID, a severity, a source and a fix hint.
2. Add a failing and a passing case to `tests/test_lint_rules.py`.
3. Add a flawed variant to `scripts/make_flawed.py` and run it.
4. Run `./init.sh`, then regenerate the README.

## Adding an example skill

1. Add the folder under `examples/skills/` and give it 10 should-trigger and 5 should-not prompts in `examples/triggers/`.
2. New prompts need a place in the split. Run `scripts/make_split.py` and log the change in `DECISIONS.md`, because it changes every number.
