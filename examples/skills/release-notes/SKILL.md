---
name: release-notes
description: Drafts release notes for a new version from merged pull requests and git commits, written for end users with highlights and upgrade steps. Use when the user asks for release notes, a release announcement, or a summary of changes since the last release.
license: MIT
---

# Release notes

Write release notes that an end user can read in one minute.

## Steps

1. Ask git for the merged pull requests since the last release tag.
2. Pick the three changes a user will notice most. These are the highlights.
3. List breaking changes with the exact upgrade step for each one.
4. Group the rest as Improvements and Fixes in plain words.
5. End with thanks to outside contributors by handle.

## Tone

- Write for users, not for the team. Say what changed for them.
- No commit hashes in the highlights.
- Keep the whole note under 300 words unless the release is large.

## Template

```
# Version 2.4.0

## Highlights
- ...

## Upgrade steps
- ...

## Improvements and fixes
- ...
```
