"""Shared core logic for the GeoJSON -> LMD XML pipeline.

Both the command line scripts and the Streamlit app call these functions, so
the web version and the CLI version always share the same verified logic.
"""

from __future__ import annotations

import json
import string
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from lmd.lib import Collection, Shape

PLATE_DIMENSIONS = {
    "4": {"rows": 2, "cols": 2, "label": "4-well"},
    "96": {"rows": 8, "cols": 12, "label": "96-well"},
    "384": {"rows": 16, "cols": 24, "label": "384-well"},
}


def extract_from_text(geojson_text: str) -> dict[str, object]:
    """Parse GeoJSON text into calibration points and cutting shapes.

    Point/LineString geometries become calibration points (in file order),
    Polygon geometries become cutting shapes. Coordinates are kept exactly
    as written in the source file.
    """

    data = json.loads(geojson_text)
    if data.get("type") != "FeatureCollection":
        raise ValueError("Expected a GeoJSON FeatureCollection")

    calibration_points: list[dict[str, object]] = []
    shapes: list[dict[str, object]] = []

    for feature in data.get("features", []):
        geometry = feature.get("geometry") or {}
        geom_type = geometry.get("type")
        coords = geometry.get("coordinates")
        if not coords:
            continue

        properties = feature.get("properties") or {}
        name = properties.get("name", "Unnamed")

        if geom_type in ("Point", "LineString"):
            point = coords[0] if geom_type == "LineString" else coords
            calibration_points.append(
                {"name": str(name), "coordinates": point, "type": geom_type}
            )
        elif geom_type == "Polygon":
            ring = coords[0] if coords and isinstance(coords[0], list) else coords
            shapes.append(
                {
                    "name": str(name),
                    "coordinates": ring,
                    "classification": _classification_name(properties),
                }
            )
        elif geom_type == "MultiPolygon":
            print(
                f"Warning: skipping MultiPolygon '{name}'; only Polygon is supported",
                file=sys.stderr,
            )

    return {
        "calibration_points": calibration_points,
        "shapes": shapes,
    }


def _classification_name(properties: dict[str, object]) -> str:
    classification = properties.get("classification")
    if isinstance(classification, dict):
        return str(classification.get("name", "Unclassified"))
    if isinstance(classification, str):
        return classification
    return "Unclassified"


def generate_wells(device: str, margin: int = 0) -> list[str]:
    """Generate well IDs for a device, optionally skipping an outer margin.

    The 4-well device uses single-letter IDs A/B/C/D; 96- and 384-well
    devices use standard grid IDs such as A1, B2, etc.
    """

    if device not in PLATE_DIMENSIONS:
        raise ValueError(
            f"Unknown device '{device}'; choose one of {sorted(PLATE_DIMENSIONS)}"
        )
    if margin < 0:
        raise ValueError("margin must be >= 0")

    if device == "4":
        return list(string.ascii_uppercase[:4])

    dims = PLATE_DIMENSIONS[device]
    rows = dims["rows"]
    cols = dims["cols"]
    wells: list[str] = []
    for row in range(margin, rows - margin):
        for col in range(margin, cols - margin):
            wells.append(f"{string.ascii_uppercase[row]}{col + 1}")
    return wells


def assign_round_robin(shape_names: list[str], wells: list[str]) -> list[dict[str, str]]:
    """Assign wells in order, cycling when there are more shapes than wells."""

    if not wells:
        raise ValueError("Device has no wells; check device configuration")
    return [
        {"shape_name": name, "well": wells[index % len(wells)]}
        for index, name in enumerate(shape_names)
    ]


def convert_to_xml(
    extracted: dict,
    match: dict,
    output_xml: str | Path,
    scale: float = 100.0,
    preview_path: str | Path | None = None,
) -> dict[str, object]:
    """Convert extracted shapes into an LMD XML file.

    Coordinates are kept in the source pixel space, with the Y axis flipped
    to match the LMD coordinate convention. Wells are written as ``CapID``
    metadata only; shape positions are not translated.
    """

    calibration = np.array(
        [point["coordinates"] for point in extracted["calibration_points"]],
        dtype=float,
    )
    if calibration.shape != (3, 2):
        raise ValueError(
            f"Expected exactly 3 calibration points, found {len(calibration)}"
        )
    calibration[:, 1] *= -1

    collection = Collection(calibration_points=calibration, scale=scale)

    well_by_name = {a["shape_name"]: a["well"] for a in match["assignments"]}
    placed = 0
    skipped: list[str] = []
    for shape in extracted["shapes"]:
        name = shape["name"]
        well = well_by_name.get(name)
        if well is None:
            skipped.append(name)
            continue
        coords = np.array(shape["coordinates"], dtype=float)
        if coords.ndim != 2 or coords.shape[1] != 2:
            raise ValueError(f"Shape '{name}' has unexpected coordinate shape")
        coords[:, 1] *= -1
        collection.add_shape(Shape(coords, well=well, name=name))
        placed += 1

    output_xml = Path(output_xml)
    output_xml.parent.mkdir(parents=True, exist_ok=True)
    collection.save(str(output_xml))

    if preview_path is not None:
        _plot_preview(collection, output_xml, preview_path)

    return {
        "calibration_points": calibration.tolist(),
        "shapes_total": len(extracted["shapes"]),
        "shapes_placed": placed,
        "shapes_skipped": skipped,
    }


def _plot_preview(
    collection: Collection, xml_path: Path, preview_path: str | Path
) -> None:
    """Plot the final cutting data as stored in the XML file.

    The figure is generated by reading the saved XML back through py-lmd, so
    the preview always shows exactly what was written to disk. Calibration
    points are drawn as red crosses; each shape is drawn with its name and
    CapID well label.
    """

    loaded = Collection()
    loaded.load(str(xml_path))

    plt.clf()
    fig, ax = plt.subplots(figsize=(10, 8))

    if loaded.calibration_points is not None:
        cal = loaded.calibration_points
        ax.scatter(cal[:, 0], cal[:, 1], marker="x", s=120, color="red", label="Calibration")
        for i, (x, y) in enumerate(cal, 1):
            ax.annotate(f"Cal{i}", (x, y), textcoords="offset points", xytext=(8, 8), color="red")

    for shape in loaded.shapes:
        points = shape.points
        ax.plot(points[:, 0], points[:, 1], linewidth=1.5)
        cx, cy = points[:, 0].mean(), points[:, 1].mean()
        label = shape.name or "Shape"
        if shape.well:
            label += f" -> {shape.well}"
        ax.annotate(label, (cx, cy), fontsize=8, ha="center", va="center")

    ax.set_xlabel("X")
    ax.set_ylabel("Y")
    ax.set_title("LMD cutting data preview")
    ax.grid(True, linestyle="--", alpha=0.4)
    ax.legend(loc="best")
    ax.set_aspect("equal", adjustable="box")
    fig.tight_layout()

    preview_path = Path(preview_path)
    preview_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(preview_path, dpi=150)
    plt.close(fig)
