#!/usr/bin/env bash
# Write docs/DEMO.md from a real terminal session. Run from the repo root after ./init.sh.
set -uo pipefail
cd "$(dirname "$0")/.."
ST=.venv/bin/skilltrial
run() {
  echo '```console'
  echo "\$ skilltrial ${*}"
  timeout 300 "$ST" "$@" 2>&1
  echo "(exit code $?)"
  echo '```'
  echo
}
{
  echo "# Demo"
  echo
  echo "A real terminal session, written by \`scripts/make_demo.sh\` on $(date -u +%Y-%m-%d). Each block shows the exit code."
  echo
  echo "## Lint the clean example skills"
  echo
  run lint examples/skills
  echo "## Lint one skill with a planted flaw"
  echo
  run lint examples/flawed/SKL101
  echo "## Token budget for one skill"
  echo
  run budget examples/skills/sql-helper
  echo "## Rerun the trigger eval and compare it with the committed results"
  echo
  run trigger examples/skills --check
  echo "## Overlapping skills"
  echo
  run overlap examples/skills
  echo "## Confirm the README tables"
  echo
  run readme --check
} > docs/DEMO.md
echo "wrote docs/DEMO.md"
