---
name: Report writing
description: Create or revise self-contained Markdown, Python, Make and Pandoc PDF report directories; use for scientific or technical reports with generated figures.
---

# Report writing

1. Copy `template/` into a new report directory. Keep experiment scripts and headered CSV results in `data/`; write the paper in `paper/src/REPORT.md`, one chart script per figure in `paper/src/`, and shared chart code in `paper/src/util/`. Place generated figures in `paper/out/img/`. Keep `Makefile`, `rebuild.py`, and `pyproject.toml` at the root. Put title, author, and date in the Markdown YAML header.
2. Set `FIGURES` and each figure's actual data dependencies in the Makefile. Each figure script takes an output path and writes the requested PDF, SVG, or PNG. `make` builds `paper/out/REPORT.pdf`; `make figures` builds the charts. Run experiment scripts explicitly and preserve their headered CSV output; rebuilding a paper should never silently collect new measurements. `uv run rebuild.py` watches sources and data and rebuilds on changes. Keep `uv.lock` for reproducible runs. Use the `writing-python` skill for Python tooling and scripts. Install Pandoc, a LaTeX engine, and Make on the host.
3. Write for the reader: methods detailed enough to reproduce the work, units and uncertainty next to claims, captions that explain what each figure shows, and conclusions bounded by the observations. Refer to vector figure files (`.pdf` or `.svg`) in the Markdown; use PNG for photographs, screenshots, or genuinely raster data. For PDF output, prefer PDF figures because Pandoc/LaTeX can embed them directly.
4. Plot with Matplotlib. Use its default `tab10` color cycle for distinct series and `turbo` for continuous values, with a labeled colorbar. Apply `matplotlib.ticker.EngFormatter` to SI-valued axes; write descriptive axis labels with units and a meaningful plot title. Use a legend only when multiple series need distinguishing. Save the figure at a print-legible size and inspect the PDF at normal zoom.
5. Run `make` and inspect the resulting PDF for clipped labels, tiny text, rasterized plots, broken references, and page breaks. Fix the source, then rebuild. Keep environment-specific paths out of the Makefile.

The template runs Python through `uv run`. On Windows, invoke `make` from a shell where it and `pandoc` are on PATH.
