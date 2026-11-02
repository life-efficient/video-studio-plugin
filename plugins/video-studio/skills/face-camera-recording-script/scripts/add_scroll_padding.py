#!/usr/bin/env python3
import argparse
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Append teleprompter scroll padding to a markdown script."
    )
    parser.add_argument("path", help="Markdown script path to update.")
    parser.add_argument(
        "--lines",
        type=int,
        default=60,
        help="Number of visible spacer lines to add.",
    )
    args = parser.parse_args()

    path = Path(args.path)
    text = path.read_text(encoding="utf-8") if path.exists() else ""
    text = text.rstrip()

    marker = "\n## Scroll Padding\n"
    if marker in text:
        text = text.split(marker, 1)[0].rstrip()

    spacer = "\n\n".join("." for _ in range(args.lines))
    path.write_text(f"{text}\n\n## Scroll Padding\n\n{spacer}\n", encoding="utf-8")


if __name__ == "__main__":
    main()
