"""Shared command-line handling; always import the submitted local library."""

import argparse
from pathlib import Path
import sys
from time import perf_counter

# Direct invocation sets sys.path[0] to apps/m2, not the checkout root.
# Put this checkout first so a globally installed bs4 cannot hide our API.
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from bs4 import BeautifulSoup, FeatureNotFound  # noqa: E402


def arguments(description, output=False):
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument("input", type=Path, help="HTML or XML file")
    parser.add_argument("--parser", choices=("html.parser", "lxml", "xml"),
                        help="Default: xml for .xml files, html.parser otherwise")
    if output:
        parser.add_argument("-o", "--output", type=Path,
                            help="Default: INPUT_STEM.blockquote.INPUT_SUFFIX")
    args = parser.parse_args()
    args.parser = args.parser or ("xml" if args.input.suffix.lower() == ".xml" else "html.parser")
    if output:
        args.output = args.output or args.input.with_name(
            f"{args.input.stem}.blockquote{args.input.suffix}"
        )
        try:
            same_file = args.input.resolve() == args.output.resolve() or (
                args.output.exists() and args.input.samefile(args.output)
            )
        except OSError as error:
            parser.error(str(error))
        if same_file:
            parser.error("Output must be a different file from the input.")
    return parser, args


def parse_file(parser, args, **kwargs):
    started = perf_counter()
    try:
        with args.input.open("rb") as source:
            soup = BeautifulSoup(source, args.parser, **kwargs)
    except FeatureNotFound as error:
        parser.error(f"{error} Install lxml for XML/lxml parsing.")
    except OSError as error:
        parser.error(str(error))
    print(f"Parser: {args.parser}; read/parse: {perf_counter() - started:.3f} seconds", file=sys.stderr)
    return soup
