# Milestone 2

See the root [README](../../README.md) for installation, application commands, tests, and build.

## Part 1: SoupStrainer applications

| File | Implementation |
| --- | --- |
| `task2.py` | Uses `SoupStrainer("a", href=True)` to retain hyperlink subtrees and prints their destinations. |
| `task3.py` | Attempts `SoupStrainer(True)` and prints every tag. Because all tags are needed, the full tree is retained and filtering provides no reduction. |
| `task4.py` | Uses `SoupStrainer(id=True)` and one `find_all(id=True)` call to print elements with IDs. |

SoupStrainer retains matching subtrees, including their descendants. Tasks 2 and 4
therefore filter the retained tree again when selecting output elements.

### Large-file test

All three Part 1 applications, plus task 6, completed successfully on a **1 GiB
(1,073,741,824-byte) HTML file**. Their outputs matched the corresponding Milestone 1
applications. Task 6 replaced every `<b>` element with `<blockquote>`.

| Application | Total elapsed time | Result |
| --- | ---: | --- |
| Task 2 | 7.028 seconds | Passed |
| Task 3 | 10.325 seconds | Passed |
| Task 4 | 7.953 seconds | Passed |
| Task 6 | 18.699 seconds | Passed |

Times are from one local run per application and include reading and writing files.
Recreate the input, then use its path with the application commands in the root README:

```sh
python apps/m2/generate_large_input.py apps/m2/generated/large-1GiB.html --mib 1024 --padding-words 1024
```

The generated large input is excluded from Git.

## Part 2: original API locations

These locations refer to the original supplied source at the
[`canvas-baseline`](https://github.com/Rathish-Rajendran/beautifulsoup/tree/canvas-baseline)
tag, before Milestone 2 changes. Inherited methods are defined in `Tag` or `PageElement`.

| API used | Original definition | Application |
| --- | --- | --- |
| `BeautifulSoup(...)` | [`bs4/__init__.py:209`](https://github.com/Rathish-Rajendran/beautifulsoup/blob/canvas-baseline/bs4/__init__.py#L209) | All applications |
| `prettify()` | [`bs4/element.py:2601`](https://github.com/Rathish-Rajendran/beautifulsoup/blob/canvas-baseline/bs4/element.py#L2601) | M1 task 1 |
| `find_all(...)` | [`bs4/element.py:2715`](https://github.com/Rathish-Rajendran/beautifulsoup/blob/canvas-baseline/bs4/element.py#L2715) | M1 tasks 2–7; M2 tasks 2–4 |
| `find_parent(...)` | [`bs4/element.py:992`](https://github.com/Rathish-Rajendran/beautifulsoup/blob/canvas-baseline/bs4/element.py#L992) | M1 task 5 |
| `get_text(...)` | [`bs4/element.py:524`](https://github.com/Rathish-Rajendran/beautifulsoup/blob/canvas-baseline/bs4/element.py#L524) | M1 tasks 5 and 8 |
| `select(...)` | [`bs4/element.py:2799`](https://github.com/Rathish-Rajendran/beautifulsoup/blob/canvas-baseline/bs4/element.py#L2799) | M1 task 8 |
| `tag["href"]`, `tag["id"]` (`__getitem__`) | [`bs4/element.py:2203`](https://github.com/Rathish-Rajendran/beautifulsoup/blob/canvas-baseline/bs4/element.py#L2203) | M1 tasks 2, 4, 5; M2 tasks 2, 4 |
| `tag["class"] = ...` (`__setitem__`) | [`bs4/element.py:2223`](https://github.com/Rathish-Rajendran/beautifulsoup/blob/canvas-baseline/bs4/element.py#L2223) | M1 task 7 |
| `tag.name` / name assignment | [`bs4/element.py:1740`](https://github.com/Rathish-Rajendran/beautifulsoup/blob/canvas-baseline/bs4/element.py#L1740); initialized at 1648 | M1 tasks 3–6, 8; M2 tasks 3, 4 |
| `str(soup)` (`__str__`) | [`bs4/element.py:2302`](https://github.com/Rathish-Rajendran/beautifulsoup/blob/canvas-baseline/bs4/element.py#L2302), alias to `__repr__` at 2298 | M1 tasks 6, 7; M2 task 6 |
| `SoupStrainer(...)` | [`bs4/filter.py:345`](https://github.com/Rathish-Rajendran/beautifulsoup/blob/canvas-baseline/bs4/filter.py#L345) | M2 tasks 2, 3, 4 |
| `FeatureNotFound` exception | [`bs4/exceptions.py:10`](https://github.com/Rathish-Rajendran/beautifulsoup/blob/canvas-baseline/bs4/exceptions.py#L10) | Parser error handling |

## Part 3: SoupReplacer

```python
from bs4 import BeautifulSoup, SoupReplacer

replacer = SoupReplacer("b", "blockquote")
soup = BeautifulSoup("<b>A<b>B</b>C</b>", "html.parser", replacer=replacer)
print(soup.prettify())
```

`bs4/replacer.py` defines `SoupReplacer(og_tag, alt_tag)`. BeautifulSoup accepts it
through the optional `replacer` constructor argument.

Replacement happens in `BeautifulSoup.popTag()` as each tag closes during parsing,
including cleanup of unclosed tags at the end of input. The parser finishes its
bookkeeping with the original tag name before renaming the node. This preserves
nested closing-tag matching, attributes, children, and tree links.

The implementation uses existing parsing events and avoids the extra tree search
and temporary list used by a post-parse replacement loop. `task6.py` supplies the
replacer during construction and writes the resulting document.

Supported replacement parsers are `html.parser` and lxml HTML/XML. Using a replacer
with `html5lib` raises an explicit error. SoupStrainer matches original input names.

### Required new tests

The cases in [test_replacer.py](../../bs4/tests/test_replacer.py) include:

1. `test_replaces_all_b_tags`: every matching tag is renamed while attributes and children are preserved.
2. `test_nested_replacements_keep_closing_tags_and_siblings`: nested replacements retain the correct structure and following siblings.

Both cases run with html.parser, lxml HTML, and XML. Run all tests with
`python -m pytest -q` from the repository root.
