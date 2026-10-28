# BeautifulSoup — Milestone 2

This project extends BeautifulSoup 4.13.0 with `SoupReplacer` to rename tags during parsing.

## Setup

Use Python **3.10.13 or 3.11.5** with the supplied dependencies for reproducible tests.

```sh
git clone https://github.com/Rathish-Rajendran/beautifulsoup.git
cd beautifulsoup
git checkout milestone-2
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements-dev.txt -e .
```

## Test and build

```sh
python -m pytest -q
./build.sh
```

Verified result: **911 passed, 7 existing upstream skips**. Build output is in `dist/`.

## Run the applications

```sh
python apps/m2/task2.py apps/m2/fixtures/example.html
python apps/m2/task3.py apps/m2/fixtures/example.html
python apps/m2/task4.py apps/m2/fixtures/example.html
python apps/m2/task6.py apps/m2/fixtures/example.html -o /tmp/m2-result.html
```

Each script accepts an HTML/XML input path. XML files use the XML parser automatically.
Task 6 saves the modified document; the input is preserved.

[apps/m2/M2-README.md](apps/m2/M2-README.md) contains the required source locations,
implementation explanation, test cases, and 1 GiB test result.

Submit the [Milestone 2 release](https://github.com/Rathish-Rajendran/beautifulsoup/releases/tag/milestone-2).
The same repository will be used for later milestones with separate tags/releases.

Original BeautifulSoup attribution and [MIT license](LICENSE) are preserved.
