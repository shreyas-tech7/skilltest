# skilltrial and skills-ref

skills-ref is the reference validator from the Agent Skills project (PyPI `skills-ref`, command `agentskills`). `scripts/compare_skills_ref.py` runs `agentskills validate` on every clean example and every flawed variant and compares its verdict with skilltrial's. skilltrial calls a skill invalid when it has at least one error. The counts are in `results/skills_ref_compare.json` and in the README.

Both tools agree on every clean example and on most flawed variants. They differ on four. In each case skilltrial follows the spec text, as the brief asks, and no lint rule changed to match skills-ref.

| Flawed variant | skills-ref | skilltrial | Why skilltrial says what it says |
| --- | --- | --- | --- |
| SKL001, `skill.md` in lower case | valid | invalid | The spec says a skill holds a `SKILL.md` file. skills-ref also accepts the lower case name. skilltrial reports the case and says how to fix it. |
| SKL012, metadata value is a number | valid | invalid | The spec says metadata maps string keys to string values. YAML reads `1.0` as a number. |
| SKL013, allowed-tools as a YAML list | valid | invalid | The spec says allowed-tools is a space-separated string. |
| SKL201, unknown top-level field | invalid | valid (warning) | skills-ref allows only the six spec fields. The spec lists six fields but never forbids others, so skilltrial gives style advice, not an error. |
