# /// script
# requires-python = ">=3.10"
# dependencies = ["typer", "svgpathtools", "shapely"]
# ///
"""Render D2 with ELK and search edge declaration permutations for crossings.

Run: uv run check_crossings.py relationships.d2 --check-only
Checks SVG connector centerlines, including overlaps. Straight segments are exact;
Bezier curves are flattened adaptively to --tolerance SVG units. Shared endpoints
are allowed; endpoint-to-interior touches count. Arrowheads and nodes are excluded.
"""

from __future__ import annotations

import itertools
import json
import re
import subprocess
import xml.etree.ElementTree as ET
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import Annotated

import typer
from shapely.geometry import LineString, Point
from shapely.geometry.base import BaseGeometry, BaseMultipartGeometry
from svgpathtools import parse_path

app = typer.Typer()


def flatten(points: list[complex], tolerance: float) -> list[complex]:
    """Subdivide until the Bezier control polygon is within tolerance of its chord."""
    chord = LineString([
        (points[0].real, points[0].imag),
        (points[-1].real, points[-1].imag),
    ])
    if (
        len(points) == 2
        or max(chord.distance(Point(p.real, p.imag)) for p in points[1:-1]) <= tolerance
    ):
        return [points[0], points[-1]]
    levels = [points]
    while len(levels[-1]) > 1:
        levels.append([(a + b) / 2 for a, b in zip(levels[-1], levels[-1][1:])])
    left = [level[0] for level in levels]
    right = [level[-1] for level in reversed(levels)]
    return flatten(left, tolerance)[:-1] + flatten(right, tolerance)


def atomic(geometry: BaseGeometry) -> list[BaseGeometry]:
    if geometry.is_empty:
        return []
    if isinstance(geometry, BaseMultipartGeometry):
        return [part for child in geometry.geoms for part in atomic(child)]
    return [geometry]


def inspect_svg(svg: Path, tolerance: float) -> dict:
    tree = ET.parse(svg)
    connectors: list[LineString] = []

    # D2 places all edge paths in the same coordinate system. Reject transformed
    # paths rather than silently comparing unrelated coordinates.
    def walk(element: ET.Element, transformed: bool = False) -> None:
        transformed = transformed or bool(element.get("transform"))
        if (
            element.tag.endswith("}path")
            and "connection" in element.get("class", "").split()
        ):
            if transformed:
                raise ValueError(
                    "Transformed connector: normalize SVG coordinates first"
                )
            points: list[complex] = []
            for segment in parse_path(element.attrib["d"]):
                if not hasattr(segment, "bpoints"):
                    raise ValueError(
                        "Unsupported SVG arc; expected D2 lines/Bezier curves"
                    )
                part = flatten(list(segment.bpoints()), tolerance)
                points.extend(part if not points else part[1:])
            connectors.append(LineString([(p.real, p.imag) for p in points]))
        for child in element:
            walk(child, transformed)

    walk(tree.getroot())
    crossings = []
    for (i, a), (j, b) in itertools.combinations(enumerate(connectors), 2):
        ends_a = [Point(a.coords[0]), Point(a.coords[-1])]
        ends_b = [Point(b.coords[0]), Point(b.coords[-1])]
        for hit in atomic(a.intersection(b)):
            if hit.geom_type == "Point" and (
                min(hit.distance(p) for p in ends_a) < 1e-6
                and min(hit.distance(p) for p in ends_b) < 1e-6
            ):
                continue
            crossings.append({
                "edges": [i, j],
                "kind": hit.geom_type,
                "geometry": hit.wkt,
            })
    return {
        "edge_count": len(connectors),
        "crossings": crossings,
        "self_intersecting_edges": [
            i for i, line in enumerate(connectors) if not line.is_simple
        ],
    }


@app.command()
def main(
    source: Annotated[
        Path, typer.Argument(help="D2 source with one edge declaration per line")
    ],
    output: Annotated[
        Path, typer.Option(help="Directory for rendered candidates and results")
    ] = Path("crossing-search"),
    prefix: Annotated[
        str,
        typer.Option(help="Permute edges starting with this text; empty selects all"),
    ] = "Image.",
    tolerance: Annotated[float, typer.Option(min=0.00001)] = 0.01,
    workers: Annotated[int, typer.Option(min=1, max=16)] = 4,
    all_edges: Annotated[
        bool, typer.Option(help="Permute all edge declarations")
    ] = False,
    tables: Annotated[
        str,
        typer.Option(
            help="Comma-separated top-level tables to permute instead of edges"
        ),
    ] = "",
    check_only: Annotated[
        bool, typer.Option(help="Render once with declarations unchanged")
    ] = False,
) -> None:
    if check_only and (tables or all_edges):
        raise typer.BadParameter("Use --check-only without permutation options")
    if all_edges:
        prefix = ""
    output.mkdir(parents=True, exist_ok=True)
    lines = source.read_text(encoding="utf-8-sig").splitlines()
    spans: list[tuple[int, int]] = []
    items: list[str] = []
    blocks: dict[str, list[str]] = {}
    if tables:
        names = tables.split(",")
        for i, line in enumerate(lines):
            name = next((name for name in names if line.startswith(name + ":")), None)
            if name is None:
                continue
            depth = 0
            for end in range(i, len(lines)):
                # Braces inside quoted row names/types do not delimit D2 blocks.
                structural = re.sub(r'"(?:\\.|[^"\\])*"', "", lines[end]).split("#", 1)[
                    0
                ]
                depth += structural.count("{") - structural.count("}")
                if depth == 0:
                    break
            else:
                raise ValueError(f"Unclosed table {name}")
            spans.append((i, end + 1))
            items.append(name)
            blocks[name] = lines[i : end + 1]
        if set(items) != set(names) or len(items) != len(names):
            raise typer.BadParameter(
                "Expected one explicit top-level block for each table"
            )
    else:
        indices = [
            i
            for i, line in enumerate(lines)
            if line.startswith("" if check_only else prefix)
            and " -> " in line
            and not line.lstrip().startswith("#")
        ]
        spans = [(i, i + 1) for i in indices]
        items = [lines[i] for i in indices]
        blocks = {line: [line] for line in items}
    if not items:
        raise typer.BadParameter("No matching declarations")
    version = subprocess.check_output(["d2", "--version"], text=True).strip()
    results = []

    def render(item: tuple[int, tuple[str, ...]]) -> dict:
        number, order = item
        candidate = list(lines)
        for (start, end), declaration in reversed(list(zip(spans, order))):
            candidate[start:end] = blocks[declaration]
        d2_file = output / f"candidate-{number:04d}.d2"
        svg = d2_file.with_suffix(".svg")
        d2_file.write_text("\n".join(candidate) + "\n", encoding="utf-8")
        subprocess.run(
            ["d2", "--layout", "elk", "--pad", "32", str(d2_file), str(svg)],
            check=True,
            capture_output=True,
        )
        result = inspect_svg(svg, tolerance)
        result.update({"candidate": number, "order": order, "svg": svg.name})
        result["edge_labels"] = [
            line
            for line in candidate
            if " -> " in line and not line.lstrip().startswith("#")
        ]
        if result["edge_count"] != len(result["edge_labels"]):
            raise ValueError("SVG edge count differs from declarations")
        return result

    with ThreadPoolExecutor(max_workers=workers) as pool:
        orders = [tuple(items)] if check_only else itertools.permutations(items)
        for result in pool.map(render, enumerate(orders)):
            results.append(result)
            if len(items) <= 3 or len(results) % 100 == 0:
                typer.echo(
                    f"{len(results)} rendered; latest: {len(result['crossings'])} intersections"
                )
    best = min(
        results, key=lambda r: len(r["crossings"]) + len(r["self_intersecting_edges"])
    )
    report = {
        "source": str(source.resolve()),
        "d2_version": version,
        "layout": "elk",
        "tolerance": tolerance,
        "prefix": prefix,
        "tables": tables,
        "check_only": check_only,
        "best": best["candidate"],
        "results": results,
    }
    (output / "results.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    typer.echo(f"Best: {output / best['svg']}")
    typer.echo(
        f"Intersections: {len(best['crossings'])}; self-intersecting edges: {len(best['self_intersecting_edges'])}"
    )


if __name__ == "__main__":
    app()
