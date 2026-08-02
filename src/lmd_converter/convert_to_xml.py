"""Step 4: build the Leica LMD XML from the extraction and match tables."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from .core import convert_to_xml as core_convert


def load_json(path: str | Path) -> dict:
    with open(path, "r", encoding="utf-8") as fh:
        return json.load(fh)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Generate Leica LMD XML cutting data"
    )
    parser.add_argument(
        "-e",
        "--extracted",
        type=Path,
        default=Path("pipeline/extracted.json"),
        help="Manifest from extract_geojson.py",
    )
    parser.add_argument(
        "-m",
        "--match",
        type=Path,
        default=Path("pipeline/match.json"),
        help="Match table from match_shapes.py",
    )
    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        default=Path("output/cutting.xml"),
        help="Output XML path (default: output/cutting.xml)",
    )
    parser.add_argument(
        "--preview",
        type=Path,
        default=Path("output/preview.png"),
        help="Preview image path (default: output/preview.png)",
    )
    parser.add_argument(
        "--no-preview",
        action="store_true",
        help="Disable preview image generation",
    )
    args = parser.parse_args(argv)

    extracted = load_json(args.extracted)
    match = load_json(args.match)
    preview_path = None if args.no_preview else args.preview
    summary = core_convert(extracted, match, args.output, preview_path=preview_path)

    print(json.dumps(summary, ensure_ascii=False, indent=2))
    print(f"XML written to: {args.output}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
