"""Simple tag-name replacements performed while a parse tree is built."""

from bs4.element import Tag

__all__ = ["SoupReplacer"]


class SoupReplacer:
    """Rename every parsed ``og_tag`` to ``alt_tag`` in place.

    Pass an instance as ``BeautifulSoup(..., replacer=...)``. Names are
    matched exactly against parser-normalized local names: HTML parsers
    normally lowercase names, while XML names are case-sensitive. XML
    namespace URIs and prefixes, attributes, and children are preserved.

    This changes the resulting tree, not the parser's interpretation of
    the input. For example, renaming a tag to ``script`` does not turn its
    input contents into raw script text. An instance can be reused for
    independent parses; it holds no per-document state.
    """

    def __init__(self, og_tag: str, alt_tag: str):
        for argument, name in (("og_tag", og_tag), ("alt_tag", alt_tag)):
            if not isinstance(name, str):
                raise TypeError(f"{argument} must be a string")
            if (
                not name
                or name == "[document]"
                or any(char.isspace() or char in "<>/:\x00" for char in name)
            ):
                raise ValueError(f"{argument} must be a non-empty local tag name")
        self.og_tag = og_tag
        self.alt_tag = alt_tag

    og_tag: str
    alt_tag: str

    def replace(self, tag: Tag) -> None:
        """Rename a completed tag without changing its identity or contents."""
        if tag.name == self.og_tag:
            tag.name = self.alt_tag
