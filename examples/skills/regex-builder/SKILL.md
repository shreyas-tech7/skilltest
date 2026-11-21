---
name: regex-builder
description: Builds regular expressions from plain-language rules and tests them against sample strings, with notes on escaping per language. Use when the user needs a regex to match, validate or extract text patterns.
license: MIT
---

# Regex builder

Turn a plain rule into a tested regular expression.

## Steps

1. Restate the rule as a list of must-match and must-not-match examples.
2. Write the pattern. Anchor it with `^` and `$` when the whole string must match.
3. Test it against every example with [the test script](scripts/test_regex.py).
4. Explain each part of the pattern in a short table.
5. Show the escaped form for the user's language (Python raw string, JavaScript literal or JSON string).

## Watch for

- Greedy `.*` that eats too much. Prefer a negated class like `[^"]*`.
- Catastrophic backtracking from nested quantifiers such as `(a+)+`.
