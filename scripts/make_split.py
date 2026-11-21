"""Write examples/triggers/split.json. The split depends only on prompt IDs and the seed.
Run: .venv/bin/python scripts/make_split.py [--check]"""

import json
import sys
from pathlib import Path

from skilltrial.prompts import load_prompts, make_split

ROOT = Path(__file__).resolve().parent.parent
FOLDER = ROOT / "examples" / "triggers"


def main(argv: list[str]) -> int:
    text = json.dumps(make_split(load_prompts(FOLDER)), indent=1) + "\n"
    path = FOLDER / "split.json"
    if "--check" in argv:
        ok = path.exists() and path.read_text() == text
        print("split matches" if ok else "split differs")
        return 0 if ok else 1
    path.write_text(text)
    print(f"wrote {path.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
