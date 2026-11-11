# Milestone 3 — SoupReplacer API brief

Milestone 2's `SoupReplacer("b", "blockquote")` is easy to read and is sufficient for a fixed rename. Milestone 3 lets the caller supply functions that make decisions using the current tag's name, attributes, or contents.

I recommend keeping the two-name form for fixed renames and offering the name and attribute callbacks for conditional rules. They return a value, so callers can tell which part of the tag the rule will change. Reserve the in-place callback for rules that need to edit contents or make several related changes. Its effects depend on the body of the function, so call order matters.

| Argument | Callback contract |
| --- | --- |
| `name_xformer` | Return the tag's new name or its current name. |
| `attrs_xformer` | Return the entire attribute mapping. Return `tag.attrs` to keep it. |
| `xformer` | Edit the completed tag in place and return `None`. |

The library calls these functions as each tag closes, after its children are parsed. When all three are supplied, it applies the name, then the attributes, then the in-place edit. This keeps the parser's closing-tag matching based on the source names and avoids a separate search of the completed tree. The two-name form and callback form are separate ways to configure the replacer. Both work with `html.parser` and lxml (HTML/XML).

## Task 7

`task7.py` uses `attrs_xformer` to set `class="test"` on every `<p>` while preserving its other attributes. It writes the whole modified document to the output path. Without `-o`, it writes beside the input with `.test-class` added before the extension.

```sh
python apps/m3/task7.py input.html -o result.html
```
