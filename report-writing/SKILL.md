---
name: Report writing
description: Create or revise self-contained Markdown, Python, Make and Pandoc PDF report directories; use for scientific or technical reports with generated figures.
---

# Report writing

1. Start a report directory with `Makefile`, `rebuild.py`, `pyproject.toml` and a named Markdown source such as `report.md`. Copy the templates in this skill's `template/` directory, then set `REPORT` and `FIGURES` in the Makefile. Keep source, data or reproducible data references, figure scripts and output together. Put the report metadata (title, author, date) in the Markdown YAML header.
2. Make one Python script per figure and declare each figure's actual data inputs in the Makefile. A figure script accepts an output filename as its first argument and writes that format. `make` produces `report.pdf`; `make figures` builds figures; `uv run rebuild.py` watches and rebuilds. Install Python packages with `uv add`; install Pandoc, a LaTeX engine and Make on the host.
3. Write for the reader: methods detailed enough to reproduce the work, units and uncertainty next to claims, captions that explain what each figure shows, and conclusions bounded by the observations. Refer to vector figure files (`.pdf` or `.svg`) in the Markdown; use PNG for photographs, screenshots, or genuinely raster data. For PDF output, prefer PDF figures because Pandoc/LaTeX can embed them directly.
4. Plot with Matplotlib. Use its default `tab10` color cycle for distinct series and `turbo` for continuous values, with a labeled colorbar. Apply `matplotlib.ticker.EngFormatter` to SI-valued axes; write descriptive axis labels with units and a meaningful plot title. Use a legend only when multiple series need distinguishing. Save the figure at a print-legible size and inspect the PDF at normal zoom.
5. Run `make` and inspect the resulting PDF for clipped labels, tiny text, rasterized plots, broken references, and page breaks. Fix the source, then rebuild. Keep environment-specific paths out of the Makefile.

The templates use `uv run --no-sync` for figure scripts after `uv sync`. Set `PYTHON_RUN` in the Makefile if a project needs another invocation. On Windows, invoke `make` from a shell where it and `pandoc` are on PATH.
