"""Example test script for the regex-builder skill. skilltrial never runs it."""

import re
import sys

pattern = re.compile(sys.argv[1])
for line in sys.stdin:
    text = line.rstrip("\n")
    print("MATCH " if pattern.fullmatch(text) else "NO    ", text)
