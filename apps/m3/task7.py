"""Set class="test" on every paragraph during parsing and save the document."""

import argparse
from pathlib import Path
import sys

# Use the local library when this script is invoked directly from a checkout.
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from bs4 import BeautifulSoup, FeatureNotFound, SoupReplacer  # noqa: E402


def paragraph_attrs(tag):
    if tag.name == "p":
        return {**tag.attrs, "class": "test"}
    return tag.attrs


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path, help="HTML or XML file")
    parser.add_argument("-o", "--output", type=Path, help="Path for the modified file")
    args = parser.parse_args()
    source = args.input
    output = args.output or source.with_name(f"{source.stem}.test-class{source.suffix}")
    parser_name = "xml" if source.suffix.lower() == ".xml" else "html.parser"

    try:
        if source.resolve() == output.resolve() or (
            output.exists() and source.samefile(output)
        ):
            parser.error("Output must be a different file from the input.")
        with source.open("rb") as markup:
            soup = BeautifulSoup(
                markup, parser_name, replacer=SoupReplacer(attrs_xformer=paragraph_attrs)
            )
        output.write_text(str(soup), encoding="utf-8")
    except (FeatureNotFound, OSError) as error:
        parser.error(str(error))
    print(f"Saved modified document: {output}")


if __name__ == "__main__":
    main()
