"""Print hyperlink destinations, using SoupStrainer to retain relevant subtrees."""

if __package__:
    from ._common import arguments, parse_file
else:
    from _common import arguments, parse_file
from bs4 import SoupStrainer


def main():
    parser, args = arguments(__doc__)
    soup = parse_file(parser, args, parse_only=SoupStrainer("a", href=True))
    # Retained anchor subtrees may include other elements; filter results too.
    for link in soup.find_all("a", href=True):
        print(link["href"])


if __name__ == "__main__":
    main()
