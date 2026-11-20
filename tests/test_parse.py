from helpers import EXAMPLES

from skilltrial.parse import find_skill_dirs, load_skill, local_refs, split_frontmatter


def test_finds_the_twelve_examples():
    assert len(find_skill_dirs(EXAMPLES)) == 12


def test_root_that_is_a_skill_is_one_skill():
    assert find_skill_dirs(EXAMPLES / "csv-cleanup") == [EXAMPLES / "csv-cleanup"]


def test_missing_root_finds_nothing(tmp_path):
    assert find_skill_dirs(tmp_path / "nope") == []
    assert find_skill_dirs(tmp_path) == []


def test_split_frontmatter():
    fm, body = split_frontmatter("---\nname: a\n---\nhello\n")
    assert fm == "name: a" and body == "hello\n"
    assert split_frontmatter("no fence\n") == (None, "no fence\n")
    assert split_frontmatter("---\nname: a\n")[0] is None  # never closed


def test_safe_load_refuses_python_tags(tmp_path):
    """Broken case: yaml.load would build a Python object from this tag. safe_load refuses it."""
    d = tmp_path / "x"
    d.mkdir()
    (d / "SKILL.md").write_text("---\nname: !!python/object/apply:os.system ['true']\n---\nbody\n")
    s = load_skill(d)
    assert s.frontmatter is None and "not valid YAML" in s.fm_error


def test_local_refs_skip_code_and_urls():
    md = "See [a](references/A.md) and [web](https://x.org) and [top](#top).\nRun scripts/run.py.\n```\nassets/no.txt\n```\n"
    assert local_refs(md) == ["references/A.md", "scripts/run.py"]


def test_example_fields():
    s = load_skill(EXAMPLES / "sql-helper")
    assert s.field("name") == "sql-helper" and s.field("license") == "MIT"
    assert s.refs == ["references/DIALECTS.md"]
