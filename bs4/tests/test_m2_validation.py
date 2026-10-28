"""Checks for the incremental reference used in large-file validation."""

import hashlib
import sys

import pytest

from apps.m2.generate_large_input import generate
from apps.m2 import validate_gb
from apps.m2.validate_gb import Fingerprint, guarded_run
from apps.m2.validate_large import file_hash, files_equal


def scan(markup, chunk_size, normalize=False):
    reference = Fingerprint(normalize)
    for offset in range(0, len(markup), chunk_size):
        reference.feed(markup[offset:offset + chunk_size])
    reference.close()
    return reference.summary()


def test_original_16_mib_fixture_is_reproducible(tmp_path):
    path = tmp_path / "input.html"
    assert generate(path) == 15770
    assert path.stat().st_size == 16 * 1024 * 1024
    assert file_hash(path) == "1dcfc307c4a7998de67e219a20c53abf10f25446fd1aa5f7796cad25ff0dd9e5"


@pytest.mark.parametrize("words", [0, -1])
def test_generator_rejects_nonpositive_padding(tmp_path, words):
    with pytest.raises(ValueError, match="padding_words"):
        generate(tmp_path / "input.html", padding_words=words)


def test_reference_is_independent_of_read_chunk_boundaries():
    markup = '<!DOCTYPE html><html><body><p id="a&amp;b">A &amp; B<b>C</b></p><a href="/q?a=1&amp;b=2">link</a></body></html>'
    expected = scan(markup, len(markup))
    assert scan(markup, 1) == scan(markup, 7) == expected
    assert expected["task_output_sha256"]["2"] == hashlib.sha256(b"/q?a=1&b=2\n").hexdigest()
    assert expected["task_output_sha256"]["4"] == hashlib.sha256(b'<p id="a&amp;b">\n').hexdigest()


def test_reference_detects_tree_text_and_attribute_changes():
    original = '<html><body><b id="q">A<b>B</b>C</b><p>D</p></body></html>'
    renamed = original.replace('<b ', '<blockquote ').replace('<b>', '<blockquote>').replace('</b>', '</blockquote>')
    before, after = scan(original, 13), scan(renamed, 19, normalize=True)
    assert after["structure_sha256"] == before["structure_sha256"]
    assert after["non_whitespace_text_sha256"] == before["non_whitespace_text_sha256"]
    assert after["tag_counts"].get("b", 0) == 0
    assert after["tag_counts"]["blockquote"] == before["tag_counts"]["b"]
    assert scan(renamed.replace('id="q"', 'id="wrong"'), 9, True)["structure_sha256"] != before["structure_sha256"]
    assert scan(renamed.replace('>D<', '>wrong<'), 9, True)["non_whitespace_text_sha256"] != before["non_whitespace_text_sha256"]


def test_large_output_comparison_detects_changes_past_first_chunk(tmp_path):
    first, second = tmp_path / "first", tmp_path / "second"
    data = b"x" * (1024 * 1024 + 10)
    first.write_bytes(data)
    second.write_bytes(data)
    assert files_equal(first, second)
    second.write_bytes(data[:-1] + b"y")
    assert not files_equal(first, second)
    second.write_bytes(data[:-1])
    assert not files_equal(first, second)


def test_timeout_terminates_the_child_process(tmp_path, monkeypatch):
    monkeypatch.setattr(validate_gb, "rss_mib", lambda pid: 1)
    monkeypatch.setattr(validate_gb, "memory_free_percent", lambda: 100)
    result = guarded_run(
        [sys.executable, "-c", "import time; time.sleep(30)"],
        tmp_path / "stdout", tmp_path / "stderr",
        timeout=0.1, minimum_free=0,
    )
    assert result["status"] == "stopped"
    assert result["stop_reason"] == "timeout exceeded"
    assert result["exit_code"] != 0


def test_monitoring_failure_does_not_leave_child_running(tmp_path, monkeypatch):
    processes = []
    original_popen = validate_gb.subprocess.Popen

    def capture_process(*args, **kwargs):
        process = original_popen(*args, **kwargs)
        processes.append(process)
        return process

    def unavailable(pid):
        raise PermissionError("monitor unavailable")

    monkeypatch.setattr(validate_gb.subprocess, "Popen", capture_process)
    monkeypatch.setattr(validate_gb, "rss_mib", unavailable)
    with pytest.raises(PermissionError, match="monitor unavailable"):
        guarded_run([sys.executable, "-c", "import time; time.sleep(30)"],
                    tmp_path / "stdout", tmp_path / "stderr")
    assert len(processes) == 1
    assert processes[0].poll() is not None


@pytest.mark.parametrize(
    "rss,free,reason",
    [(2, 100, "process RSS limit exceeded"),
     (0, 10, "system memory free percentage below configured minimum")],
)
def test_resource_guards_stop_the_child(tmp_path, monkeypatch, rss, free, reason):
    monkeypatch.setattr(validate_gb, "rss_mib", lambda pid: rss)
    monkeypatch.setattr(validate_gb, "memory_free_percent", lambda: free)
    result = guarded_run(
        [sys.executable, "-c", "import time; time.sleep(30)"],
        tmp_path / "stdout", tmp_path / "stderr",
        timeout=10, rss_limit_mib=1, minimum_free=15,
    )
    assert result["status"] == "stopped"
    assert result["stop_reason"] == reason
    assert result["exit_code"] != 0
