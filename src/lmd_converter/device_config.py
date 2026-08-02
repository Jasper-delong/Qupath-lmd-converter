"""Step 2: choose and configure the collection device (4-well / 96 / 384)."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from .core import PLATE_DIMENSIONS, generate_wells


def _ask_device() -> str:
    print("Choose collection device:")
    for device, dims in PLATE_DIMENSIONS.items():
        print(f"  {device}: {dims['label']}")
    while True:
        choice = input("Enter device (4 / 96 / 384): ").strip()
        if choice in PLATE_DIMENSIONS:
            return choice
        print("Invalid choice, try again.")


def _ask_margin(max_margin: int) -> int:
    while True:
        try:
            value = int(input(f"Margin (0-{max_margin}, default 0): ").strip() or "0")
            if 0 <= value <= max_margin:
                return value
        except ValueError:
            pass
        print("Invalid margin, try again.")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Configure the collection device and generate valid well IDs"
    )
    parser.add_argument(
        "--device",
        choices=sorted(PLATE_DIMENSIONS),
        help="Device type: 4, 96 or 384",
    )
    parser.add_argument(
        "--margin",
        type=int,
        default=0,
        help="Skip this many outer rows/columns (default: 0)",
    )
    parser.add_argument(
        "--interactive",
        action="store_true",
        help="Prompt for device and margin interactively",
    )
    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        default=Path("pipeline/device.json"),
        help="Output manifest (default: pipeline/device.json)",
    )
    args = parser.parse_args(argv)

    if args.interactive:
        device = _ask_device()
        dims = PLATE_DIMENSIONS[device]
        max_margin = min(dims["rows"], dims["cols"]) // 2 - 1
        margin = _ask_margin(max_margin)
    else:
        if args.device is None:
            parser.error("--device is required unless --interactive is used")
        device = args.device
        margin = args.margin

    wells = generate_wells(device, margin)
    manifest = {
        "device": device,
        "label": PLATE_DIMENSIONS[device]["label"],
        "margin": margin,
        "well_count": len(wells),
        "wells": wells,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    print(f"Device: {manifest['label']} (margin={margin})")
    print(f"Wells generated: {len(wells)}")
    print("Well list:", ", ".join(wells[:24]) + ("..." if len(wells) > 24 else ""))
    print(f"Manifest written to: {args.output}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
