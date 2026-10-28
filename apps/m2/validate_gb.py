"""Run the actual M1/M2 applications on generated HTML with resource guards.

The reference is an independent, incremental standard-library HTMLParser scan.
It computes exact task 2/3/4 output hashes and task 6 structural/text fingerprints.
No verification step constructs a second BeautifulSoup tree or reads a complete
output file into memory. Only the generated, well-formed HTML fixture is supported.
"""

import argparse
from collections import Counter
from datetime import datetime
import hashlib
from html import escape
from html.parser import HTMLParser
import json
from pathlib import Path
import platform
import re
import subprocess
import sys
from time import perf_counter, sleep
from zoneinfo import ZoneInfo

if __package__:
    from .validate_large import file_hash, files_equal
else:
    from validate_large import file_hash, files_equal

ROOT = Path(__file__).resolve().parents[2]


class Fingerprint(HTMLParser):
    """Incremental reference for the generated fixture, with bounded buffers."""

    def __init__(self, normalize_replacements=False):
        super().__init__(convert_charrefs=True)
        self.normalize_replacements = normalize_replacements
        self.events = hashlib.sha256()
        self.text = hashlib.sha256()
        self.tags = Counter()
        self.outputs = {task: hashlib.sha256() for task in (2, 3, 4)}
        self.lines = Counter()

    def event(self, *values):
        self.events.update((json.dumps(values, ensure_ascii=True) + "\n").encode("ascii"))

    def handle_starttag(self, tag, attrs):
        self.tags[tag] += 1
        values = dict(attrs)
        lines = {3: f"<{tag}>"}
        if tag == "a" and "href" in values:
            lines[2] = values["href"]
        if "id" in values:
            lines[4] = f'<{tag} id="{escape(values["id"], quote=True)}">'
        for task, line in lines.items():
            self.outputs[task].update((line + "\n").encode("utf-8"))
            self.lines[task] += 1
        if self.normalize_replacements and tag == "blockquote":
            tag = "b"
        self.event("start", tag, sorted(attrs))

    def handle_endtag(self, tag):
        if self.normalize_replacements and tag == "blockquote":
            tag = "b"
        self.event("end", tag)

    def handle_data(self, data):
        # Ignore formatting whitespace; chunk boundaries do not affect the
        # resulting concatenation of non-whitespace text characters.
        self.text.update("".join(data.split()).encode("utf-8"))

    def handle_decl(self, declaration):
        self.event("declaration", declaration)

    def summary(self):
        return {
            "structure_sha256": self.events.hexdigest(),
            "non_whitespace_text_sha256": self.text.hexdigest(),
            "tag_counts": dict(self.tags),
            "task_output_sha256": {str(task): digest.hexdigest() for task, digest in self.outputs.items()},
            "task_output_lines": {str(task): self.lines[task] for task in (2, 3, 4)},
        }


def fingerprint(path, normalize_replacements=False):
    parser = Fingerprint(normalize_replacements)
    with path.open("r", encoding="utf-8") as source:
        for chunk in iter(lambda: source.read(64 * 1024), ""):
            parser.feed(chunk)
    parser.close()
    return parser.summary()


def rss_mib(pid):
    result = subprocess.run(["ps", "-o", "rss=", "-p", str(pid)], capture_output=True, text=True)
    if result.returncode or not result.stdout.strip():
        return None
    return int(result.stdout.strip()) / 1024


def memory_free_percent():
    if sys.platform != "darwin":
        return None
    result = subprocess.run(["memory_pressure", "-Q"], capture_output=True, text=True, timeout=5)
    match = re.search(r"memory free percentage: (\d+)%", result.stdout)
    return int(match.group(1)) if match else None


def guarded_run(command, stdout, stderr, timeout=300, rss_limit_mib=6144, minimum_free=15):
    started = perf_counter()
    peak = 0
    lowest_free = None
    reason = None
    next_pressure = 0
    next_update = 15
    observed_rss = False
    with stdout.open("wb") as normal, stderr.open("wb") as errors:
        process = subprocess.Popen(command, stdout=normal, stderr=errors, stdin=subprocess.DEVNULL)
        try:
            while process.poll() is None:
                sample = rss_mib(process.pid)
                if sample is not None:
                    observed_rss = True
                    peak = max(peak, sample)
                elapsed = perf_counter() - started
                if elapsed >= next_pressure:
                    free = memory_free_percent()
                    if free is not None:
                        lowest_free = free if lowest_free is None else min(free, lowest_free)
                        if free < minimum_free:
                            reason = "system memory free percentage below configured minimum"
                    next_pressure = elapsed + 2
                if peak > rss_limit_mib:
                    reason = "process RSS limit exceeded"
                elif elapsed > timeout:
                    reason = "timeout exceeded"
                if elapsed >= next_update:
                    print(f"  Running {elapsed:.1f}s; sampled peak RSS {peak:.1f} MiB", flush=True)
                    next_update = elapsed + 15
                if reason:
                    process.terminate()
                    try:
                        process.wait(timeout=3)
                    except subprocess.TimeoutExpired:
                        process.kill()
                        process.wait()
                    break
                sleep(0.1)
            process.wait()
        finally:
            # A monitoring error or interruption must not leave a large
            # parser running without its resource guard.
            if process.poll() is None:
                process.terminate()
                try:
                    process.wait(timeout=3)
                except subprocess.TimeoutExpired:
                    process.kill()
                    process.wait()
    return {
        "status": "stopped" if reason else "completed" if process.returncode == 0 else "failed",
        "stop_reason": reason, "exit_code": process.returncode,
        "elapsed_seconds": round(perf_counter() - started, 3),
        "sampled_peak_rss_mib": round(peak, 1) if observed_rss else None,
        "lowest_system_free_percent": lowest_free,
    }


def validate(path, output, work_dir, timeout=300, rss_limit_mib=6144, minimum_free=15):
    import bs4
    import lxml.etree
    import soupsieve

    path, output, work_dir = path.resolve(), output.resolve(), work_dir.resolve()
    work_dir.mkdir(parents=True, exist_ok=True)
    output.parent.mkdir(parents=True, exist_ok=True)
    print("Fingerprinting input with the incremental reference scanner...", flush=True)
    source_hash = file_hash(path)
    reference = fingerprint(path)
    report = {
        "run_at": datetime.now(ZoneInfo("America/Los_Angeles")).isoformat(),
        "python": platform.python_version(), "platform": platform.platform(),
        "bs4": bs4.__version__, "soupsieve": soupsieve.__version__,
        "lxml": lxml.etree.LXML_VERSION, "libxml": lxml.etree.LIBXML_VERSION,
        "input": path.name, "input_bytes": path.stat().st_size,
        "input_sha256": source_hash, "parser": "html.parser", "repeats": 1,
        "limits": {"rss_mib": rss_limit_mib, "timeout_seconds_per_application": timeout,
                   "minimum_system_free_percent": minimum_free},
        "timing_scope": "Entire actual CLI process: startup, reading, parsing, query/replacement, output writing, and monitoring; reference verification excluded.",
        "memory_scope": "Sampled child process RSS every approximately 0.1 seconds; process-wide peak may be higher. System free percentage checked approximately every two seconds on macOS.",
        "reference": reference, "runs": [], "comparisons": [],
    }

    def save():
        output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")

    save()
    for task in (2, 3, 4, 6):
        task_runs = []
        for milestone in ("m1", "m2"):
            label = f"{milestone}-task{task}"
            stdout, stderr = work_dir / f"{label}.stdout.txt", work_dir / f"{label}.stderr.txt"
            markup = work_dir / f"{label}.html"
            command = [sys.executable, str(ROOT / "apps" / milestone / f"task{task}.py"), str(path), "--parser", "html.parser"]
            if task == 6:
                command.extend(["-o", str(markup)])
            print(f"Starting {label} on {path.stat().st_size:,} bytes", flush=True)
            result = guarded_run(command, stdout, stderr, timeout, rss_limit_mib, minimum_free)
            result.update({"milestone": milestone, "task": task,
                           "stderr": stderr.read_text(encoding="utf-8", errors="replace")})
            if result["status"] == "completed":
                actual = markup if task == 6 else stdout
                result.update({"output_bytes": actual.stat().st_size, "output_sha256": file_hash(actual)})
                if task == 6:
                    actual_reference = fingerprint(actual, normalize_replacements=True)
                    valid = (actual_reference["structure_sha256"] == reference["structure_sha256"]
                             and actual_reference["non_whitespace_text_sha256"] == reference["non_whitespace_text_sha256"]
                             and actual_reference["tag_counts"].get("b", 0) == 0
                             and actual_reference["tag_counts"].get("blockquote", 0) == reference["tag_counts"].get("b", 0))
                    result["output_fingerprint"] = actual_reference
                else:
                    valid = result["output_sha256"] == reference["task_output_sha256"][str(task)]
                result["verification"] = "passed" if valid else "failed"
            else:
                result["verification"] = "not completed"
            report["runs"].append(result)
            task_runs.append(result)
            save()
            print(f"{label}: {result['status']}; {result['elapsed_seconds']:.3f}s; verification {result['verification']}", flush=True)
        first, second = task_runs
        comparable = all(run["status"] == "completed" for run in task_runs)
        left = work_dir / (f"m1-task{task}.html" if task == 6 else f"m1-task{task}.stdout.txt")
        right = work_dir / (f"m2-task{task}.html" if task == 6 else f"m2-task{task}.stdout.txt")
        report["comparisons"].append({"task": task, "comparable": comparable,
                                       "byte_for_byte_identical": files_equal(left, right) if comparable else None})
        save()
    report["input_unchanged"] = file_hash(path) == source_hash
    report["all_passed"] = (report["input_unchanged"]
                            and all(run["verification"] == "passed" for run in report["runs"])
                            and all(row["byte_for_byte_identical"] for row in report["comparisons"]))
    save()
    print(f"Saved {output}; all passed: {report['all_passed']}", flush=True)
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path)
    parser.add_argument("--output", type=Path, default=Path("apps/m2/validation-gb.json"))
    parser.add_argument("--work-dir", type=Path, default=Path("apps/m2/generated/gb-results"))
    parser.add_argument("--timeout", type=float, default=300)
    parser.add_argument("--rss-mib", type=float, default=6144)
    parser.add_argument("--minimum-free-percent", type=int, default=15)
    args = parser.parse_args()
    if args.timeout <= 0 or args.rss_mib <= 0 or not 0 <= args.minimum_free_percent <= 100:
        parser.error("timeout/RSS must be positive and free percent must be between 0 and 100")
    result = validate(args.input, args.output, args.work_dir, args.timeout, args.rss_mib, args.minimum_free_percent)
    if not result["all_passed"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
