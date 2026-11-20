# Human steps

Steps that only Shreyas can do, in order. While Shreyas was away, Claude was allowed to open and merge the pull request, create the pre-release and set the About box and topics. Check each of those on GitHub before you redo it.

Release commit: this commit

The commits after the release commit only record this SHA and the hand-off notes. Tag the release commit.

## 1. Create main on GitHub, if it is missing

The GitHub repo had no `main` branch when the build started, so the build branched from `main` in the local backup remote. That commit is `1e74ec46181ffc8fb315288ea5ade3386d2d350d` (the initial README stub), and it is the first commit of `claude/build-skilltest`, so GitHub already has it. If `main` is still missing, create it from that commit before you open the pull request:

```bash
git fetch origin
git push origin 1e74ec46181ffc8fb315288ea5ade3386d2d350d:refs/heads/main
```

Then set `main` as the default branch in Settings, General.

## 2. Check that CI runs

Open the Actions tab. The `CI` workflow should finish green on `claude/build-skilltest` in under five minutes. The build session also ran every CI step locally and all passed.

## 3. Open and merge the pull request

1. Open a pull request from `claude/build-skilltest` into `main`, unless one is already merged.
2. Read the diff.
3. Merge with a merge commit, not a squash, so the release commit stays in the history of `main`.

## 4. Tag the release candidate

```bash
git fetch origin
git tag -a v0.1.0-rc1 RELEASE_SHA -m "Release candidate 1"
git push origin v0.1.0-rc1
```

Use the full SHA from the "Release commit" line above. Or create a pre-release with that tag on GitHub. The README's Action and pre-commit examples point at this tag.

## 5. Run the secret scan once more

```bash
gitleaks git -v .
```

The build ran it on the full history with no findings.

## 6. Rename the repo, or keep the name

The package and command are `skilltrial`, because `skilltest` is taken on npm by another Agent Skills testing tool (see `DECISIONS.md`). The repo is still named `skilltest`. If you rename it to `skilltrial` in Settings, General, update the clone URL, the badge, the Action example and the pre-commit example in the README, and the links in `docs/GITHUB_ABOUT.md`. GitHub redirects the old URL, but the Action reference should use the new name.

## 7. Record mode on a free provider

This is the step the build could not do. The proxy blocked the provider (`BLOCKERS.md`, B3). Without it, the README reports only the BM25 baseline.

1. Create a free key at Groq (https://console.groq.com/keys). Check the free limits first. Send only synthetic text.
2. Run locally:

   ```bash
   ./init.sh
   export GROQ_API_KEY=your-key            # never commit it
   .venv/bin/skilltrial llm examples/skills --mode record --split all
   .venv/bin/skilltrial llm examples/skills --mode replay --split heldout --write
   ```

3. Or add the secret `GROQ_API_KEY` in the repo settings and run the `Record LLM selector` workflow from the Actions tab, then download the recordings artifact into `fixtures/llm/`.
4. Commit `fixtures/llm/` and `results/trigger_llm_heldout.json`. Add an LLM row to the README results block in `src/skilltrial/readme.py`, labeled with the date and model, then run `skilltrial readme`.

## 8. Make the repo public

All history becomes public at that moment. Read `docs/build/BUILD_PROMPT.md` first (step 11).

## 9. Turn on Pages

Settings, Pages, deploy from the `main` branch and the `/docs` folder. `docs/index.html` is the results page. Put the Pages URL in the About box.

## 10. Social preview, About box and topics

- Upload `docs/social-preview.png` in Settings, General, Social preview.
- The description is in `docs/GITHUB_ABOUT.md`. The topics are in `docs/topics.txt`, one per line.

## 11. Pin the repo

Pin it on your profile, or list it in your profile README.

## 12. Publish to PyPI (optional)

The name `skilltrial` answered 404 on PyPI on 2026-11-20. If you want the package, set up trusted publishing on PyPI for this repo and add a release workflow. The build did not do this.

## 13. Add the Action to your own skill repos (optional)

In each repo that holds skills, add the step from the README's GitHub Action section, pointed at your skills folder. Start with `strict: "false"` and read the warnings before you turn strict on.

## 14. Decide whether the build prompt stays public

`docs/build/BUILD_PROMPT.md` holds the full prompt the agents followed. Keep it, trim it or remove it before the repo goes public.

## 15. Update the human checks in the README

The README lists three human checks as "not done yet". Change each one only after you do it.
