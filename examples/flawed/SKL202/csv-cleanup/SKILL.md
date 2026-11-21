---
name: csv-cleanup
description: Cleans CSV files when asked.
license: MIT
---

# CSV cleanup

Clean a CSV file without losing data.

## Steps

1. Detect the delimiter and the encoding. Read the file as UTF-8 when you can.
2. Make headers snake_case and unique.
3. Trim spaces in every cell.
4. Drop rows that are exact duplicates. Report how many you dropped.
5. Convert dates to ISO 8601 (`2026-11-20`) and numbers to plain decimals with no thousands separator.
6. Write the result to a new file. Never overwrite the input.

Run [the cleanup script](scripts/clean.py) for large files.

## Report

Tell the user the row count before and after, the columns you renamed and any cells you could not parse.
