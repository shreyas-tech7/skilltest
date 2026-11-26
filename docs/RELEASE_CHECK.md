# Release check

The checks from section 11 of the build prompt, run on 2026-11-20 on branch `claude/build-skilltest`.

| Check | Command | Result |
| --- | --- | --- |
| Code review | manual review of the CLI, the loaders and the LLM selector (the ponytail skill could not be installed) | three bugs fixed, see below |
| Secret scan | `gitleaks git -v .` | no leaks found in the full history |
| Dependencies | `pip-audit --path .venv/lib/python3.13/site-packages` | no known vulnerabilities. The one runtime dependency is PyYAML. |
| Security lint | `ruff check --select S src scripts` | five findings, all fixed or justified, see below |
| Workflows | `actionlint` | clean |
| Links | `scripts/check_links.py` | no broken relative links. External links are listed as "not checked". |
| Writing rules | `tests/test_repo_quality.py` and a manual humanizer pass | see below |
| Outside check | one subagent cloned the repo to `/tmp/outside-check` and checked every Done-means item | all seven items pass. Six findings, five fixed, see below |
| CI | `gh api` on the branch's Actions runs | green on every push since the two early failures that CI caught, see below |

## Security lint findings

- S310 in `src/skilltrial/llm.py`: record mode opens a URL. The selector and `http_post` now refuse any endpoint that does not start with `https://`, and `test_record_endpoint_must_be_https` proves it.
- S101 in `scripts/make_flawed.py`: an assert guarded a text replacement. It is now a plain `ValueError`, so it still runs under `python -O`.
- S603 twice in `scripts/compare_skills_ref.py`: the script runs the reference validator with a fixed argument list and repo paths, with no shell. Marked with the reason.
- S311 in `src/skilltrial/metrics.py`: the bootstrap uses `random.Random` with a fixed seed. That is the point, because the intervals must reproduce. Nothing here needs secure randomness.

## Code review

The ponytail and humanizer skills could not be installed in this session (see `BLOCKERS.md`, B1), so the review and the writing pass were manual.

- A prompt file with bad YAML printed a traceback and exited 1. It now exits 3 and names the file, with a test.
- A misspelled key in a prompt file dropped its prompts without a word. Unknown keys and non-list values are now errors, with tests.
- Checked that every selector sees only names and descriptions, that tuning reads only the tuning split, and that `trigger --check` and `overlap --check` match a fresh run.

## CI

CI caught two real failures that the local run missed. A flawed variant left an empty folder, which git drops, so a fresh checkout differed from the script output. The link checker failed on links the flawed examples break on purpose. Both are fixed with tests, and every run since is green.

## Writing pass

Read `README.md` and every file in `docs/` for passive voice, filler and long sentences. The repo quality test checks for em dashes, dashes used as punctuation, semicolons in prose and the banned words. One fact was wrong and is fixed: the Limits section said the detector flags one pair that was not planted, and it flags two.

## Outside check

A subagent that did not write the code cloned commit c8f3f1a to `/tmp/outside-check`, ran `./init.sh` and checked each Done-means item with its own commands. It edited nothing in the clone.

- Item 1, offline tests: pass, with the proxy variables unset and again inside a network namespace with only loopback.
- Item 2, lint rules: pass. Each of the 23 planted rules fires on its flawed copy and stays silent on the fixed skill.
- Item 3, budgets: pass. It recounted four skills with `wc` and all matched.
- Item 4, README results: pass. It recomputed precision, recall, F1 and the false trigger rate from the saved predictions and found no LLM numbers. Its caveat: only the "All" row has 120 prompts or more. The held-out row has fewer, because half the prompts are for tuning.
- Item 5, overlaps: pass. All planted pairs are flagged, and the detector never reads the planted list.
- Item 6, CI lint: pass, with the path filter bug below.
- Item 7, quality bar: pass. It triggered every exit code in the README table, and `make_demo.sh` rebuilt `docs/DEMO.md` byte for byte.

Fixed after the outside check:

- CI ignored every Markdown file, so a change to a SKILL.md or the README did not run CI. It now ignores only `docs/` and the notes files.
- Run from the repo root, `trigger` on someone else's skills used the settings tuned on the examples. Tuned settings now apply only to the exact skill set they were tuned on, and other runs say they are untuned. A test covers both cases.
- A tiny split printed an interval with no warning. `trigger` now warns when a split has too few prompts.
- `test_guard_allows_loopback` could hang if loopback was down. It now has timeouts and a daemon thread.
- The README said the lint block came from CI. It now says the block is the same command run locally, and the run guide says that the strict flawed run exits 1 on purpose.
- `DECISIONS.md` said the split was half and half. It now gives the real per-skill counts.

Logged, not changed:

- The whole build ran in one short session, so commit times are weak proof that the split came before the selector. Git order does show `split.json` committed before `selector.py`, and `scripts/make_split.py --check` shows the split depends only on prompt IDs and the seed.
