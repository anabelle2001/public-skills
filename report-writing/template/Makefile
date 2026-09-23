# Set FIGURES to the stems of scripts in paper/src/ (without .py).
FIGURES := example_figure
DATA := data/results.csv
UTIL := $(wildcard paper/src/util/*.py)
PYTHON_RUN := uv run python
PANDOC := pandoc
PDF_ENGINE := xelatex

FIGURE_PDFS := $(addprefix paper/out/img/,$(addsuffix .pdf,$(FIGURES)))

.DEFAULT_GOAL := all
.PHONY: all figures clean
all: REPORT.pdf
figures: $(FIGURE_PDFS)

REPORT.pdf: paper/out/REPORT.pdf
	$(PYTHON_RUN) -c "from shutil import copyfile; copyfile('paper/out/REPORT.pdf', 'REPORT.pdf')"

paper/out/REPORT.pdf: paper/src/REPORT.md $(FIGURE_PDFS)
	$(PANDOC) $< --pdf-engine=$(PDF_ENGINE) -o $@

# Replace DATA with the real inputs for each figure, using separate rules if needed.
paper/out/img/%.pdf: paper/src/%.py $(DATA) $(UTIL) pyproject.toml
	$(PYTHON_RUN) $< $@

# Optional alternate formats: make paper/out/img/example_figure.svg
paper/out/img/%.svg: paper/src/%.py $(DATA) $(UTIL) pyproject.toml
	$(PYTHON_RUN) $< $@

paper/out/img/%.png: paper/src/%.py $(DATA) $(UTIL) pyproject.toml
	$(PYTHON_RUN) $< $@

clean:
	$(RM) REPORT.pdf paper/out/REPORT.pdf $(addprefix paper/out/img/,$(foreach f,$(FIGURES),$(f).pdf $(f).svg $(f).png))
