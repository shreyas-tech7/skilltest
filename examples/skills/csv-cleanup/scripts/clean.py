"""Example cleanup script for the csv-cleanup skill. skilltrial never runs it."""

import csv
import sys


def main(src: str, dst: str) -> None:
    with open(src, newline="", encoding="utf-8") as f:
        rows = list(csv.reader(f))
    seen, out = set(), []
    for row in rows:
        key = tuple(cell.strip() for cell in row)
        if key not in seen:
            seen.add(key)
            out.append(list(key))
    with open(dst, "w", newline="", encoding="utf-8") as f:
        csv.writer(f).writerows(out)


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
