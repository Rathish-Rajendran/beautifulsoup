# Milestone 2

This document answers Parts 1–3 and maps the submission to the rubric.
The root [README](../../README.md) contains installation, build, and run commands.

## Part 1: SoupStrainer applications

- **Task 2:** `SoupStrainer("a", href=True)` retains hyperlink subtrees while
  parsing. `find_all("a", href=True)` then prints destinations in document order,
  preserving Milestone 1 behavior, including empty href values and excluding
  placeholder anchors with no href.
- **Task 3:** `SoupStrainer(True)` is the requested attempt to keep every tag.
  This accepts outermost elements and therefore their entire subtrees. It cannot
  save meaningful tree memory or skip their text. Dropping any tag would make
  the output incomplete. Use full parsing for this use case in practice.
- **Task 4:** `SoupStrainer(id=True)` retains ID-bearing subtrees. A single
  `find_all(id=True)` call selects output elements and excludes retained descendants
  without IDs. Presence includes `id=""`. IDs are escaped for readable output.

A SoupStrainer selects **subtrees**, not an independent flat set of matching nodes.
Once an ancestor is accepted, descendants remain, even if they do not match.
The follow-up queries in tasks 2 and 4 are consequently necessary. Filtering saves
node construction and memory, but the underlying parser still reads/tokenizes the
input; this API is not a bounded-memory stream. In particular, BeautifulSoup reads
an input file handle in full before parsing it. `html5lib` does not honor parse_only,
so these applications deliberately offer compatible parsers only.

The handout says “two application programs” and also requests task 3 separately.
All three requested files (`task2.py`, `task3.py`, `task4.py`) are included.

## Large-file validation

Generate the exact deterministic 16 MiB input and rerun the experiment from the
repository root, after activating the environment:

```sh
python apps/m2/generate_large_input.py apps/m2/generated/large-16MiB.html
python apps/m2/validate_large.py apps/m2/generated/large-16MiB.html
```

The generator includes 15,770 sections, nested bold elements, sparse hyperlinks,
and sparse IDs, with 40,416 total tags. This is a tag-rich case, rather than a large
file consisting almost entirely of one text node. Generated inputs are ignored by
Git; [validation.json](validation.json) stores every raw run and result hash.

Recorded on October 27, 2026 (America/Los_Angeles), Python 3.11.5, BeautifulSoup
4.13.0 course source, lxml 5.3.2, macOS arm64; parser: `html.parser`.
Input size: **16,777,216 bytes**. Input SHA-256:
`1dcfc307c4a7998de67e219a20c53abf10f25446fd1aa5f7796cad25ff0dd9e5`.
Each mode ran three times in fresh subprocesses, alternating full and M2 modes.

| Task | Mode | Median construction seconds | Max process RSS MiB | Retained tags | Matches |
| --- | --- | ---: | ---: | ---: | ---: |
| 2 | Full parse / M1 style | 0.4320 | 139.0 | 40,416 | 493 |
| 2 | M2 | 0.2324 | 67.8 | 986 | 493 |
| 3 | Full parse / M1 style | 0.4218 | 138.8 | 40,416 | 40,416 |
| 3 | M2 | 0.4157 | 138.8 | 40,416 | 40,416 |
| 4 | Full parse / M1 style | 0.4183 | 138.3 | 40,416 | 247 |
| 4 | M2 | 0.2439 | 68.5 | 1,482 | 247 |
| 6 | Full parse / M1 style | 0.4259 | 196.7 | 40,416 | 7,886 |
| 6 | M2 | 0.4242 | 196.3 | 40,416 | 7,886 |

Construction timing includes reading and parsing; for baseline task 6 it also
includes the post-parse `find_all("b")` and rename loop. It excludes process startup,
query/output verification, and serialization. RSS is the maximum for the whole
worker process, including subsequent query/serialization, not just tree storage.
Task 6 includes serialization of the full document when measuring process RSS.

Tasks 2 and 4 clearly reduced retained nodes and memory on this input. Task 3
retained exactly the same tree. Task 6 timings are effectively equal within normal
noise; the measured result does **not** establish a substantial wall-clock speedup.
The algorithmic improvement is removal of a redundant tree scan and O(K) temporary
match list, where K is the number of renamed tags. Both approaches still require
O(N) parsing and storage of the full resulting tree. The replacer adds O(1) state
per soup and O(1) replacement work per close event (treating name lengths as bounded).

Beyond the timed in-process API comparisons, the validator executes all four actual
M1/M2 application pairs against the large input and checks **byte-for-byte identical
output**, including the saved task 6 document. All passed, and the input hash stayed
unchanged. Milestone 2 asks for large-file validation; it does not add a new GB-scale
requirement. The earlier 1 GiB Milestone 1 results remain in `apps/m1/README.md`.

## Part 2: original API locations

Every location below refers to **unmodified course source**, tagged
[`canvas-baseline`](https://github.com/Rathish-Rajendran/SWE262P_Project/tree/canvas-baseline)
(commit `0c57a7b`), before any M2 implementation changes. All 32 original `bs4`
Python files at that tag match the supplied `beautifulsoup.zip` byte for byte.
The prior Milestone 1 runtime used an installed 4.15.0 distribution; the assignment
asks for locations in the supplied 4.13.0 source, which is what this table records.

| Used API / operation | Original definition | Used by |
| --- | --- | --- |
| `BeautifulSoup(...)` / constructor | [`bs4/__init__.py:209`](https://github.com/Rathish-Rajendran/SWE262P_Project/blob/canvas-baseline/bs4/__init__.py#L209), class at 133 | Every M1 and M2 app |
| `soup.prettify()` (`Tag.prettify`) | [`bs4/element.py:2601`](https://github.com/Rathish-Rajendran/SWE262P_Project/blob/canvas-baseline/bs4/element.py#L2601) | M1 task 1 |
| `soup.find_all(...)` (`Tag.find_all`) | [`bs4/element.py:2715`](https://github.com/Rathish-Rajendran/SWE262P_Project/blob/canvas-baseline/bs4/element.py#L2715) | M1 tasks 2–7; M2 tasks 2–4 |
| `tag.find_parent(id=True)` (`PageElement.find_parent`) | [`bs4/element.py:992`](https://github.com/Rathish-Rajendran/SWE262P_Project/blob/canvas-baseline/bs4/element.py#L992) | M1 task 5 |
| `tag.get_text(" ", strip=True)` (`PageElement.get_text`) | [`bs4/element.py:524`](https://github.com/Rathish-Rajendran/SWE262P_Project/blob/canvas-baseline/bs4/element.py#L524) | M1 tasks 5 and 8 |
| `soup.select(...)` (`Tag.select`) | [`bs4/element.py:2799`](https://github.com/Rathish-Rajendran/SWE262P_Project/blob/canvas-baseline/bs4/element.py#L2799) | M1 task 8; delegates to `CSS.select`, `bs4/css.py:161`, then SoupSieve |
| `tag["href"]`, `tag["id"]` (`Tag.__getitem__`) | [`bs4/element.py:2203`](https://github.com/Rathish-Rajendran/SWE262P_Project/blob/canvas-baseline/bs4/element.py#L2203) | M1 tasks 2, 4, 5; M2 tasks 2, 4 |
| `tag["class"] = "test"` (`Tag.__setitem__`) | [`bs4/element.py:2223`](https://github.com/Rathish-Rajendran/SWE262P_Project/blob/canvas-baseline/bs4/element.py#L2223) | M1 task 7 |
| `tag.name` / `tag.name = "blockquote"` | [`bs4/element.py:1740`](https://github.com/Rathish-Rajendran/SWE262P_Project/blob/canvas-baseline/bs4/element.py#L1740); ordinary field, initialized at 1648 in `Tag.__init__` (1618) | M1 tasks 3–8 as relevant; M2 tasks 3, 4 |
| `str(soup)` (`Tag.__str__`) | [`bs4/element.py:2302`](https://github.com/Rathish-Rajendran/SWE262P_Project/blob/canvas-baseline/bs4/element.py#L2302), alias to `Tag.__repr__` at 2298 | M1 tasks 6, 7; M2 task 6 |
| `SoupStrainer(...)` / constructor | [`bs4/filter.py:345`](https://github.com/Rathish-Rajendran/SWE262P_Project/blob/canvas-baseline/bs4/filter.py#L345), class at 313 | M2 Part 1 tasks 2, 3, 4 |
| `FeatureNotFound` (imported/caught exception) | [`bs4/exceptions.py:10`](https://github.com/Rathish-Rajendran/SWE262P_Project/blob/canvas-baseline/bs4/exceptions.py#L10) | All apps' parser error handling |

Supporting internal calls: `find_parent` delegates to `PageElement.find_parents`
at `bs4/element.py:1022`; `Tag.__repr__` calls `decode` (`Tag.decode` at
`bs4/element.py:2334`, overridden by `BeautifulSoup.decode` at `bs4/__init__.py:1073`).
Parsing consults `SoupStrainer.allow_tag_creation` at `bs4/filter.py:580`, from
`BeautifulSoup.handle_starttag` at `bs4/__init__.py:987` (original locations).
`Path.open`, `Path.write_text`, `argparse`, and `html.escape` are standard Python
APIs, not BeautifulSoup definitions. The new `SoupReplacer` has no original-source
location because it is introduced in M2.

## Part 3: SoupReplacer design

Public API:

```python
from bs4 import BeautifulSoup, SoupReplacer
b_to_blockquote = SoupReplacer("b", "blockquote")
soup = BeautifulSoup(html_doc, "html.parser", replacer=b_to_blockquote)
print(soup.prettify())
```

### How it works

1. `bs4/replacer.py` defines `SoupReplacer`, validates two nonempty local tag-name
   strings, and implements `replace(tag)` as an in-place name comparison/assignment.
   The object stores only the two names and can be reused between documents.
2. `bs4/__init__.py` exports the class and adds optional `replacer=None` after
   existing positional constructor parameters, preserving their order. The
   constructor validates/stores it rather than forwarding it to the tree builder.
3. Existing parsers build nodes with their original names. When `popTag()` closes
   a node, it first updates the original-name counters and whitespace/string stacks.
   It then calls the replacer on that just-completed tag. No replacement traversal
   or collection of matching nodes is introduced.
4. This hook executes during `builder.feed()` for explicit/implicit closing events
   and during `_feed()` cleanup for any tags left unclosed at EOF. A test observes
   a replacement before `builder.feed()` returns and makes any `find_all` call fail.
5. Task 6 supplies `SoupReplacer("b", "blockquote")` to the constructor and writes
   the tree. Serialization still visits the tree, as any file-writing app must.

### Why close events

Renaming an open `<b>` immediately would leave `</b>` looking for an open name that
no longer exists. Nested tags and following siblings could be attached incorrectly,
and special tags could lose whitespace/string behavior. Closing first lets existing
parser bookkeeping finish with the source name. The result is equivalent to the
M1 `tag.name` assignment, while avoiding M1's extra search after construction.
Attributes, children, object identity, namespace URI/prefix, and structural links
remain unchanged. Parser-normalized names are matched exactly (normally lowercase
for HTML, case-sensitive for XML); namespace matching uses the local name.

### Scope and compatibility

- Supported: `html.parser`, lxml HTML, and lxml XML (`xml` / `lxml-xml` in the library).
- `html5lib` reconstructs nodes via its own tree adapter rather than `popTag()`;
  using it with a replacer raises `ValueError` instead of silently doing nothing.
  Existing html5lib calls without a replacer continue to pass upstream tests.
- `SoupStrainer` matches source names, and replacement applies to retained nodes.
- Replacements rename nodes; they do not re-tokenize markup according to the new
  name, change namespace bindings, or reinterpret void/raw-text semantics. This
  matches the M1 post-parse rename contract.
- Omitting the argument leaves previous behavior intact. Copy/deepcopy and pickle
  are covered. Names containing prefixes/markup delimiters and non-string values
  are rejected. Pass `"b"`, not `"<b>"` or `"x:b"`.
- Attribute callbacks and task 7's `class="test"` transformation belong to M3.

## Tests and build

`python -m pytest -q` reports **901 passed, 7 skipped** in the recorded local run.
The original suite contributes 829 passes and seven existing skips; M2 contributes
58 API test instances and 14 application tests.

The two explicitly requested new cases are
`test_replaces_all_b_tags` and `test_nested_replacements_keep_closing_tags_and_siblings`,
each exercised on three parsers. Additional cases cover preservation of nonmatches,
empty/self-closing nodes, unfinished/malformed markup, XML namespaces and case,
raw-text/whitespace tags, strainer composition, reuse, defaults, validation, copies,
and the supported-backend boundary. CLI tests compare against the preserved M1
programs and cover escaping, missing inputs, module invocation, and input alias safety.

`./build.sh` uses the existing Hatch/PEP 517 project to create a wheel and source
archive. The source archive includes the milestone apps, fixtures, requirements,
validation record, and documentation. CI repeats tests/build and installs the wheel
outside the checkout to ensure the new module is actually packaged.

## Rubric checklist

| Criterion | Points | Evidence |
| --- | ---: | --- |
| Completeness | 5 | Three Part 1 programs, all original API locations, SoupReplacer and constructor integration, required cases plus edge tests, task 6 app |
| Correctness | 50 | Full suite passes; HTML/XML app comparisons; all four actual CLI outputs verified on 16 MiB input |
| Performance | 40 | Existing close-event hook; no new tree walk or O(K) replacement list; structural proof and candid timing/memory measurements |
| Build | 5 | Executable `build.sh`, reproducible requirements, wheel/sdist build and install verification, CI |

Submit the `milestone-2` release/tag link listed in the root README. This repository
uses the owner-requested private name `SWE262P_Project`; the handout's suggested
name was `beautifulsoup`. The private repository needs grader access.
