"""Read an HTML/XML file and print each tag name in angle brackets."""

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

    # True matches every tag name; text and comment nodes are not matches.
    for tag in soup.find_all(True):
        print(f"<{tag.name}>")


if __name__ == "__main__":
    main()
