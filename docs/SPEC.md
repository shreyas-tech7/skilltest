# Spec source

- Source used: https://raw.githubusercontent.com/agentskills/agentskills/main/docs/specification.mdx
- Fetched: 2026-11-20
- sha256 of the fetched file: b9079c0c10b7930e8c6a20ff2bc10cda2a3343c55185120e3f1116a1a529b220
- First source in the brief (https://agentskills.io/specification.md) answered 403 through the proxy.

## Rules taken from the spec text

| Spec text | skilltrial rule | Severity |
| --- | --- | --- |
| A skill is a directory containing, at minimum, a `SKILL.md` file | SKL001 | error |
| `SKILL.md` must contain YAML frontmatter followed by Markdown content | SKL002 | error |
| `name` is required | SKL003 | error |
| `name` must be 1 to 64 characters | SKL004 | error |
| `name` may only contain lowercase letters, digits and hyphens | SKL005 | error |
| `name` must not start or end with a hyphen | SKL006 | error |
| `name` must not contain consecutive hyphens | SKL007 | error |
| `name` must match the parent directory name | SKL008 | error |
| `description` is required and non-empty | SKL009 | error |
| `description` is at most 1024 characters | SKL010 | error |
| `compatibility` must be 1 to 500 characters if provided | SKL011 | error |
| `metadata` is a map from string keys to string values | SKL012 | error |
| `allowed-tools` is a space-separated string (experimental) | SKL013 | error |
| Keep your main `SKILL.md` under 500 lines | SKL101 | warning, spec guidance |
| Instructions under 5000 tokens recommended | SKL102 | warning, spec guidance |
| Metadata about 100 tokens | SKL103 | warning, spec guidance |
| Keep file references one level deep | SKL104 | warning, spec guidance |
| Description should say what the skill does and when to use it | SKL105 | warning, spec guidance |
| Use relative paths from the skill root | SKL106 | warning, spec guidance |

The rules SKL201 to SKL204 are style advice. The spec does not state them.
