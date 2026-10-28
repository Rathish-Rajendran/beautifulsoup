"""Rename all <b> elements to <blockquote> and save the modified HTML/XML tree."""

import argparse
from pathlib import Path

from bs4 import BeautifulSoup, FeatureNotFound


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path, help="HTML or XML file to read")
    parser.add_argument(
        "-o", "--output", type=Path,
        help="Output file (default: INPUT_NAME.blockquote.html or .xml)",
    )
    parser.add_argument(
        "--parser", choices=("html.parser", "xml"),
        help="Override parser selection (default: xml for .xml; html.parser otherwise)",
    )
    args = parser.parse_args()

    input_path = args.input
    output_path = args.output or input_path.with_name(
        f"{input_path.stem}.blockquote{input_path.suffix}"
    )
    if input_path.resolve() == output_path.resolve():
        parser.error("Output must be a different file from the input.")

    parser_name = args.parser or (
        "xml" if input_path.suffix.lower() == ".xml" else "html.parser"
    )

    try:
        # Also reject a different path that points to the same file via a hard link.
        if output_path.exists() and input_path.samefile(output_path):
            parser.error("Output must be a different file from the input.")

        # Binary input lets BeautifulSoup detect the document's encoding.
        with input_path.open("rb") as source:
            soup = BeautifulSoup(source, parser_name)

        bold_tags = soup.find_all("b")
        for tag in bold_tags:
            # Rename the existing element, preserving its attributes and children.
            tag.name = "blockquote"

        # Save the entire modified tree without adding prettification whitespace.
        output_path.write_text(str(soup), encoding="utf-8")
    except FeatureNotFound as error:
        parser.error(f"{error} Install lxml to enable XML parsing.")
    except OSError as error:
        parser.error(str(error))

    print(f"Elements renamed from <b> to <blockquote>: {len(bold_tags)}")
    print(f"Saved modified document: {output_path}")


if __name__ == "__main__":
    main()
