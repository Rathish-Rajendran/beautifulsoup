"""Print elements with IDs, using SoupStrainer to retain relevant subtrees."""

from html import escape

if __package__:
    from ._common import arguments, parse_file
else:
    from _common import arguments, parse_file
from bs4 import SoupStrainer


def main():
    parser, args = arguments(__doc__)
    soup = parse_file(parser, args, parse_only=SoupStrainer(id=True))
    # Descendants of an accepted tag may lack IDs, so keep the single search.
    for tag in soup.find_all(id=True):
        print(f'<{tag.name} id="{escape(tag["id"], quote=True)}">')


if __name__ == "__main__":
    main()
