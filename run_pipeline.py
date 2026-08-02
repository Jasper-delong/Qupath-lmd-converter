"""Run the full GeoJSON -> LMD XML pipeline in one command."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "src"))

from lmd_converter import convert_to_xml, device_config, extract_geojson, match_shapes


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Run extract -> device -> match -> convert in one go"
    )
    parser.add_argument("geojson", type=Path, help="QuPath GeoJSON export")
    parser.add_argument(
        "--device",
        choices=["4", "96", "384"],
        default="4",
        help="Collection device (default: 4)",
    )
    parser.add_argument("--margin", type=int, default=0, help="Outer margin to skip")
    parser.add_argument(
        "--interactive",
        action="store_true",
        help="Ask for device/margin and confirm each shape-to-well assignment",
    )
    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        default=Path("output/cutting.xml"),
        help="Output XML path (default: output/cutting.xml)",
    )
    args = parser.parse_args()

    steps = [
        extract_geojson.main([str(args.geojson)]),
        device_config.main(
            ["--interactive"] if args.interactive else ["--device", args.device, "--margin", str(args.margin)]
        ),
        match_shapes.main(["--interactive"] if args.interactive else []),
        convert_to_xml.main(["--output", str(args.output)]),
    ]
    return max(steps)


if __name__ == "__main__":
    sys.exit(main())
