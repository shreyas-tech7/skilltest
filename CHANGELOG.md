# Changelog

All notable changes to this project are listed here.

## v0.1.0-rc1 (2026-11-20, release candidate, not yet tagged)

Release commit: this commit

### Added

- A SKILL.md parser that reads the frontmatter, the body and every local file the body links to.
- `skilltrial lint` with one rule per spec requirement. A spec "must" is an error, a spec "should" is a warning marked spec guidance, and anything else is a warning marked style advice. Every rule has an ID, a fix hint, a failing test, a passing test and a flawed example skill.
- `skilltrial budget`, which estimates tokens for the metadata, the body and each referenced file, and flags the spec's rough guides.
- Twelve example skills with fifteen synthetic trigger prompts each, and a tuning and held-out split committed before any selector code.
- `skilltrial trigger`, an offline BM25 selector over name and description with a "none" threshold, tuned on the tuning set only. It reports precision, recall, F1 and the false trigger rate with percentile bootstrap intervals, plus per-skill scores and a confusion table.
- `skilltrial overlap`, which flags pairs of skills whose descriptions compete and lists the prompts where they collide.
- An optional LLM selector with replay and record modes. The record run is blocked on this machine, so no LLM row is in the results.
- A GitHub Action (`action.yml`) and a pre-commit hook (`.pre-commit-hooks.yaml`).
- A README whose tables a script writes from the results files, and a test that fails when they drift.
- A results page (`docs/index.html`), a social preview image and a demo transcript, each written by a script.

### Known limits

- Token counts are estimates (characters divided by 4).
- The prompts are synthetic and written by the same author as the skills.
- The LLM selector is tested with a fake transport only.
