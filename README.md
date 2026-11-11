# BeautifulSoup — Milestone 3

`SoupReplacer` accepts functions that transform tags while BeautifulSoup parses HTML or XML. The two-name form from Milestone 2 is still available.

## Setup, test, and build

Use Python 3.10.13 or 3.11.5 with the pinned dependencies.

```sh
git clone https://github.com/Rathish-Rajendran/beautifulsoup.git
cd beautifulsoup
git checkout milestone-3
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements-dev.txt -e .
python -m pytest -q bs4/tests/test_m3_replacer.py  # Six Milestone 3 cases
python -m pytest -q                            # Full suite
./build.sh                                     # Package output in dist/
```

## Run Task 7

```sh
python apps/m3/task7.py apps/m2/fixtures/example.html -o /tmp/m3-result.html
```

The script sets `class="test"` on each `<p>` during parsing and saves the document. It accepts HTML or XML.

[Milestone 3 API brief](apps/m3/M3-README.md) · [Milestone 2 release](https://github.com/Rathish-Rajendran/beautifulsoup/releases/tag/milestone-2) · [MIT license](LICENSE)
