Milestone 2 extends the supplied BeautifulSoup 4.13.0 source with `SoupReplacer(og_tag, alt_tag)` and the optional BeautifulSoup `replacer` argument. Tags are renamed in existing parser close events, preserving nesting and avoiding a post-parse replacement search/list.

Included deliverables:
- SoupStrainer applications for tasks 2, 3, and 4, and a SoupReplacer task 6 application.
- Original API source locations linked to the unchanged `canvas-baseline` tag.
- 58 API test instances and 14 CLI tests; full local suite: **901 passed, 7 existing upstream skips**.
- Reproducible 16 MiB experiments: all four actual M1/M2 application outputs are byte-for-byte identical. Raw timing, memory, and hashes are committed.
- Build script, development requirements, installable wheel/source archive, and CI for Python 3.10.13/3.11.5.

Start with the root README and `apps/m2/M2-README.md`. Supported replacement backends are html.parser and lxml HTML/XML; using html5lib with a replacer raises an explicit error. Task 3's all-tag strainer retains the full tree, and the measured task 6 timing is essentially equal to the post-parse baseline; the implementation removes the redundant scan and match list.

This repository is private and named SWE262P_Project as explicitly requested by its owner (the handout suggested beautifulsoup). Ensure the grader has repository access before submitting this release link.
