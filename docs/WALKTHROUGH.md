# Walkthrough

A tour of every file in the repo, in the order a reader would meet them. Read it with the code open.

## The idea in one paragraph

An agent loads skills in stages. At startup it sees only each skill's name and description. It loads the full SKILL.md body only when it decides the skill fits the task. So the description is the trigger. A vague description means the skill never loads when it should. A greedy description means it loads when it should not, and its body fills the context window for nothing. skilltrial checks the files against the spec, counts what each stage costs, and measures how well the descriptions pick the right skill.

## The package: src/skilltrial/

Read these in this order. Each module depends only on the ones above it.

### parse.py

`load_skill` reads one folder. `split_frontmatter` finds the YAML block between two `---` lines and parses it with `yaml.safe_load` only, so a SKILL.md can never run code. It returns the frontmatter, the body and a parse error if there was one. `local_refs` pulls every relative link and script path out of the body. `find_skill_dirs` walks a folder and returns every folder that holds a SKILL.md (or a near miss like `skill.md`, so the linter can say what is wrong). The `Skill` dataclass holds all of it, so no other module reads files.

### budget.py

`est_tokens` is `ceil(chars / 4)`. That is an estimate and the docs say so everywhere. `budget` counts three stages: the metadata (name plus description values, which every session pays for), the body (paid when the skill loads) and each referenced file (paid when the agent opens it). `resolve_ref` keeps a reference inside the skill folder. `format_budgets` prints the table and the note that no tokenizer is used.

### lint.py

The `RULES` table is the heart of the linter. Each `Rule` has an ID, a severity, a source, a summary, a fix hint and a check function. The source says where the rule comes from: "spec" for a "must" in the spec (an error), "spec guidance" for a "should" (a warning), "style advice" for anything else (a warning). The `c_*` functions are the checks, one per rule. They return messages, and `_finding` wraps each in a `Finding` with a line of text. `lint_skill` runs every rule on one skill. `lint_all` runs them on a folder, and `summary` counts errors and warnings. SKL001 and SKL002 are found while parsing, so their check functions return nothing.

### prompts.py

`load_prompts` reads `examples/triggers/*.yaml`. Each file holds should-trigger prompts for one skill and should-not prompts, whose gold answer is `none`. `make_split` puts half of each skill's positives and half of its negatives in the tuning set, chosen by a sha256 hash of the prompt ID and a seed. The split depends only on IDs, so editing a prompt's text never moves it. `load_split` and `subset` read the committed split.

### selector.py

The offline baseline. `tokens` lowercases, drops stopwords and runs a crude `stem`. `BM25Selector` builds an index over each skill's name and description, and nothing else, because that is all an agent sees before it loads a skill. `scores` ranks every skill for a prompt. `select` returns the top skill if its score clears the threshold, else `none`.

### metrics.py

`point` computes micro precision (correct picks over all picks), micro recall (correct picks over prompts that should trigger), F1 and the false trigger rate (none prompts where something was picked). `bootstrap` resamples prompts with replacement and takes the 2.5th and 97.5th percentiles. `per_skill` and `confusion` give the detail, and `top_confusions` lists the most common mistakes.

### evaluate.py

`skill_docs` turns skills into (name, description) pairs. `predict` runs any selector over prompts. `tune` is a grid search over k1, b and the threshold, scored on the tuning set only. `result` builds one results file with the parameters, the counts, the metrics with intervals, per-skill scores and every prediction. `same_result` compares two results while ignoring the date, which is what the `--check` flags use. `write_json` writes with a stable key order so diffs stay small.

### overlap.py

Two signals, each with a threshold fixed before the first run. `tfidf` and `cosine` measure how similar two descriptions are. `collisions` finds prompts where two skills both clear the selector threshold and the runner up scores at least most of the leader. `detect` flags a pair on either signal and records the shared terms and colliding prompts. `format_overlaps` prints them.

### llm.py

An optional second selector. `build_messages` gives the model only the names and descriptions, the same view the baseline gets. `parse_answer` finds a skill name in the reply, longest name first so `image-resize` does not match inside `image-resize-pro`. `LLMSelector` has a replay mode, which reads saved answers by `recording_key`, and a record mode, which calls `http_post` and backs off on HTTP 429. `MissingRecording` and `RecordBlocked` are the two ways it stops. Tests pass a fake `post` function, so they never touch the network.

### readme.py

Every number in the README sits between `<!-- BEGIN:x -->` and `<!-- END:x -->` markers. Each `block_*` function renders one block from the results files. `render` fills them all, `write_readme` writes the file and `results/lint_examples.txt`, and `check_readme` lists any block that differs. The test suite fails when the README drifts.

### cli.py

The `skilltrial` command. `build_parser` defines `lint`, `budget`, `trigger`, `overlap`, `llm` and `readme`. Each `cmd_*` function returns an exit code: 0 for clean, 1 for findings or a failed check, 2 for a usage error (argparse does this) and 3 for no skills or bad input (`InputError`). `_all_result_files` writes the tuning file and the three trigger results for both split seeds.

### `__init__.py`

The package docstring and `__version__`.

## Tests: tests/

`conftest.py` blocks every socket, so a test that tries the network fails loudly. `test_network_guard.py` proves the guard works. `helpers.py` holds shared paths. Then one file per module: `test_parse.py`, `test_lint_rules.py` (a failing and a passing case for every rule), `test_flawed.py` (every rule has a flawed example, and the committed variants match the script), `test_budget.py` (counts match `fixtures/hand_counts.json`, which `scripts/hand_count.sh` made with `wc`), `test_prompts.py`, `test_selector.py`, `test_metrics.py` (small hand-worked cases), `test_overlap.py` (the planted pairs are found), `test_llm.py` (replay, record with a fake transport, backoff), `test_cli.py` (every exit code), `test_action.py` (the Action and the hook files), `test_external_checks.py` (the skills-ref comparison file is consistent), `test_readme_sync.py` (no typed numbers) and `test_repo_quality.py` (the files a public repo needs, the writing rules, the release record).

## Example data: examples/

`examples/skills/` holds twelve small skills. Some pairs compete on purpose, and `PLANTED_OVERLAPS.json` names them before the detector ever ran. `examples/triggers/` holds the prompts and `split.json`. `examples/flawed/` holds one broken copy of a clean skill per rule, made by `scripts/make_flawed.py`, with `MANIFEST.json` saying which clean skill is the fix. `examples/README.md` explains all of this.

## Results: results/

`tuning_bm25.json` is the full grid. `trigger_bm25_tuning.json`, `trigger_bm25_heldout.json` and `trigger_bm25_all.json` are the scored runs, and `seed2/` repeats them on a second split. `overlap.json` is the detector output. `skills_ref_compare.json` compares the linter with the reference validator. `timing.json` is the cost run. `lint_examples.txt` is the lint output the README shows.

## Scripts: scripts/

- `make_flawed.py` writes the flawed variants. `--check` compares without writing.
- `make_split.py` writes the split. It ran once, before any selector code.
- `hand_count.sh` counts characters and lines with standard tools for the budget test.
- `compare_skills_ref.py` runs the reference validator from the agentskills repo on every example and records where it agrees.
- `time_eval.py` times lint and trigger on two cores and writes `results/timing.json`.
- `make_site.py` writes `docs/index.html`. `make_social_preview.py` draws `docs/social-preview.png` with the standard library. Both have `--check`.
- `make_demo.sh` writes `docs/DEMO.md` from a real terminal session.
- `check_links.py` checks every relative link and anchor, and skips `examples/flawed`, whose broken links are the point.
- `check_features.py` and `setpass.py` keep `feature_list.json` honest: a feature is marked passing only after its steps run clean.

## Running in other places

`action.yml` is a composite GitHub Action that installs skilltrial and runs lint and budget on a path. `.pre-commit-hooks.yaml` lets another repo use skilltrial as a pre-commit hook. `.github/workflows/ci.yml` runs `init.sh`, every `--check`, the link checker and the Action itself on the examples. `.github/workflows/record.yml` runs the LLM record mode by hand only, because it needs a key.

## Project files

- `README.md` is the front page. `CHANGELOG.md`, `CONTRIBUTING.md`, `LICENSE` and `.github/ISSUE_TEMPLATE/` are the usual public repo files.
- `PROJECT_CONTEXT.md`, `PROGRESS.md`, `HANDOVER.md`, `feature_list.json` and `CLAUDE.md` let a new session pick up the work.
- `DECISIONS.md` records each design choice and why. `BLOCKERS.md` records what failed and the fallback.
- `pyproject.toml` defines the package. `init.sh` sets up and tests everything. `.pre-commit-config.yaml` runs gitleaks. `.env.example` names the one optional key. `.gitignore` keeps the venv and caches out.
- `docs/SPEC.md` maps spec lines to rules. `docs/SKILLS_REF.md` explains where skilltrial and the reference validator differ. `docs/PLAN.md`, `docs/ENVIRONMENT.md`, `docs/TOOLING.md` and `docs/SECURITY_CHECKS.md` record the setup. `docs/GITHUB_ABOUT.md` and `docs/topics.txt` fill the About box. `docs/PROPOSALS.md` lists ideas left for later. `docs/WALKTHROUGH.md` is this file and `docs/INTERVIEW_QA.md` is the question bank. `docs/RELEASE_CHECK.md`, `docs/HUMAN_STEPS.md` and `docs/handoff/COWORK_PROMPT.md` are the release record and hand-off. `docs/build/BUILD_PROMPT.md` is the prompt the build followed.
