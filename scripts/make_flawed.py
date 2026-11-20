"""Build examples/flawed/: one broken copy of a clean example skill per lint rule.

Each copy differs from its clean skill by one change, so the clean skill is the fixed version.
Run: .venv/bin/python scripts/make_flawed.py          (write the files)
     .venv/bin/python scripts/make_flawed.py --check  (fail if the committed files differ)
"""

import filecmp
import json
import shutil
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CLEAN = ROOT / "examples" / "skills"
OUT = ROOT / "examples" / "flawed"
LONG_NAME = "image-resize-" + "-".join(["and-convert"] * 5) + "-tool"
FILLER = "Keep this step short and plain so that the agent can follow it without extra context. "


def sub(old, new):
    def f(d: Path):
        p = d / "SKILL.md"
        t = p.read_text(encoding="utf-8")
        assert old in t, (d, old)
        p.write_text(t.replace(old, new, 1), encoding="utf-8")
    return f


def set_desc(new):
    def f(d: Path):
        p = d / "SKILL.md"
        lines = p.read_text(encoding="utf-8").split("\n")
        i = next(i for i, ln in enumerate(lines) if ln.startswith("description:"))
        lines[i] = f"description: {new}"
        p.write_text("\n".join(lines), encoding="utf-8")
    return f


def append_body(text):
    def f(d: Path):
        p = d / "SKILL.md"
        p.write_text(p.read_text(encoding="utf-8") + text, encoding="utf-8")
    return f


def rename_name(new):
    return sub("name: image-resize\n", f"name: {new}\n")


def lowercase_file(d: Path):
    (d / "SKILL.md").rename(d / "skill.md")


def drop_fences(d: Path):
    p = d / "SKILL.md"
    t = p.read_text(encoding="utf-8")
    p.write_text(t.replace("---\n", "", 2), encoding="utf-8")


def empty_body(d: Path):
    p = d / "SKILL.md"
    t = p.read_text(encoding="utf-8")
    head, _, _ = t.partition("\n---\n")
    p.write_text(head + "\n---\n", encoding="utf-8")


def nested_ref(d: Path):
    f = d / "references" / "FORMAT.md"
    f.write_text(f.read_text(encoding="utf-8") + "\nMore samples are in [the examples](EXAMPLES.md).\n", encoding="utf-8")
    (d / "references" / "EXAMPLES.md").write_text("# Examples\n\nA sample release entry.\n", encoding="utf-8")


def delete_script(d: Path):
    (d / "scripts" / "test_regex.py").unlink()


LONG_DESC = ("Resizes, crops and converts images between PNG, JPEG and WebP while keeping the aspect ratio. "
             * 12).strip()
MID_DESC = ("Resizes, crops and converts images between PNG, JPEG and WebP while keeping the aspect ratio, "
            "reads the size and format first, picks the Lanczos filter, saves at quality 85, strips location "
            "data, never upscales unless asked, reports the old and new size in pixels and kilobytes, and handles "
            "folders of photos in one pass with a summary table at the end for every file it changed or skipped. "
            "Use when the user wants to resize an image, shrink image files, or make smaller versions of photos.")

# rule: (clean skill, flawed folder name, what changed, mutation)
VARIANTS = {
    "SKL001": ("csv-cleanup", "csv-cleanup", "SKILL.md renamed to skill.md", lowercase_file),
    "SKL002": ("commit-message", "commit-message", "the two '---' frontmatter lines removed", drop_fences),
    "SKL003": ("image-resize", "image-resize", "name line removed", sub("name: image-resize\n", "")),
    "SKL004": ("image-resize", LONG_NAME, f"name and folder are {len(LONG_NAME)} characters", rename_name(LONG_NAME)),
    "SKL005": ("image-resize", "Image_Resize", "name uses uppercase and an underscore", rename_name("Image_Resize")),
    "SKL006": ("image-resize", "image-resize-", "name ends with a hyphen", rename_name("image-resize-")),
    "SKL007": ("image-resize", "image--resize", "name has a double hyphen", rename_name("image--resize")),
    "SKL008": ("image-resize", "image-resizer", "folder renamed so it no longer matches the name", lambda d: None),
    "SKL009": ("meeting-notes", "meeting-notes", "description set to an empty string", set_desc('""')),
    "SKL010": ("image-resize", "image-resize", f"description repeated to {len(LONG_DESC)} characters", set_desc(LONG_DESC)),
    "SKL011": ("csv-cleanup", "csv-cleanup", "compatibility of 600 characters added",
               sub("license: MIT\n", "license: MIT\ncompatibility: " + "x" * 600 + "\n")),
    "SKL012": ("csv-cleanup", "csv-cleanup", "metadata value is a number, not a string",
               sub("license: MIT\n", "license: MIT\nmetadata:\n  version: 1.0\n")),
    "SKL013": ("csv-cleanup", "csv-cleanup", "allowed-tools written as a YAML list",
               sub("license: MIT\n", "license: MIT\nallowed-tools:\n  - Read\n  - Bash\n")),
    "SKL101": ("commit-message", "commit-message", "520 filler lines appended to the body",
               append_body("".join(f"\n- Note {i}." for i in range(520)) + "\n")),
    "SKL102": ("commit-message", "commit-message", "100 long filler lines appended (about 5,400 more tokens)",
               append_body("".join("\n" + FILLER * 2 + FILLER[:46] for _ in range(100)) + "\n")),
    "SKL103": ("image-resize", "image-resize", "description grown to about 130 tokens", set_desc(MID_DESC)),
    "SKL104": ("changelog-writer", "changelog-writer", "references/FORMAT.md now links to references/EXAMPLES.md",
               nested_ref),
    "SKL105": ("sql-helper", "sql-helper", "the 'Use when' sentence removed from the description",
               set_desc("Writes, explains and optimizes SQL queries for PostgreSQL and SQLite, including joins, "
                        "window functions and indexes.")),
    "SKL106": ("dockerfile-review", "dockerfile-review", "checklist link points outside the skill folder",
               sub("(references/CHECKLIST.md)", "(../shared/CHECKLIST.md)")),
    "SKL201": ("csv-cleanup", "csv-cleanup", "top-level version field added",
               sub("license: MIT\n", "license: MIT\nversion: \"1.0\"\n")),
    "SKL202": ("csv-cleanup", "csv-cleanup", "description cut to 28 characters", set_desc("Cleans CSV files when asked.")),
    "SKL203": ("regex-builder", "regex-builder", "scripts/test_regex.py deleted", delete_script),
    "SKL204": ("thumbnail-maker", "thumbnail-maker", "body removed", empty_body),
}


def build(out: Path) -> dict:
    manifest = {}
    for rule, (clean, folder, change, mutate) in VARIANTS.items():
        dest = out / rule / folder
        shutil.copytree(CLEAN / clean, dest)
        mutate(dest)
        for d in sorted(dest.rglob("*"), reverse=True):  # git keeps no empty folders, so the script must not make any
            if d.is_dir() and not any(d.iterdir()):
                d.rmdir()
        manifest[rule] = {"flawed": f"examples/flawed/{rule}/{folder}", "fixed": f"examples/skills/{clean}",
                          "change": change}
    (out / "MANIFEST.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    return manifest


def same_tree(a: Path, b: Path) -> bool:
    cmp = filecmp.dircmp(a, b)
    if cmp.left_only or cmp.right_only or cmp.funny_files:
        return False
    _, mismatch, errors = filecmp.cmpfiles(a, b, cmp.common_files, shallow=False)
    return not mismatch and not errors and all(same_tree(a / d, b / d) for d in cmp.common_dirs)


def main(argv: list[str]) -> int:
    if "--check" in argv:
        with tempfile.TemporaryDirectory() as tmp:
            build(Path(tmp) / "flawed")
            ok = OUT.exists() and same_tree(Path(tmp) / "flawed", OUT)
        print("flawed variants match the script" if ok else "flawed variants differ: run scripts/make_flawed.py")
        return 0 if ok else 1
    if OUT.exists():
        shutil.rmtree(OUT)
    build(OUT)
    print(f"wrote {len(VARIANTS)} flawed variants to {OUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
