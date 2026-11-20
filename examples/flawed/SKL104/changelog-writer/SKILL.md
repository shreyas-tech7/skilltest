---
name: changelog-writer
description: Writes CHANGELOG.md entries from git commits and merged pull requests, grouped as Added, Changed and Fixed. Use when the user asks to update the changelog, summarize changes since the last release, or prepare release notes from commits.
license: MIT
---

# Changelog writer

Write entries for `CHANGELOG.md` in the Keep a Changelog style.

## Steps

1. Find the last release tag with `git describe --tags --abbrev=0`.
2. List commits since that tag with `git log <tag>..HEAD --oneline`.
3. Sort each change into Added, Changed, Deprecated, Removed, Fixed or Security.
4. Write one line per change in the past tense. Link the pull request number when there is one.
5. Put the new entries under an `## [Unreleased]` heading at the top of the file.

## Rules

- Skip merge commits, version bumps and pure formatting changes.
- Keep each line under 100 characters.
- Never invent a change that is not in the commit list.

See [the format guide](references/FORMAT.md) for the exact headings and an example.

## Example

Input commits:

```
a1b2c3d Add --json flag to export
d4e5f6a Fix crash when config file is empty
```

Output:

```
## [Unreleased]
### Added
- `--json` flag for the export command.
### Fixed
- Crash when the config file is empty.
```
