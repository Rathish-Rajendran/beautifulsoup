# BeautifulSoup — SWE262P Milestone 2

This project extends BeautifulSoup 4.13.0 with **`SoupReplacer(og_tag, alt_tag)`**.
Replacement happens while parsing, without a second tree search. Original code and
MIT attribution are preserved; this is a course extension, not an upstream release.

## Installation, tests, and build

Use Python **3.10.13 or 3.11.5** to reproduce the supplied source tests
(locally verified with 3.11.5). Let `python3` below name that interpreter.
From a fresh clone:

```sh
git clone https://github.com/Rathish-Rajendran/beautifulsoup.git
cd beautifulsoup
git checkout milestone-2
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements-dev.txt -e .
python -m pytest -q
./build.sh
```

Recorded local result: **901 passed, 7 skipped**; the seven skips are existing
upstream tests. The build produces a wheel and source archive under `dist/`.
For an explicit interpreter: `PYTHON=.venv/bin/python ./build.sh`.
The development requirements pin lxml 5.3.2 because lxml 6.1.3 changes three
behaviors expected by the unmodified course-source tests. CI checks Python 3.10.13
and 3.11.5, runs the suite, builds the package, and tests the wheel outside the
checkout. Newer Python patch releases change
malformed-declaration handling in `html.parser`, making three original rejection
tests fail; the exact runtime versions avoid that upstream test incompatibility.

## Run the required applications

```sh
python apps/m2/task2.py apps/m2/fixtures/example.html
python apps/m2/task3.py apps/m2/fixtures/example.html
python apps/m2/task4.py apps/m2/fixtures/example.html
python apps/m2/task6.py apps/m2/fixtures/example.html -o /tmp/m2-result.html
```

Each accepts an HTML/XML filename. `.xml` selects the XML parser automatically;
`--parser html.parser`, `--parser lxml`, and `--parser xml` override this.
The XML example is `apps/m2/fixtures/example.xml`. Input files are preserved.
Task 6 defaults to `INPUT_STEM.blockquote.INPUT_SUFFIX`; an existing separate
output file is overwritten. Parsing timings go to stderr, leaving task output clean.

| Requirement | Implementation / evidence |
| --- | --- |
| Part 1: filtered hyperlinks | [task2.py](apps/m2/task2.py), `SoupStrainer("a", href=True)` |
| Part 1: attempt all tags | [task3.py](apps/m2/task3.py), `SoupStrainer(True)`; full-tree limitation explained |
| Part 1: filtered ID elements | [task4.py](apps/m2/task4.py), `SoupStrainer(id=True)` |
| Large-file tests | [reproduction and measured results](apps/m2/M2-README.md#large-file-validation), [raw measurements](apps/m2/validation.json) |
| Part 2: original API locations | [original source table](apps/m2/M2-README.md#part-2-original-api-locations), stable `canvas-baseline` tag |
| Part 3: new library API | [SoupReplacer](bs4/replacer.py), integration in [BeautifulSoup](bs4/__init__.py) |
| Part 3: application | [task6.py](apps/m2/task6.py) |
| Required new API tests | [test_replacer.py](bs4/tests/test_replacer.py): 58 test instances, including the two required cases |
| Application correctness | [test_m2_apps.py](bs4/tests/test_m2_apps.py): 14 tests; actual M1/M2 HTML/XML output comparisons |
| Performance | Parser close-event hook; no new tree traversal or replacement match list; structural test and measured results |
| Build | [build.sh](build.sh), [pyproject.toml](pyproject.toml), [CI](.github/workflows/ci.yml) |

## API example

```python
from bs4 import BeautifulSoup, SoupReplacer

html = '<b id="outer">A<b>B</b>C</b><p>D</p>'
soup = BeautifulSoup(html, "html.parser", replacer=SoupReplacer("b", "blockquote"))
print(soup.prettify())
```

Names are replaced in place, preserving attributes, children, namespace prefixes,
and tree links. Nesting is preserved because original names remain on the parser's
open-tag stack until closure. Supported parsers: `html.parser`, `lxml`, and XML via
lxml. Supplying a replacer with `html5lib` raises a clear error because that builder
reconstructs trees outside this close-event interface. Ordinary html5lib parsing is
unchanged. `parse_only` filters original names before replacement.

The Milestone 3 callable/attribute transformations are outside this milestone.

## Submission and history

- Submit the [Milestone 2 release](https://github.com/Rathish-Rajendran/beautifulsoup/releases/tag/milestone-2).
- [Milestone 2 tag](https://github.com/Rathish-Rajendran/beautifulsoup/tree/milestone-2) fixes the graded source revision; future milestones use new tags.
- `canvas-baseline` contains the unmodified imported source. All 32 original `bs4`
  Python files were verified byte-for-byte against the supplied ZIP.
- `apps/m1/` preserves the previously implemented Milestone 1 programs unchanged.
- The repository is named **beautifulsoup**, matching the assignment. It is private;
  the grader must have repository access to open the submission link.

See [M2-README.md](apps/m2/M2-README.md) for the milestone answers and design details,
and [COMPLIANCE.md](apps/m2/COMPLIANCE.md) for the requirement-by-requirement review.
Upstream: [Beautiful Soup](https://www.crummy.com/software/BeautifulSoup/bs4/).
Original license: [LICENSE](LICENSE).
