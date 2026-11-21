"""Every documented exit code, for every command. 0 ok, 1 findings or failed check, 2 usage, 3 no skills or bad input."""

import shutil

import pytest
from helpers import EXAMPLES, MANIFEST, ROOT

from skilltrial.cli import FINDINGS, NO_INPUT, OK, USAGE, main

TRIG = str(ROOT / "examples/triggers")
RES = str(ROOT / "results")


def run(*args) -> int:
    return main([str(a) for a in args])


def test_codes_are_the_documented_values():
    assert (OK, FINDINGS, USAGE, NO_INPUT) == (0, 1, 2, 3)


def test_lint_clean_is_0(capsys):
    assert run("lint", EXAMPLES) == OK
    assert "0 errors, 0 warnings" in capsys.readouterr().out


def test_lint_error_is_1():
    assert run("lint", ROOT / MANIFEST["SKL007"]["flawed"]) == FINDINGS


def test_lint_warning_is_0_unless_strict():
    path = ROOT / MANIFEST["SKL105"]["flawed"]
    assert run("lint", path) == OK
    assert run("lint", path, "--strict") == FINDINGS


def test_no_skills_is_3(tmp_path, capsys):
    assert run("lint", tmp_path) == NO_INPUT
    assert "no skill folders" in capsys.readouterr().err
    for cmd in ("budget", "trigger", "overlap"):
        assert run(cmd, tmp_path) == NO_INPUT


def test_usage_error_is_2():
    for args in ([], ["nope"], ["lint"], ["trigger", EXAMPLES, "--split", "bogus"]):
        with pytest.raises(SystemExit) as e:
            run(*args)
        assert e.value.code == USAGE


def test_budget_codes():
    assert run("budget", EXAMPLES) == OK
    assert run("budget", EXAMPLES, "--strict") == OK
    over = ROOT / MANIFEST["SKL102"]["flawed"]
    assert run("budget", over) == OK
    assert run("budget", over, "--strict") == FINDINGS


def test_trigger_codes(capsys):
    assert run("trigger", EXAMPLES, "--prompts", TRIG, "--results", RES) == OK
    assert "95% CI" in capsys.readouterr().out
    assert run("trigger", EXAMPLES, "--prompts", TRIG, "--results", RES, "--min-f1", "0.99") == FINDINGS
    assert run("trigger", EXAMPLES, "--prompts", TRIG, "--results", RES, "--check") == OK


def test_trigger_bad_prompts_is_3(tmp_path):
    assert run("trigger", EXAMPLES, "--prompts", tmp_path / "missing") == NO_INPUT
    (tmp_path / "x.yaml").write_text("- just a list\n")
    assert run("trigger", EXAMPLES, "--prompts", tmp_path) == NO_INPUT
    empty = tmp_path / "empty"
    empty.mkdir()
    assert run("trigger", EXAMPLES, "--prompts", empty) == NO_INPUT


def test_check_mismatch_is_1(tmp_path):
    res = tmp_path / "results"
    shutil.copytree(ROOT / "results", res)
    (res / "trigger_bm25_heldout.json").write_text("{}")
    (res / "overlap.json").write_text("{}")
    assert run("trigger", EXAMPLES, "--prompts", TRIG, "--results", res, "--check") == FINDINGS
    assert run("overlap", EXAMPLES, "--prompts", TRIG, "--results", res, "--check") == FINDINGS


def test_overlap_codes():
    assert run("overlap", EXAMPLES, "--prompts", TRIG, "--results", RES) == OK
    assert run("overlap", EXAMPLES, "--prompts", TRIG, "--results", RES, "--fail-on-overlap") == FINDINGS
    assert run("overlap", EXAMPLES, "--prompts", TRIG, "--results", RES, "--check") == OK


def test_write_goes_to_the_results_folder(tmp_path):
    res = tmp_path / "out"
    assert run("trigger", EXAMPLES, "--prompts", TRIG, "--results", res, "--write") == OK
    assert (res / "trigger_bm25_heldout.json").exists() and (res / "seed2" / "tuning_bm25.json").exists()
    assert run("overlap", EXAMPLES, "--prompts", TRIG, "--results", res, "--write") == OK
    assert (res / "overlap.json").exists()


def test_json_output(capsys):
    import json

    run("lint", ROOT / MANIFEST["SKL004"]["flawed"], "--json")
    assert json.loads(capsys.readouterr().out)[0]["rule"] == "SKL004"


def test_version(capsys):
    with pytest.raises(SystemExit) as e:
        run("--version")
    assert e.value.code == 0 and "skilltrial" in capsys.readouterr().out


def test_trigger_malformed_yaml_is_3(tmp_path, capsys):
    """Broken case: bad YAML in a prompt file printed a traceback and exited 1."""
    (tmp_path / "x.yaml").write_text("skill: [unclosed\n")
    assert run("trigger", EXAMPLES, "--prompts", tmp_path) == NO_INPUT
    assert "x.yaml" in capsys.readouterr().err


def test_tuned_settings_apply_only_to_the_skills_they_were_tuned_on(tmp_path, capsys):
    """Broken case: run from the repo root, trigger on other skills used the example-tuned settings."""
    import shutil

    skills = tmp_path / "mine"
    shutil.copytree(ROOT / "examples/skills/csv-cleanup", skills / "csv-cleanup")
    shutil.copytree(ROOT / "examples/skills/sql-helper", skills / "sql-helper")
    trig = tmp_path / "trig"
    trig.mkdir()
    for s in ("csv-cleanup", "sql-helper"):
        shutil.copy(ROOT / f"examples/triggers/{s}.yaml", trig)
    assert run("trigger", skills, "--prompts", trig, "--results", ROOT / "results", "--split", "all") == OK
    out = capsys.readouterr()
    assert "k1': 1.2" in out.out and "untuned" in out.err
    assert run("trigger", EXAMPLES, "--results", ROOT / "results") == OK
    assert "k1': 2.0" in capsys.readouterr().out


def test_small_split_warns_about_the_interval(tmp_path, capsys):
    """Broken case: a tiny held-out split printed a 1.000 to 1.000 interval with no warning."""
    import shutil

    trig = tmp_path / "trig"
    trig.mkdir()
    shutil.copy(ROOT / "examples/triggers/csv-cleanup.yaml", trig)
    assert run("trigger", EXAMPLES, "--prompts", trig, "--results", tmp_path, "--split", "heldout") == OK
    assert "too few prompts" in capsys.readouterr().err
