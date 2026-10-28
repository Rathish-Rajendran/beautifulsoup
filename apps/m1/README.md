# BeautifulSoup — Milestone 1

## Setup and usage

Prerequisites: Python and `uv` installed. Tested with Python 3.14.5,
BeautifulSoup 4.15.0, and lxml 6.1.3.

If `uv` is not installed, use its [official installer](https://docs.astral.sh/uv/getting-started/installation/)
on macOS/Linux:

```sh
curl -LsSf https://astral.sh/uv/install.sh | sh
```

Restart the terminal, then confirm installation with `uv --version`.

Run these commands from the directory containing `Milestone-1`.
Create the environment and install dependencies once:

```sh
uv venv --python 3.14.5 .venv
uv pip install --python .venv/bin/python beautifulsoup4==4.15.0 lxml==6.1.3
```

In each new terminal session, activate the environment and verify the imports:

```sh
source .venv/bin/activate
python -c "import bs4, lxml; print('Dependencies ready')"
```

Test files are excluded from the submission. Supply your own HTML/XML file,
replacing the placeholder paths below with its actual location:

```sh
python Milestone-1/task1.py "/path/to/input.html"
python Milestone-1/task1.py "/path/to/input.xml"
```

Run `deactivate` when finished. The `.venv` directory is kept outside
`Milestone-1`.

Each script accepts an HTML/XML input filename. Replace `task1.py` with the
required task. HTML uses `html.parser`; `.xml` files use `xml` (provided by
lxml). Use `--parser xml` or `--parser html.parser` to override the choice.

| Script | Behavior |
| --- | --- |
| `task1.py` | Parse the input and save prettified markup with `prettify()`. |
| `task2.py` | Print hyperlink destinations (`href` values). |
| `task3.py` | Print each element's name as `<tagname>`, once per element. |
| `task4.py` | Print tag names and IDs using one search: `find_all(id=True)`. |
| `task5.py` | Use `find_parent(id=True)` to identify each hyperlink's nearest ancestor with an ID. |
| `task6.py` | Rename all `<b>` elements to `<blockquote>` and save. |
| `task7.py` | Set every `<p>` element's class to `test`, replacing existing classes, and save. |
| `task8.py` | Exercise `select()` to list headings `<h1>` through `<h6>` and their text. |

Tasks 1, 6, and 7 save beside the input with suffixes `.pretty`, `.blockquote`,
and `.test-class`, respectively. Use `-o` to choose another destination:

```sh
python Milestone-1/task7.py "/path/to/input.html" -o "/path/to/paragraphs.html"
```

Output directories must already exist. Inputs are preserved; existing separate
output files are overwritten. The table below documents the files tested locally.

## Test files and completion times

Tested **17 files**: 11 public downloads (linked below), two original examples,
and four generated stress files. All listed runs passed. Times are total program-run
seconds; ranges show the fastest and slowest of Tasks 1–8 on each file.

| Input | Tasks run | Time (seconds) |
| --- | --- | ---: |
| [w3schools-note.xml](https://www.w3schools.com/xml/note.xml) | 1–8 | 0.105–0.114 |
| [w3schools-menu.xml](https://www.w3schools.com/xml/simple.xml) | 1–8 | 0.105–0.121 |
| [w3schools-books.xml](https://www.w3schools.com/xml/books.xml) | 1–8 | 0.105–0.120 |
| [w3c-xml-namespace.xml](https://www.w3.org/2001/xml.xsd) | 1–8 | 0.105–0.111 |
| [python-library.html](https://docs.python.org/3/library/index.html) | 1–8 | 0.105–0.110 |
| [python-functions.html](https://docs.python.org/3/library/functions.html) | 1–8 | 0.211–0.218 |
| [python-tutorial.html](https://docs.python.org/3/tutorial/index.html) | 1–8 | 0.104–0.110 |
| [beautifulsoup-docs.html](https://www.crummy.com/software/BeautifulSoup/bs4/doc/) | 1–8 | 0.214–0.218 |
| [lxml-tutorial.html](https://lxml.de/tutorial.html) | 1–8 | 0.213–0.221 |
| [python-pathlib.html](https://docs.python.org/3/library/pathlib.html) | 1–8 | 0.213–0.246 |
| [python-argparse.html](https://docs.python.org/3/library/argparse.html) | 1–8 | 0.210–0.219 |
| `small.html` | 1–8 | 0.072–0.131 |
| `small.xml` | 1–8 | 0.069–0.077 |
| `deeply-nested.html` | 1–8 | 0.105–0.110 |
| `medium-1MiB.html` | 1–8 | 0.106–0.110 |
| `large-16MiB.html` | 1–8 | 0.428–0.555 |
| `very-large-1GiB.html` | 1–8 | 23.055–35.456 |

The nested input has 600 nested `<div>` elements (maximum depth 606).
Individual timings for the 1 GiB input are listed below.

## GB-scale processing result

On October 13, 2026, **all eight tasks completed successfully on the same
1 GiB HTML input (1,073,741,824 bytes)** using `html.parser`. All outputs
passed verification, and the input remained unchanged.

Sample command for your own GB-scale input, with the environment activated:

```sh
python Milestone-1/task1.py "/path/to/large.html" -o "/path/to/large.pretty.html"
```

This runs Task 1 directly; the recorded runs used an external monitor to apply
the resource limits below.

| Task | Total run time (seconds) |
| --- | ---: |
| 1 | 35.456 |
| 2 | 23.055 |
| 3 | 23.510 |
| 4 | 24.844 |
| 5 | 27.204 |
| 6 | 33.848 |
| 7 | 33.251 |
| 8 | 24.696 |

Times include startup, processing, output I/O, and monitoring; verification
time is excluded. Each task had a 6 GiB sampled RSS guard, a 180-second timeout,
and a stop if the system's reported memory-free percentage fell below 15%.
No guard triggered. These are single-run results for this generated input.
