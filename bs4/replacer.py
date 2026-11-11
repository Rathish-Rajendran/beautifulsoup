"""Transform tags while a parse tree is built."""

from collections.abc import Callable, Mapping
from typing import Optional

from bs4._typing import _AttributeValue
from bs4.element import Tag

__all__ = ["SoupReplacer"]


def _validate_name(argument: str, name: object) -> None:
    if not isinstance(name, str):
        raise TypeError(f"{argument} must be a string")
    if (
        not name
        or name == "[document]"
        or any(char.isspace() or char in "<>/:\x00" for char in name)
    ):
        raise ValueError(f"{argument} must be a non-empty local tag name")


class SoupReplacer:
    """Pass to ``BeautifulSoup(..., replacer=...)`` to transform tags as they close.

    Supply a pair of local tag names for an exact rename, or supply keyword
    callbacks. Each callback receives the completed Tag. If supplied together,
    the name callback returns a name first, the attribute callback returns a
    complete mapping second, and the in-place callback runs last.
    """

    # Milestone 2 pickles store only the two tag names.
    xformer: Optional[Callable[[Tag], None]] = None

    def __init__(
        self,
        og_tag: Optional[str] = None,
        alt_tag: Optional[str] = None,
        *,
        name_xformer: Optional[Callable[[Tag], str]] = None,
        attrs_xformer: Optional[Callable[[Tag], Mapping[str, _AttributeValue]]] = None,
        xformer: Optional[Callable[[Tag], None]] = None,
    ):
        if og_tag is not None or alt_tag is not None:
            _validate_name("og_tag", og_tag)
            _validate_name("alt_tag", alt_tag)
            if any(
                callback is not None for callback in (name_xformer, attrs_xformer, xformer)
            ):
                raise TypeError("Supply a tag-name pair or transformer callbacks")
        for argument, callback in (
            ("name_xformer", name_xformer),
            ("attrs_xformer", attrs_xformer),
            ("xformer", xformer),
        ):
            if callback is not None and not callable(callback):
                raise TypeError(f"{argument} must be callable")
        self.og_tag = og_tag
        self.alt_tag = alt_tag
        self.name_xformer = name_xformer
        self.attrs_xformer = attrs_xformer
        self.xformer = xformer

    def replace(self, tag: Tag) -> None:
        """Apply the configured transformations to a completed tag."""
        if self.alt_tag is not None:
            if tag.name == self.og_tag:
                tag.name = self.alt_tag
            return
        if self.name_xformer is not None:
            name = self.name_xformer(tag)
            if name != tag.name:
                _validate_name("name_xformer result", name)
                tag.name = name
        if self.attrs_xformer is not None:
            attrs = self.attrs_xformer(tag)
            if not isinstance(attrs, Mapping):
                raise TypeError("attrs_xformer must return an attribute mapping")
            if attrs is not tag.attrs:
                replacement = type(tag.attrs)()
                for key, value in attrs.items():
                    replacement[key] = value
                tag.attrs = replacement
        if self.xformer is not None:
            self.xformer(tag)
