"""Exercise the actual Milestone 2 command-line applications against Milestone 1."""

from pathlib import Path
import subprocess
import sys

import pytest

from bs4.tests import LXML_PRESENT

ROOT = Path(__file__).resolve().parents[2]
FIXTURES = ROOT / "apps" / "m2" / "fixtures"


def run(milestone, task, source, *extra):
    return subprocess.run(
        [sys.executable, str(ROOT / "apps" / milestone / f"task{task}.py"), str(source), *map(str, extra)],
        cwd=source.parent, text=True, capture_output=True,
    )


@pytest.mark.parametrize("suffix", ["html", pytest.param("xml", marks=pytest.mark.skipif(not LXML_PRESENT, reason="lxml"))])
@pytest.mark.parametrize("task", [2, 3, 4, 6])
def test_cli_matches_milestone1(task, suffix, tmp_path):
    source = FIXTURES / f"example.{suffix}"
    if task == 6:
        before = run("m1", task, source, "-o", tmp_path / "before")
        after = run("m2", task, source, "-o", tmp_path / "after")
        assert (tmp_path / "before").read_bytes() == (tmp_path / "after").read_bytes()
    else:
        before, after = run("m1", task, source), run("m2", task, source)
        assert before.stdout == after.stdout
    assert before.returncode == after.returncode == 0, after.stderr


def test_cli_id_escaping_and_nested_unselected_tags(tmp_path):
    source = tmp_path / "input.html"
    source.write_text('<div id="a&amp;&quot;b"><p>child without id</p><p id="">empty id</p></div>', encoding="utf-8")
    result = run("m2", 4, source)
    assert result.returncode == 0
    assert result.stdout == '<div id="a&amp;&quot;b">\n<p id="">\n'


def test_cli_rejects_missing_input(tmp_path):
    result = run("m2", 2, tmp_path / "missing.html")
    assert result.returncode == 2
    assert "No such file" in result.stderr


@pytest.mark.parametrize("alias", ["same", "symlink", "hardlink"])
def test_cli_task6_preserves_input(tmp_path, alias):
    source = tmp_path / "input.html"
    source.write_text("<b>keep source</b>", encoding="utf-8")
    output = source if alias == "same" else tmp_path / "alias.html"
    if alias == "symlink":
        output.symlink_to(source)
    elif alias == "hardlink":
        output.hardlink_to(source)
    result = run("m2", 6, source, "-o", output)
    assert result.returncode == 2
    assert "different file" in result.stderr
    assert source.read_text(encoding="utf-8") == "<b>keep source</b>"


def test_cli_module_invocation():
    result = subprocess.run([sys.executable, "-m", "apps.m2.task2", str(FIXTURES / "example.html")],
                            cwd=ROOT, text=True, capture_output=True)
    assert result.returncode == 0, result.stderr
    assert result.stdout == "https://example.com/?a=1&b=2\n"
