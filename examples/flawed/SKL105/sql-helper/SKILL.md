---
name: sql-helper
description: Writes, explains and optimizes SQL queries for PostgreSQL and SQLite, including joins, window functions and indexes.
license: MIT
---

# SQL helper

Write correct, readable SQL and explain it.

## Steps

1. Ask for the table definitions if you do not have them. Do not guess column names.
2. Write the query with one clause per line and uppercase keywords.
3. Explain what each join and filter does in one sentence each.
4. For a slow query, read the `EXPLAIN ANALYZE` output and point to the costly step.
5. Suggest an index only when the plan shows a sequential scan on a large table.

## Rules

- Use parameters (`$1` or `?`) for user input. Never build SQL with string concatenation.
- Prefer window functions over self joins for running totals and rankings.

Dialect differences are in [the dialect notes](references/DIALECTS.md).
