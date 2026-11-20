# Interview questions and answers

Questions someone might ask about skilltrial, with short answers that point at the code and the results files. Numbers live in `results/` and the README, so check them there before you quote one.

## What problem does skilltrial solve?

People write Agent Skills and ship them untested. A skill can break the spec, cost more context than it needs, or fail to load when it should. skilltrial checks all three before release: `src/skilltrial/lint.py` for the spec, `src/skilltrial/budget.py` for the cost and `src/skilltrial/evaluate.py` for triggering.

## Why do descriptions matter so much in progressive disclosure?

Progressive disclosure means the agent loads a skill in stages. At startup it sees only the name and description of every skill. It loads the body only after it decides the skill fits. So the description is the only thing the agent can use to choose. A great body behind a vague description never loads. That is why the baseline selector in `src/skilltrial/selector.py` indexes the name and description and nothing else: it sees what the agent sees.

## How do you measure trigger precision and recall?

Each example skill has prompts that should trigger it and prompts that should trigger nothing. The selector picks one skill or `none` per prompt. Precision is correct picks over all picks. Recall is correct picks over all prompts that should trigger a skill. Both are micro averages over the whole set, computed in `point` in `src/skilltrial/metrics.py`. The scored runs are in `results/trigger_bm25_heldout.json` and its siblings.

## Why does a false trigger waste context?

A false trigger is a prompt that should load no skill, where the selector picks one anyway. The agent then pulls that skill's whole body into the context window. Those tokens do nothing for the task and crowd out what does. The body can be thousands of tokens, which is why `src/skilltrial/budget.py` reports the body cost next to the metadata cost. The false trigger rate is reported on its own in every results file.

## Why a BM25 baseline and not an LLM?

It runs offline, costs nothing, is deterministic and runs in milliseconds in CI (`results/timing.json`). It gives a floor: if a keyword ranker cannot tell two descriptions apart, a model may struggle too. The LLM selector in `src/skilltrial/llm.py` exists for a second opinion, but the record run was blocked on the build machine (see `BLOCKERS.md`), so no LLM numbers are reported.

## How did you keep the evaluation honest?

Three things. The split into tuning and held-out prompts was committed before any selector code (`scripts/make_split.py`, `examples/triggers/split.json`). The grid search in `tune` in `src/skilltrial/evaluate.py` sees only tuning prompts. And a second split with a new seed was tuned and scored too (`results/seed2/`), so one lucky split cannot carry the result.

## Why bootstrap intervals?

The held-out set is small, so a point estimate alone overstates how much we know. `bootstrap` in `src/skilltrial/metrics.py` resamples prompts with replacement and reports the 95% percentile interval. A fixed seed makes the interval reproducible, and the tests rerun it.

## The held-out score is higher than the tuning score. Is that a bug?

No. With this few prompts the two scores sit within each other's intervals. The second split in `results/seed2/` was run to check, and the README shows both rows. If held-out were far above tuning on both splits, I would look for leakage.

## How is severity decided in the linter?

From the spec's own words. A "must" line becomes an error, a "should" line becomes a warning marked spec guidance, and anything that is my advice is a warning marked style advice. Each rule's `source` field in the `RULES` table in `src/skilltrial/lint.py` says which, and `docs/SPEC.md` maps every rule to its spec line.

## How do you know each lint rule works?

Every rule has a failing and a passing case in `tests/test_lint_rules.py`, and a flawed copy of a real example skill in `examples/flawed/` made by `scripts/make_flawed.py`. The clean skill is the fixed version. A test fails if a rule has no flawed example.

## How did you check the linter against the reference?

`scripts/compare_skills_ref.py` runs the reference validator from the agentskills repo on every clean example and every flawed variant. The agreement and the differences are in `results/skills_ref_compare.json`, and `docs/SKILLS_REF.md` explains each difference.

## How does the overlap detector work?

Two signals with thresholds fixed before the first run, in `src/skilltrial/overlap.py`. One is TF-IDF cosine similarity between descriptions. The other counts prompts where both skills clear the selector threshold and score close to each other. Three competing pairs were planted in the examples and named in `examples/PLANTED_OVERLAPS.json` first. The detector output is in `results/overlap.json`, including the extra pairs it flagged and why.

## Why estimate tokens instead of using a tokenizer?

Every model family tokenizes differently, the spec's guides are rough, and a tokenizer would mean a download. `ceil(chars / 4)` is close enough to flag a body that is far over the guide. The README and every budget report say the counts are estimates. `tests/test_budget.py` checks the counts against character counts made by `wc` in `scripts/hand_count.sh`.

## How do you stop the README from going stale?

Every number sits between markers that `src/skilltrial/readme.py` fills from `results/`. `skilltrial readme --check` and `tests/test_readme_sync.py` fail on any drift, and another test fails if a number appears in README prose outside a generated block.

## What would you build next?

A `compare` command that scores two versions of a skill folder on the same prompts with a paired bootstrap, so an author can see whether a description edit helped. It is written up in `docs/PROPOSALS.md`.

## What are the main limits?

The prompts are synthetic and written by the same author as the skills, so they may favor the descriptions. Token counts are estimates. The LLM selector is tested only with a fake transport. The README's Limits section lists them with the sizes from `results/`.
