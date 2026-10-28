"""Read an HTML/XML file into a BeautifulSoup tree and save pretty output."""

import argparse
from pathlib import Path
from time import perf_counter

from bs4 import BeautifulSoup, FeatureNotFound


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path, help="HTML or XML file to read")
    parser.add_argument(
        "-o", "--output", type=Path,
        help="Output file (default: INPUT_NAME.pretty.html or .xml)",
    )
    parser.add_argument(
        "--parser", choices=("html.parser", "xml"),
        help="Override parser selection (default: xml for .xml; html.parser otherwise)",
    )
    args = parser.parse_args()

    input_path = args.input
    output_path = args.output or input_path.with_name(
        f"{input_path.stem}.pretty{input_path.suffix}"
    )
    if input_path.resolve() == output_path.resolve():
        parser.error("Output must be a different file from the input.")

    parser_name = args.parser or (
        "xml" if input_path.suffix.lower() == ".xml" else "html.parser"
    )
    started = perf_counter()

    try:
        # Binary input lets BeautifulSoup detect the document's encoding.
        with input_path.open("rb") as source:
            soup = BeautifulSoup(source, parser_name)

        # Serialize the tree as indented Unicode text, then save it as UTF-8.
        pretty_markup = soup.prettify()
        output_path.write_text(pretty_markup, encoding="utf-8")
    except FeatureNotFound as error:
        parser.error(f"{error} Install lxml to enable XML parsing.")
    except OSError as error:
        parser.error(str(error))

    elapsed = perf_counter() - started
    print(f"Parser: {parser_name}")
    print(f"Saved: {output_path}")
    print(f"Read, parse, prettify, and write time: {elapsed:.3f} seconds")


if __name__ == "__main__":
    main()
