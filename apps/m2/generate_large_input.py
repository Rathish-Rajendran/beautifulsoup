"""Generate a deterministic, tag-rich HTML file for large-file validation."""

import argparse
from pathlib import Path


def generate(path, mib=16, padding_words=128):
    if mib < 1:
        raise ValueError("mib must be at least 1")
    if padding_words < 1:
        raise ValueError("padding_words must be at least 1")
    target = mib * 1024 * 1024
    header = b"<!DOCTYPE html><html><head><title>M2 large input</title></head><body>\n"
    footer = b"</body></html>\n"
    written = len(header)
    index = 0
    with path.open("wb") as output:
        output.write(header)
        while True:
            identifier = f' id="section-{index}"' if index % 64 == 0 else ""
            link = f'<a href="https://example.com/{index}"><span>link</span></a>' if index % 32 == 0 else ""
            bold = '<b class="bold">outer <b>inner</b> tail</b>' if index % 4 == 0 else ""
            row = (f'<section{identifier}><p>{"padding " * padding_words}</p>{link}{bold}</section>\n').encode("ascii")
            if written + len(row) + len(footer) > target:
                break
            output.write(row)
            written += len(row)
            index += 1
        # Padding is outside selected subtrees, not one giant text-only file.
        output.write(b" " * (target - written - len(footer)))
        output.write(footer)
    return index


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("output", type=Path)
    parser.add_argument("--mib", type=int, default=16)
    parser.add_argument("--padding-words", type=int, default=128,
                        help="Words per paragraph; 1024 is used for the 1 GiB fixture")
    args = parser.parse_args()
    if args.mib < 1:
        parser.error("--mib must be at least 1")
    if args.padding_words < 1:
        parser.error("--padding-words must be at least 1")
    args.output.parent.mkdir(parents=True, exist_ok=True)
    rows = generate(args.output, args.mib, args.padding_words)
    print(f"Generated {args.output}: {args.output.stat().st_size} bytes, {rows} sections")


if __name__ == "__main__":
    main()
