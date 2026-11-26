# Handover

## Done

Every feature in `feature_list.json`. The BM25 baseline results are in `results/trigger_bm25_heldout.json` and its siblings. The planted overlaps are all found (`results/overlap.json`). The README tables come from the results files. The release check is in `docs/RELEASE_CHECK.md`.

Release commit: e4b84f9423339efe2791fae455d96863e7afcdec

It is tagged `v0.1.0-rc1`. Later commits tidy the repo for public release.

## Not done

- The live LLM record run. The proxy blocked the provider and there was no key. See `docs/HUMAN_STEPS.md`, step 7, and `BLOCKERS.md`, B3.
- The stretch `compare` command. It is written up in `docs/PROPOSALS.md`.

## Open decisions for Shreyas

- Rename the repo to `skilltrial`, or keep `skilltest` (`docs/HUMAN_STEPS.md`, step 6).
- Whether the README should show LLM numbers once they exist.
- Whether `docs/build/BUILD_PROMPT.md` stays public.
- Whether to publish the package to PyPI.

## Exact commands

```bash
git clone https://github.com/shreyas-tech7/skilltest.git && cd skilltest
git checkout claude/build-skilltest
./init.sh
.venv/bin/skilltrial trigger examples/skills --check
.venv/bin/skilltrial overlap examples/skills --check
.venv/bin/skilltrial readme --check
.venv/bin/python scripts/check_features.py
```
