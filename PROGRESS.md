# Progress

## Done

- All 42 features in `feature_list.json` pass their steps: parser, 23 lint rules with flawed variants, budget, prompts and split, BM25 selector, metrics, overlap detector, CLI exit codes, Action, pre-commit hook, LLM selector (replay, offline), skills-ref comparison, README sync, quality bar, study kit, release check and hand-off.
- CI on GitHub is green on the branch.

## Next

- Nothing in the build. The human steps are in `docs/HUMAN_STEPS.md`.
- Stretch, only if asked: the `compare` command in `docs/PROPOSALS.md`.

## Open blockers

- B1 third-party skills refused (review and writing pass done by hand).
- B2 agentskills.io 403 (second spec source used).
- B3 LLM record mode blocked at the proxy, no key. The README reports only the BM25 baseline.

## Last init.sh

- 2026-11-20: all tests passed, ruff clean.
