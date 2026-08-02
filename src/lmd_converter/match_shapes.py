"""Step 3: assign each cutting shape to a well."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from .core import assign_round_robin


def load_json(path: str | Path) -> dict:
    with open(path, "r", encoding="utf-8") as fh:
        return json.load(fh)


def _ask_assignments(
    shape_names: list[str], wells: list[str]
) -> list[dict[str, str]]:
    assignments: list[dict[str, str]] = []
    print("Assign each shape to a well (round-robin values shown as defaults):")
    for index, name in enumerate(shape_names):
        default = wells[index % len(wells)]
        while True:
            value = input(f"  {name} -> well [{default}]: ").strip()
            if not value:
                value = default
            if value in wells:
                assignments.append({"shape_name": name, "well": value})
                break
            print(f"  '{value}' is not in the well list, try again.")
    return assignments


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Assign cutting shapes to wells and write the match table"
    )
    parser.add_argument(
        "-e",
        "--extracted",
        type=Path,
        default=Path("pipeline/extracted.json"),
        help="Manifest from extract_geojson.py (default: pipeline/extracted.json)",
    )
    parser.add_argument(
        "-d",
        "--device",
        type=Path,
        default=Path("pipeline/device.json"),
        help="Manifest from device_config.py (default: pipeline/device.json)",
    )
    parser.add_argument(
        "--interactive",
        action="store_true",
        help="Prompt for every shape-to-well assignment",
    )
    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        default=Path("pipeline/match.json"),
        help="Output match table (default: pipeline/match.json)",
    )
    args = parser.parse_args(argv)

    extracted = load_json(args.extracted)
    device = load_json(args.device)
    shape_names = [shape["name"] for shape in extracted["shapes"]]
    wells = device["wells"]

    if args.interactive:
        assignments = _ask_assignments(shape_names, wells)
    else:
        assignments = assign_round_robin(shape_names, wells)

    manifest = {
        "device": device["device"],
        "assignments": assignments,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    print(f"Shapes: {len(shape_names)}, wells used: {len(set(a['well'] for a in assignments))}")
    for assignment in assignments:
        print(f"  {assignment['shape_name']} -> {assignment['well']}")
    print(f"Match table written to: {args.output}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
