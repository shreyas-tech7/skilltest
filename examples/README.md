# Example skills

Twelve invented Agent Skills for the skilltrial tests and the trigger eval. They were written for this repo and are not copied from anyone else's skills. They are MIT licensed, like the rest of the repo (see the LICENSE file at the root).

- `skills/`: the clean skills. Each one lints with no findings.
- `flawed/`: one broken copy per lint rule, made by `scripts/make_flawed.py`. `flawed/MANIFEST.json` maps each rule to its broken copy and the clean skill that fixes it.
- `triggers/`: prompts that should and should not trigger each skill, and the tuning and held-out split.
- `PLANTED_OVERLAPS.json`: the skill pairs whose descriptions were written to compete on purpose.

The scripts inside the skills are examples only. skilltrial never runs them.
