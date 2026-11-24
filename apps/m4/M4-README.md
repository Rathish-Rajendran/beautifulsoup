# Milestone 4 — Iterating over a Beautiful Soup document

Use `for node in soup` to walk a parsed HTML or XML document in document order.
The iterator visits each tag before its children and yields the original node
objects, including text, comments, and doctypes present in the parse tree.
An empty document yields zero nodes.

```python
from bs4 import BeautifulSoup

soup = BeautifulSoup("<p>Hello <b>world</b></p>", "html.parser")
for node in soup:
    print(type(node).__name__, repr(str(node)))
```

```text
Tag '<p>Hello <b>world</b></p>'
NavigableString 'Hello '
Tag '<b>world</b>'
NavigableString 'world'
```

`BeautifulSoup.__iter__` returns a fresh `descendants` generator each time.
The generator starts at the document's first child and follows `next_element`
links in the existing tree. Traversal takes linear time in the number of visited
nodes and uses constant extra space, with no list of traversal results. The
constructor builds the parse tree before iteration begins.

Use `soup.children` when you only want the document's direct children. Iterating
over an individual `Tag`, such as `soup.p`, still yields its direct children.

Run the five milestone tests from the repository root.

```sh
python -m pytest bs4/tests/test_m4_iteration.py
```
