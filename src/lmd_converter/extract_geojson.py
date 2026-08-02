"""Step 1: extract calibration points and cutting shapes from a GeoJSON file."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from .core import extract_from_text


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Extract calibration points and cutting shapes from QuPath GeoJSON"
    )
    parser.add_argument("geojson", type=Path, help="QuPath GeoJSON export")
    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        default=Path("pipeline/extracted.json"),
        help="Output manifest (default: pipeline/extracted.json)",
    )
    args = parser.parse_args(argv)

    if not args.geojson.exists():
        parser.error(f"GeoJSON file not found: {args.geojson}")

    with open(args.geojson, "r", encoding="utf-8") as fh:
        result = extract_from_text(fh.read())
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    print(f"Calibration points: {len(result['calibration_points'])}")
    for point in result["calibration_points"]:
        print(
            f"  {point['name']}: {point['coordinates'][0]}, {point['coordinates'][1]}"
        )
    print(f"Cutting shapes: {len(result['shapes'])}")
    for shape in result["shapes"]:
        print(f"  {shape['name']} ({shape['classification']}, {len(shape['coordinates'])} points)")
    print(f"Manifest written to: {args.output}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
