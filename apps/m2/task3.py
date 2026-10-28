"""Print every tag; an all-tag SoupStrainer cannot reduce this task's tree."""

if __package__:
    from ._common import arguments, parse_file
else:
    from _common import arguments, parse_file
from bs4 import SoupStrainer


def main():
    parser, args = arguments(__doc__)
    # Keeping every tag includes the outermost tag and all its descendants.
    # SoupStrainer is a subtree filter, not a way to discard text in that tree.
    soup = parse_file(parser, args, parse_only=SoupStrainer(True))
    for tag in soup.find_all(True):
        print(f"<{tag.name}>")


if __name__ == "__main__":
    main()
