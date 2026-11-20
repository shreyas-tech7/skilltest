# Tooling

Tools set up for this build VM only. Nothing from a third-party skill is committed.

| Tool | Source | Version | Why | Check result |
| --- | --- | --- | --- | --- |
| gitleaks | go install github.com/zricethezav/gitleaks/v8 | v8.30.1 | secret scan before each commit | installed |
| actionlint | go install github.com/rhysd/actionlint | v1.7.12 | lint workflow files | installed |
| pip-audit | uv tool install pip-audit | latest on 2026-11-20 | dependency check | installed |
| pre-commit | uv tool install pre-commit | latest on 2026-11-20 | runs the gitleaks hook | installed |
| skills-ref | uv tool install skills-ref | 0.1.1 (command `agentskills`) | reference validator to compare verdicts | installed |
| skill-scanner | uv tool install cisco-ai-skill-scanner | latest on 2026-11-20 | security scan of the example skills | installed |
| ruff | preinstalled | see `ruff --version` | lint and security rules | installed |
| superpowers skills | already present in the session | session copy | plans, TDD, debugging, verification, review | used |
| ponytail, caveman, find-skills, humanizer | npx skills add | none | style, token saving, docs pass | blocked: the permission system refused `npx skills add`. Rules applied by hand |
| graphify | uv tool install graphifyy | not installed | resume runs on large code | skipped: small codebase |
