Milestone 2 extends the supplied BeautifulSoup 4.13.0 source with `SoupReplacer(og_tag, alt_tag)` and the optional BeautifulSoup `replacer` argument. Tags are renamed in existing parser close events, preserving nesting and avoiding a post-parse replacement search/list.

Included deliverables:

- SoupStrainer applications for tasks 2, 3, and 4, and a SoupReplacer task 6 application.
- Original API source locations linked to the unchanged `canvas-baseline` tag.
- 58 API test instances, 14 CLI tests, and 10 validation-harness tests; full local suite: **911 passed, 7 existing upstream skips**.
- Reproducible **1 GiB** stress validation: all four M2 applications completed on 1,073,741,824 bytes / 334,252 tags, matched M1 output byte for byte, and passed independent incremental checks. All 65,220 bold elements were replaced. No resource guard triggered.
- Repeated 16 MiB comparison benchmark plus raw timing, memory, and input/output hashes for both sizes.
- Resource-monitored GB validator with chunked output comparisons, timeout/RSS guards, and cleanup tests; the generated GB input/output files remain local.
- Build script, development requirements, installable wheel/source archive, and CI for Python 3.10.13/3.11.5.

Start with the root README and `apps/m2/M2-README.md`. Supported replacement backends are html.parser and lxml HTML/XML; using html5lib with a replacer raises an explicit error. Task 3's all-tag strainer retains the full tree, and the measured task 6 timing is essentially equal to the post-parse baseline; the implementation removes the redundant scan and match list.

Repository: [Rathish-Rajendran/beautifulsoup](https://github.com/Rathish-Rajendran/beautifulsoup).
The public repository name, visibility, and source layout match the assignment setup. The detailed requirement review is in `apps/m2/COMPLIANCE.md`.
