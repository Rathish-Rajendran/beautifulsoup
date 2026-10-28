"""Read an HTML/XML file and identify each hyperlink's nearest ancestor with an id."""

import argparse
from html import escape
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

    links = soup.find_all("a", href=True)
    if not links:
        print("No hyperlinks found.")
        return

    for number, link in enumerate(links, start=1):
        # Search upward from the link, stopping at the first ancestor with an id.
        parent = link.find_parent(id=True)
        link_text = link.get_text(" ", strip=True) or "(no text)"
        destination = link["href"] or "(empty href)"
        print(f"Link {number}")
        print(f"  Link text: {link_text}")
        print(f"  Destination: {destination}")
        if parent is None:
            print("  Nearest ancestor with an id: None found.")
        else:
            parent_id = escape(parent["id"], quote=True)
            print(f'  Nearest ancestor with an id: <{parent.name} id="{parent_id}">')
        print()


if __name__ == "__main__":
    main()
