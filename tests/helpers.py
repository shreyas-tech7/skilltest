"""Shared paths for the tests."""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
EXAMPLES = ROOT / "examples" / "skills"
MANIFEST = json.loads((ROOT / "examples" / "flawed" / "MANIFEST.json").read_text())
