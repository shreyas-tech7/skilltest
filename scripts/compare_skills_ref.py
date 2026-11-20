"""Run the reference validator (skills-ref, command `agentskills`) on every example and flawed skill and
compare its valid or invalid verdict with skilltrial's (invalid = at least one error). Writes
results/skills_ref_compare.json. Needs `uv tool install skills-ref`. Run: .venv/bin/python scripts/compare_skills_ref.py"""

import datetime as dt
import json
import shutil
import subprocess
import sys
from pathlib import Path

from skilltrial.lint import lint_skill
from skilltrial.parse import load_skill

ROOT = Path(__file__).resolve().parent.parent


def main() -> int:
    exe = shutil.which("agentskills")
    if not exe:
        print("agentskills (skills-ref) is not installed")
        return 1
    version = subprocess.run([exe, "--version"], capture_output=True, text=True, timeout=30).stdout.strip()
    manifest = json.loads((ROOT / "examples/flawed/MANIFEST.json").read_text())
    targets = [(f"examples/skills/{d.name}", None) for d in sorted((ROOT / "examples/skills").iterdir()) if d.is_dir()]
    targets += [(v["flawed"], rule) for rule, v in manifest.items()]
    rows = []
    for rel, rule in targets:
        proc = subprocess.run([exe, "validate", str(ROOT / rel)], capture_output=True, text=True, timeout=60)
        ref_valid = proc.returncode == 0
        findings = lint_skill(load_skill(ROOT / rel))
        ours_valid = not any(f.severity == "error" for f in findings)
        msg = [ln.strip("- ").strip() for ln in (proc.stdout + proc.stderr).splitlines()[1:] if ln.strip()]
        rows.append({"skill": rel, "planted_rule": rule, "skills_ref_valid": ref_valid, "skilltrial_valid": ours_valid,
                     "agree": ref_valid == ours_valid, "skills_ref_messages": msg,
                     "skilltrial_rules": sorted({f.rule for f in findings})})
    out = {"date": dt.date.today().isoformat(), "skills_ref_version": version, "n": len(rows),
           "agree": sum(r["agree"] for r in rows), "disagree": [r for r in rows if not r["agree"]], "rows": rows}
    (ROOT / "results/skills_ref_compare.json").write_text(json.dumps(out, indent=1) + "\n")
    print(f"{out['agree']} of {out['n']} verdicts agree")
    for r in out["disagree"]:
        print(f"differ: {r['skill']} skills-ref valid={r['skills_ref_valid']} skilltrial valid={r['skilltrial_valid']} "
              f"{r['skills_ref_messages']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
