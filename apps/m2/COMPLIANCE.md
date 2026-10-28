# Milestone 2 requirement review

This review maps the Milestone 2 specification and rubric to the implementation
and verification evidence. Setup and application commands are in the root
[README](../../README.md); the Part 2 source table and Part 3 design explanation
are in [M2-README.md](M2-README.md).

## Required deliverables

| Requirement | Implementation and evidence |
| --- | --- |
| Repository named `beautifulsoup` | [Rathish-Rajendran/beautifulsoup](https://github.com/Rathish-Rajendran/beautifulsoup); the clone directory and local project directory are also named `beautifulsoup`. |
| Use the supplied BeautifulSoup source | Imported BeautifulSoup 4.13.0; all 32 original `bs4` Python files at `canvas-baseline` match the supplied ZIP byte for byte. |
| New library API inside `bs4/` | `bs4/replacer.py` defines `SoupReplacer`; `bs4/__init__.py` exports it and integrates it with construction. |
| New tests inside `bs4/tests/` | `test_replacer.py` contains 58 API test instances; `test_m2_apps.py` contains 14 application tests. |
| Application tasks inside `apps/m2/` | Separate `task2.py`, `task3.py`, `task4.py`, and `task6.py` files. |
| Milestone README inside `apps/m2/` | `M2-README.md` answers Parts 1–3, including the source locations and replacement implementation. |
| Root README explains installation and repository setup | Fresh clone, checkout, environment creation, dependencies, test, build, and application commands are included. |
| Submit a milestone tag/release | [milestone-2 release](https://github.com/Rathish-Rajendran/beautifulsoup/releases/tag/milestone-2); the tag identifies the submitted source revision and the release includes the wheel and source archive. |
| Reuse the repository for future milestones | The repository retains the original source history and a separate Milestone 2 tag. Later milestones can add their own tags without replacing this submission. |

## Part 1 — SoupStrainer applications

| Requirement | Implementation and evidence |
| --- | --- |
| Task 2 using SoupStrainer | `task2.py` constructs the soup with `parse_only=SoupStrainer("a", href=True)` and prints hyperlink destinations. |
| Task 3 using SoupStrainer | `task3.py` attempts `parse_only=SoupStrainer(True)` and prints every tag. The README explains why retaining all tags also retains the full tree. |
| Task 4 using SoupStrainer | `task4.py` constructs the soup with `parse_only=SoupStrainer(id=True)` and uses one `find_all(id=True)` call to select output elements. |
| Each application tested on a large HTML or XML file | All three applications were executed on a deterministic 16,777,216-byte HTML file and compared with the unchanged Milestone 1 applications. All output bytes match. |
| Explain filter behavior accurately | Accepted subtrees include descendants that may not match the strainer. Follow-up result queries exclude those descendants when necessary. The README records the all-tag limitation and full-input reading behavior. |

The large-file generator is committed instead of the generated 16 MiB file.
`generate_large_input.py` recreates it, and `validation.json` records its SHA-256,
input size, node counts, individual runs, memory measurements, and output hashes.

## Part 2 — original API definitions

The source table includes every BeautifulSoup API used by the Milestone 1 programs
and the Part 1 programs: the BeautifulSoup and SoupStrainer constructors,
`prettify`, `find_all`, `find_parent`, `get_text`, `select`, attribute indexing and
assignment, the `name` field, string serialization, and the imported parser
exception. Inherited methods are located in `Tag` or `PageElement`, as appropriate.

All file paths and line numbers refer to `canvas-baseline`, before the Milestone 2
changes. The links point to that tag so later line-number changes do not invalidate
the answers. Supporting delegation locations are also recorded. Standard Python
file and command-line APIs are identified separately from library APIs.

## Part 3 — SoupReplacer

| Requirement | Implementation and evidence |
| --- | --- |
| Object named `SoupReplacer` | Exported by `bs4`, supporting `from bs4 import SoupReplacer`. |
| Constructor `SoupReplacer(og_tag, alt_tag)` | Accepts two tag-name strings and stores the original and replacement names. The underscores are valid Python identifiers for the specification's `og-tag` and `alt-tag` notation. |
| Optional constructor argument to BeautifulSoup | `BeautifulSoup(..., replacer=SoupReplacer("b", "blockquote"))`; the default is `None`, and existing positional parameters retain their order. |
| Replace every occurrence of the original tag | Matching completed tags are renamed in place, including nested matches and tags completed during end-of-input cleanup. |
| Replacement during parsing | The existing `popTag()` close event invokes the replacer after original-name stack bookkeeping. There is no replacement search after parsing. |
| At least two new API test cases | `test_replaces_all_b_tags` and `test_nested_replacements_keep_closing_tags_and_siblings`, each parameterized over html.parser, lxml HTML, and XML. |
| Verify the parse-time performance benefit | A custom test builder observes a renamed node before `feed()` returns while `find_all` is patched to fail. This verifies the operation occurs inside construction without an added search. |
| Application implementing task 6 through the API | `task6.py` passes the replacer during construction and saves the modified document, without a rename loop or replacement search. Its output matches Milestone 1 on HTML, XML, and the 16 MiB HTML input. |

The implementation preserves node identity, attributes, children, namespace
prefixes/URIs, and tree links. It retains source names on the open-tag stack until
closure so original closing tags still match correctly.

The supported replacement parsers are html.parser and lxml HTML/XML. html5lib's
separate tree-reconstruction adapter is explicitly rejected when a replacer is
supplied. Ordinary html5lib parsing remains supported. The specification does not
require replacement support for every parser backend; this boundary is documented
and tested. Attribute and functional transformations are Milestone 3 work.

## Rubric evidence

| Criterion | Points | Verification |
| --- | ---: | --- |
| Completeness | 5 | Required applications, API integration, original-source answers, and new tests are present in the specified directories. |
| Correctness | 50 | Full local suite: 901 passed, seven pre-existing upstream skips. New cases cover nested/unfinished tags, XML, attributes, links, filtering, defaults, invalid inputs, copy/pickle, and CLI input preservation. |
| Performance | 40 | Replacement uses existing parser close events, eliminating the separate O(N) tree search and O(K) match list. The 16 MiB experiment reports actual measurements without promising a universal speedup. |
| Build | 5 | Executable `build.sh`, existing Hatch/PEP 517 configuration, pinned development dependencies, wheel/source archive, and CI build plus wheel-install verification. |

The reproducible test runtimes are Python 3.10.13 and 3.11.5 with lxml 5.3.2.
Newer Python patch releases and lxml 6 change behaviors expected by some original
tests; the README records this compatibility constraint. No original test is
modified or newly skipped to make the extension pass.

## Submission access

The repository is private. The grading account must have access to the repository
and release before the release URL is submitted on Canvas. The setup README's
GitHub CLI example uses public visibility; private visibility requires arranging
that access. Canvas submission is a separate step from publishing the release.
