---
name: Type relationship diagrams
description: Draw Python type relationships in D2 using ELK and SQL-table rows; use for attribute and return-type diagrams, callable notation, or checking connector crossings.
---

# Type relationship diagrams

Use these diagrams to communicate relationships between types. Choose the content to fit the reader's question; the conventions below govern how to draw it.

## Tables and rows

- Render types with `shape: sql_table`. Use the type name alone as the table heading, without a tagline or interpunct suffix.
- Put attribute names on the left and their types on the right. Keep useful Python notation such as `list[Region]` and `Image | None`.
- For callables, put the name and receiver on the left. Put remaining parameter names, types, and the return type on the right. Include `self` or `cls` as appropriate:

  | Left column | Right column |
  | --- | --- |
  | `current_image(self)` | `→ Image` |
  | `load_image(self, ...)` | `(path: Path, channel: int) → Image` |
  | `from_file(cls, ...)` | `(path: Path) → Self` |

- Use `...` on the left when parameters continue on the right. Show a static method without a receiver. Use the Unicode `→` in displayed signatures; D2 connection syntax still uses `->`.
- Normally show a Python property as an attribute, since callers access it without parentheses. If the diagram explains its getter implementation, a callable row may be more useful.
- Connect the exact source row to the referenced type. For `list[Region]`, the arrow can lead to `Region`; the row retains the collection information. Methods lead to their return types. Inheritance arrows are not the default relationship in this notation.
- Quote row keys containing punctuation and use the same quoted key in the edge declaration. See `examples/relationships.d2` for a complete example.

## Rendering

1. Write `.d2` source as UTF-8 **without a byte-order mark**. A BOM produced a spurious empty node in the tested D2 version.
2. Set `direction: down` as the starting layout. Render with ELK explicitly:

   ```sh
   d2 --layout elk --pad 32 relationships.d2 relationships.svg
   ```

   ELK supports anchoring SQL-table connections to individual rows. Keep ELK selected when iterating; the default D2 layout is not a substitute.
3. Start with each table's outgoing edges declared bottom-to-top relative to its rows. This is a routing heuristic, not a guarantee.
4. Inspect the SVG at readable scale. Follow each wire from its row to its arrowhead, checking crossings, shared segments, clipped labels, and unintended nodes. Use a rendered screenshot for visual inspection. When presenting alternatives, change one thing at a time and preserve the source for each.
5. Prefer downward flow unless the result is clearer horizontally. Compare `direction: down` and `direction: right` with identical nodes, rows, and edges when direction is uncertain. Keep the `.d2` source alongside the SVG.

## Checking crossings

Use `scripts/check_crossings.py` when routing is ambiguous or a diagram needs a crossing check. It runs D2/ELK itself, checks the SVG connector paths, and writes each candidate `.d2`, `.svg`, and a `results.json` with intersection coordinates. Run it through uv; its inline dependency metadata supplies Typer, svgpathtools, and Shapely.

```sh
# Render and check the current diagram without reordering it.
uv run <skill-dir>/scripts/check_crossings.py relationships.d2 --check-only

# Try all orders of one type's outgoing edge declarations.
uv run <skill-dir>/scripts/check_crossings.py relationships.d2 --prefix Image. --output edge-orders

# Hold rows and edges fixed while permuting three table declarations.
uv run <skill-dir>/scripts/check_crossings.py relationships.d2 --tables Image,Pixels,Region --output table-orders
```

The script accepts one standalone edge declaration per line and explicit top-level table blocks. It checks connector centerlines, including overlaps and self-intersections. Shared endpoints are allowed. Node collisions and arrowhead geometry require visual inspection. Lines use geometric intersection tests; curves are adaptively flattened to the configured tolerance, defaulting to 0.01 SVG units. Transformed connector paths are rejected rather than compared in incompatible coordinate systems.

Changing declaration order can change ELK's routing, including downstream routing. It can also leave the same crossings in every permutation. Start with a small, named permutation set; `--all-edges` grows factorially. Preserve the table rows while testing edge or table declaration order. Treat row reordering as a separate experiment.

After a change, rerender and recheck the whole diagram. Report the tested cases and remaining intersections honestly; neither bottom-to-top declarations nor a quick visual glance proves the diagram is crossing-free.
