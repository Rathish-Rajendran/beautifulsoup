"""Compare full parsing with M2 on a large file in isolated subprocesses.

Reports construction time, process peak RSS, retained tags, result hashes,
and byte-for-byte equivalence of the actual M1/M2 command-line outputs.
"""

import argparse
import hashlib
import json
from pathlib import Path
import platform
import statistics
import subprocess
import sys
import tempfile
from time import perf_counter

if __package__:
    from . import _common
else:
    import _common
from bs4 import BeautifulSoup, SoupReplacer, SoupStrainer, __version__
from bs4.element import Tag

ROOT = Path(__file__).resolve().parents[2]


def file_hash(path):
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def worker(path, task, optimized, parser):
    kwargs = {}
    if optimized:
        if task == 6:
            kwargs["replacer"] = SoupReplacer("b", "blockquote")
        else:
            kwargs["parse_only"] = {
                2: SoupStrainer("a", href=True),
                3: SoupStrainer(True),
                4: SoupStrainer(id=True),
            }[task]
    started = perf_counter()
    with path.open("rb") as source:
        soup = BeautifulSoup(source, parser, **kwargs)
    if task == 6 and not optimized:
        matches = soup.find_all("b")
        for tag in matches:
            tag.name = "blockquote"
        del matches
    construction_seconds = perf_counter() - started

    # Measurements/verification below are outside the construction timer.
    digest = hashlib.sha256()
    if task == 6:
        digest.update(str(soup).encode("utf-8"))
        matches = len(soup.find_all("blockquote"))
    else:
        from html import escape
        tags = soup.find_all("a", href=True) if task == 2 else soup.find_all(True) if task == 3 else soup.find_all(id=True)
        matches = len(tags)
        for tag in tags:
            line = tag["href"] if task == 2 else f"<{tag.name}>" if task == 3 else f'<{tag.name} id="{escape(tag["id"], quote=True)}">'
            digest.update((line + "\n").encode("utf-8"))
    import resource
    peak = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    # macOS reports bytes; Linux reports KiB. Includes query/serialization.
    peak_mib = peak / (1024 * 1024 if sys.platform == "darwin" else 1024)
    return {
        "construction_seconds": construction_seconds,
        "peak_process_mib": peak_mib,
        "retained_tags": sum(isinstance(node, Tag) for node in soup.descendants),
        "matches": matches,
        "result_sha256": digest.hexdigest(),
    }


def validate_cli(path, parser):
    checks = []
    with tempfile.TemporaryDirectory(prefix="m2-cli-") as folder:
        folder = Path(folder)
        for task in (2, 3, 4, 6):
            outputs = []
            for milestone in ("m1", "m2"):
                output = folder / f"{milestone}-task{task}"
                command = [sys.executable, str(ROOT / "apps" / milestone / f"task{task}.py"), str(path), "--parser", parser]
                if task == 6:
                    command.extend(["-o", str(output)])
                    result = subprocess.run(command, capture_output=True, timeout=180)
                else:
                    with output.open("wb") as destination:
                        result = subprocess.run(command, stdout=destination, stderr=subprocess.PIPE, timeout=180)
                if result.returncode:
                    raise RuntimeError(result.stderr.decode("utf-8", "replace"))
                outputs.append(output)
            if outputs[0].read_bytes() != outputs[1].read_bytes():
                raise AssertionError(f"Task {task}: M1 and M2 output differs")
            checks.append({"task": task, "identical": True, "output_bytes": outputs[1].stat().st_size,
                           "output_sha256": file_hash(outputs[1])})
            print(f"Task {task}: actual CLI outputs identical", flush=True)
    return checks


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path)
    parser.add_argument("--parser", choices=("html.parser", "lxml", "xml"), default="html.parser")
    parser.add_argument("--repeats", type=int, default=3)
    parser.add_argument("--output", type=Path, default=Path("apps/m2/validation.json"))
    parser.add_argument("--worker", type=int, choices=(2, 3, 4, 6), help=argparse.SUPPRESS)
    parser.add_argument("--optimized", action="store_true", help=argparse.SUPPRESS)
    args = parser.parse_args()
    if args.worker:
        print(json.dumps(worker(args.input, args.worker, args.optimized, args.parser)))
        return
    if args.repeats < 1:
        parser.error("--repeats must be positive")
    path = args.input.resolve()
    initial_hash = file_hash(path)
    rows = []
    for task in (2, 3, 4, 6):
        measurements = {False: [], True: []}
        for _ in range(args.repeats):
            for optimized in (False, True):
                command = [sys.executable, str(Path(__file__).resolve()), str(path), "--worker", str(task), "--parser", args.parser]
                if optimized:
                    command.append("--optimized")
                result = subprocess.run(command, check=True, capture_output=True, text=True, timeout=180)
                measurements[optimized].append(json.loads(result.stdout))
        expected = measurements[False][0]["result_sha256"]
        for optimized, runs in measurements.items():
            if any(run["result_sha256"] != expected for run in runs):
                raise AssertionError(f"Task {task}: result mismatch")
            rows.append({
                "task": task, "mode": "m2" if optimized else "full_parse",
                "median_construction_seconds": statistics.median(run["construction_seconds"] for run in runs),
                "max_peak_process_mib": max(run["peak_process_mib"] for run in runs),
                "retained_tags": runs[0]["retained_tags"], "matches": runs[0]["matches"],
                "result_sha256": expected, "runs": runs,
            })
        print(f"Task {task}: {args.repeats} full/M2 pairs verified", flush=True)
    checks = validate_cli(path, args.parser)
    if file_hash(path) != initial_hash:
        raise AssertionError("Input changed during validation")
    import lxml.etree
    report = {
        "python": platform.python_version(), "platform": platform.platform(),
        "bs4": __version__, "lxml": lxml.etree.LXML_VERSION, "libxml": lxml.etree.LIBXML_VERSION,
        "input": path.name, "input_bytes": path.stat().st_size, "input_sha256": initial_hash,
        "parser": args.parser, "repeats": args.repeats,
        "timing_scope": "Read and construct tree, plus post-parse rename for baseline task 6; excludes query, serialization, startup.",
        "memory_scope": "Fresh process maximum RSS including query/serialization; not just tree memory.",
        "measurements": rows, "cli_checks": checks, "input_unchanged": True,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(f"Saved {args.output}")


if __name__ == "__main__":
    main()
