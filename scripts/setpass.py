"""Set passes=true for the given feature IDs, only after their steps pass.
Run: .venv/bin/python scripts/setpass.py F01 F02 ..."""

import json
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def main(ids: list[str]) -> int:
    env = dict(os.environ)
    env["PATH"] = f"{ROOT / '.venv' / 'bin'}:{Path.home() / 'go' / 'bin'}:{env.get('PATH', '')}"
    feats = json.loads((ROOT / "feature_list.json").read_text())
    bad = []
    for f in feats:
        if f["id"] not in ids:
            continue
        ok = all(subprocess.run(s, shell=True, cwd=ROOT, env=env, capture_output=True,  # noqa: S602
                                timeout=900).returncode == 0 for s in f["steps"])
        if ok:
            f["passes"] = True
        else:
            bad.append(f["id"])
    (ROOT / "feature_list.json").write_text(json.dumps(feats, indent=2) + "\n")
    print("failed:", bad if bad else "none")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
