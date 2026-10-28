"""Read an HTML/XML file and print anchor href values in document order."""

import argparse
from pathlib import Path

from bs4 import BeautifulSoup, FeatureNotFound


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path, help="HTML or XML file to read")
    parser.add_argument(
        "--parser", choices=("html.parser", "xml"),
        help="Override parser selection (default: xml for .xml; html.parser otherwise)",
    )
    args = parser.parse_args()

    input_path = args.input
    parser_name = args.parser or (
        "xml" if input_path.suffix.lower() == ".xml" else "html.parser"
    )

    try:
        # Binary input lets BeautifulSoup detect the document's encoding.
        with input_path.open("rb") as source:
            soup = BeautifulSoup(source, parser_name)
    except FeatureNotFound as error:
        parser.error(f"{error} Install lxml to enable XML parsing.")
    except OSError as error:
        parser.error(str(error))

    # Include nested anchors with an href; skip placeholders without one.
    for link in soup.find_all("a", href=True):
        print(link["href"])


if __name__ == "__main__":
    main()
