# Plan

The brief in docs/build/BUILD_PROMPT.md is the spec. No question rounds. Assumptions are listed at the end and in DECISIONS.md.

## Goal

A small offline tool, `skilltrial`, that lints Agent Skills, estimates their token budgets, measures trigger precision and recall with intervals, and flags competing descriptions.

## Architecture

1. `parse.py` finds skill folders (any folder with `SKILL.md`) and splits frontmatter and body with `yaml.safe_load`.
2. `lint.py` holds one table of rules. Each rule has an ID, a severity, a source (spec, spec guidance or style) and a fix hint.
3. `budget.py` counts characters for the metadata, the body and each referenced file and divides by 4.
4. `prompts.py` loads the trigger prompt files and the committed tuning and held-out split.
5. `selector.py` ranks skills with BM25 over name and description and picks the top one when it clears a threshold.
6. `metrics.py` computes micro precision, recall and F1, bootstrap intervals and a confusion table.
7. `overlap.py` scores description similarity for every pair and lists prompts where two skills nearly tie.
8. `llm.py` is the optional LLM selector with replay and record modes.
9. `readme.py` writes the README tables from results files and checks them.
10. `cli.py` wires the steps together and sets the exit code.

## Tasks, in build order

1. Initializer, 12 example skills, flawed variants from a script.
2. Parser, then the lint rules from one table. Each rule gets a fail test on its flawed variant and a pass test on the clean skill.
3. Budget report and the independent wc counts.
4. Trigger prompts (10 should-trigger and 5 should-not per skill) and the seeded split. Commit the split before any selector code.
5. BM25 selector, tuning on the tuning set only, metrics and bootstrap.
6. Overlap detector with planted pairs listed in `examples/PLANTED_OVERLAPS.json`.
7. CLI, exit codes, `action.yml`, CI workflow, `.pre-commit-hooks.yaml`.
8. LLM selector replay with test fixtures, then one record attempt.
9. README, study kit, release check, hand-off.

## Testing

Every rule and every exit code has a test. The README sync test fails when a README number does not match its results file. The network guard fails any test that opens a non-local connection.

## Assumptions

- The repo name stays `skilltest`. The package and command are `skilltrial` because the npm name is taken.
- "Counted by hand" means an independent shell count with `wc -m`.
- Should-not prompts have gold "none".
- The overlap threshold is fixed before looking at the overlap results: cosine 0.20 on description term vectors, or at least 2 colliding prompts.
