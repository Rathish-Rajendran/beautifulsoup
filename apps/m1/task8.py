"""Use CSS selectors to list document headings and their text in document order."""

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

    # A comma-separated CSS selector matches any of these heading tag names.
    headings = soup.select("h1, h2, h3, h4, h5, h6")
    if not headings:
        print("No headings found.")
        return

    print("Document headings:")
    for number, heading in enumerate(headings, start=1):
        heading_text = heading.get_text(" ", strip=True) or "(no text)"
        print(f"{number}. <{heading.name}> {heading_text}")


if __name__ == "__main__":
    main()
