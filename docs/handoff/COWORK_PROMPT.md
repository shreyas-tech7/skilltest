# Prompt for Claude Cowork

Paste everything below the line into Claude Cowork.

---

You are helping Shreyas finish the browser steps for his private GitHub repo `shreyas-tech7/skilltest`. Read `docs/HUMAN_STEPS.md` in the repo first.

Do only steps that are free and can be undone:

1. Open the Actions tab and report whether the latest `CI` run on `main` and on `claude/build-skilltest` is green. If one is red, copy the failing step name and its last lines.
2. In Settings, General, check that `main` exists and is the default branch. If not, tell Shreyas. Do not change it yourself unless he says so.
3. Check the About box. The description should match `docs/GITHUB_ABOUT.md` and the topics should match `docs/topics.txt`. Fill in what is missing.
4. Upload `docs/social-preview.png` as the social preview in Settings, General.
5. Check the Releases page for a `v0.1.0-rc1` pre-release on the release commit named in `docs/HUMAN_STEPS.md`. Report what you see.

Do not:

- make the repo public,
- rename the repo,
- publish a package,
- enter any key, token or secret,
- sign in for Shreyas or create an account,
- pay for anything or change a billing setting,
- delete a branch, a tag or a release.

When you finish, write a short report of what you checked and changed. Then end with this prompt for the next Claude Code session, filled in:

> Context: skilltrial (repo skilltest) tests Agent Skills offline. It lints SKILL.md against the spec, estimates token budgets, measures trigger precision and recall with a BM25 baseline and bootstrap intervals, and flags overlapping skills.
> Complete: every Done-means item for the BM25 baseline. The LLM selector is built and tested offline, but no record run has happened.
> Open: the LLM record run needs a free Groq key (see `docs/HUMAN_STEPS.md`, step 7), the repo name decision (step 6), plus anything this Cowork report found.
> Read docs/build/BUILD_PROMPT.md and follow it. Resume from PROGRESS.md on branch claude/build-skilltest. Do not ask questions. Do not stop until every Done-means item is true or blocked with a fallback.
