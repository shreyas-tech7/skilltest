#!/usr/bin/env bash
# Count the example skill budgets with shell tools (sed, awk, wc), apart from the Python code.
# Tokens = (characters + 3) / 4 in integer math, the same as ceil(characters / 4).
# Run: bash scripts/hand_count.sh          (write tests/fixtures/hand_counts.json)
#      bash scripts/hand_count.sh --check  (fail if the committed file differs)
set -euo pipefail
cd "$(dirname "$0")/.."
export LC_ALL=C.UTF-8
tok() { echo $(( ($1 + 3) / 4 )); }
out=$(mktemp)
{
  echo "{"
  first=1
  for d in examples/skills/*/; do
    s=$(basename "$d")
    md="$d/SKILL.md"
    name_c=$(sed -n 's/^name: //p' "$md" | head -1 | tr -d '\n' | wc -m)
    desc_c=$(sed -n 's/^description: //p' "$md" | head -1 | tr -d '\n' | wc -m)
    meta=$((name_c + desc_c))
    body=$(awk 'c>=2{print; next} /^---$/{c++}' "$md" | wc -m)
    lines=$(wc -l < "$md")
    files=0
    while IFS= read -r f; do
      c=$(wc -m < "$f")
      files=$((files + $(tok "$c")))
    done < <(find "$d" -type f ! -name SKILL.md | sort)
    [ $first -eq 1 ] || echo ","
    first=0
    printf '  "%s": {"metadata_chars": %d, "metadata_tokens": %d, "body_chars": %d, "body_tokens": %d, "lines": %d, "files_tokens": %d}' \
      "$s" "$meta" "$(tok $meta)" "$body" "$(tok $body)" "$lines" "$files"
  done
  echo
  echo "}"
} > "$out"
if [ "${1:-}" = "--check" ]; then
  if diff -q "$out" tests/fixtures/hand_counts.json >/dev/null; then echo "hand counts match"; rm -f "$out"; exit 0; fi
  echo "hand counts differ from tests/fixtures/hand_counts.json"; rm -f "$out"; exit 1
fi
mv "$out" tests/fixtures/hand_counts.json
echo "wrote tests/fixtures/hand_counts.json"
