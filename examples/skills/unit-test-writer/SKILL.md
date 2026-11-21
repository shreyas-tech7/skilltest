---
name: unit-test-writer
description: Writes pytest unit tests for Python functions, with fixtures, fake test data and edge cases. Use when the user asks for unit tests, more test coverage, or test data for a function.
license: MIT
---

# Unit test writer

Write focused pytest tests for one function at a time.

## Steps

1. Read the function and list its inputs, outputs and error cases.
2. Write one test per behavior. Name it `test_<function>_<behavior>`.
3. Put shared setup in a fixture in `conftest.py`.
4. Add edge cases: empty input, one item, the largest allowed value and a bad type.
5. Run the tests and show the result.

## Rules

- Use `pytest.raises` for errors and check the message.
- Use `tmp_path` for any file the test writes.
- Do not mock the function under test.
