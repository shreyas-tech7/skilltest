"""Run the steps of every feature in feature_list.json and print pass or fail.
It does not change any flag. Run: .venv/bin/python scripts/check_features.py [F01 F02 ...]"""

import json
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def main(ids) -> int:
    env = dict(os.environ)
    gobin = Path.home() / "go" / "bin"
    env["PATH"] = f"{ROOT / '.venv' / 'bin'}:{gobin}:{env.get('PATH', '')}"
    bad = 0
    for f in json.loads((ROOT / "feature_list.json").read_text()):
        if ids and f["id"] not in ids:
            continue
        ok = all(subprocess.run(step, shell=True, cwd=ROOT, env=env, capture_output=True,  # noqa: S602
                                timeout=900).returncode == 0 for step in f["steps"])
        flag = "true " if f["passes"] else "false"
        print(f"{f['id']} steps {'PASS' if ok else 'FAIL'} (flag {flag}) {f['description'][:70]}")
        bad += ok != f["passes"]
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
