# Demo

A real terminal session, written by `scripts/make_demo.sh` on 2026-11-20. Each block shows the exit code.

## Lint the clean example skills

```console
$ skilltrial lint examples/skills
12 skills checked: 0 errors, 0 warnings
(exit code 0)
```

## Lint one skill with a planted flaw

```console
$ skilltrial lint examples/flawed/SKL101
commit-message: SKL101 warning [spec guidance] SKILL.md has 543 lines, the spec suggests under 500. Fix: move detail into references/ files
1 skills checked: 0 errors, 1 warnings
(exit code 0)
```

## Token budget for one skill

```console
$ skilltrial budget examples/skills/sql-helper
Token counts are estimates: ceil(characters / 4). No tokenizer is used.

skill                   meta  body lines files  flags
sql-helper                59   176    24    39  ok
(exit code 0)
```

## Rerun the trigger eval and compare it with the committed results

```console
$ skilltrial trigger examples/skills --check
trigger results match the committed files
(exit code 0)
```

## Overlapping skills

```console
$ skilltrial overlap examples/skills
5 competing pairs (similarity >= 0.2 or >= 2 colliding prompts)
- mock-data <> unit-test-writer: similarity 0.54, 2 colliding prompts, shared terms: data, fake, fixtur, test, unit, user
    unit-test-writer:pos:03 (gold unit-test-writer): Write a fixture for a temporary config file and tests that use it
    unit-test-writer:pos:07 (gold unit-test-writer): Make a conftest.py fixture and three tests for the cache class
- changelog-writer <> release-notes: similarity 0.47, 2 colliding prompts, shared terms: ask, chang, commit, git, last, merg, note, pull
    release-notes:pos:04 (gold release-notes): Summarize what changed since the last release for the blog post
    release-notes:pos:05 (gold release-notes): Write the GitHub release description for v1.8.0
- image-resize <> thumbnail-maker: similarity 0.35, 2 colliding prompts, shared terms: imag, photo, resiz, smaller, user, version, want
    image-resize:pos:00 (gold image-resize): Resize this photo to 1200 pixels wide
    image-resize:pos:09 (gold image-resize): Remove the GPS data and resize this photo for the blog
- dockerfile-review <> image-resize: similarity 0.24, 0 colliding prompts, shared terms: imag, user
- changelog-writer <> commit-message: similarity 0.17, 2 colliding prompts, shared terms: ask, commit, git, user, writ
    commit-message:pos:05 (gold commit-message): Help me write the git commit for these two changed files
    commit-message:neg:00 (gold none): Undo my last git commit
(exit code 0)
```

## Confirm the README tables

```console
$ skilltrial readme --check
README matches the results files
(exit code 0)
```

