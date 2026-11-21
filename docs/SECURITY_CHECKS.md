# Security checks

## skill-scanner on the example skills

- Tool: Cisco skill-scanner 2.3.2 (`uv tool install cisco-ai-skill-scanner`), static analyzers only. No LLM, VirusTotal or other online analyzer was turned on.
- Command: `skill-scanner scan-all examples/skills --format json`
- Date: 2026-11-20
- Result: 12 skills scanned, 0 findings, 12 safe.
- Max severity: none (0 critical, 0 high, 0 medium, 0 low, 0 info).

The flawed variants were not scanned. They only differ in frontmatter and structure, and they hold no new scripts.

## Other checks

See docs/RELEASE_CHECK.md for gitleaks, pip-audit, `ruff check --select S` and actionlint.
