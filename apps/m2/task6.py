"""Rename <b> to <blockquote> during parsing and write the resulting tree."""

if __package__:
    from ._common import arguments, parse_file
else:
    from _common import arguments, parse_file
from bs4 import SoupReplacer


def main():
    parser, args = arguments(__doc__, output=True)
    soup = parse_file(parser, args, replacer=SoupReplacer("b", "blockquote"))
    # No find_all or second traversal to rename nodes. Serialization still
    # necessarily visits the result tree to write it to disk.
    try:
        args.output.write_text(str(soup), encoding="utf-8")
    except OSError as error:
        parser.error(str(error))
    print(f"Saved modified document: {args.output}")


if __name__ == "__main__":
    main()
