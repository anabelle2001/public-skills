# Set REPORT to the Markdown stem, and FIGURES to Python stems (without .py).
REPORT := report
FIGURES := example_figure
DATA := data.csv
PYTHON_RUN := uv run --no-sync python
PANDOC := pandoc
PDF_ENGINE := xelatex

FIGURE_PDFS := $(addprefix figures/,$(addsuffix .pdf,$(FIGURES)))

.PHONY: all figures clean
all: $(REPORT).pdf
figures: $(FIGURE_PDFS)

$(REPORT).pdf: $(REPORT).md $(FIGURE_PDFS)
	$(PANDOC) $< --pdf-engine=$(PDF_ENGINE) -o $@

# Put real input files for each figure here; replace DATA or add specific rules.
figures/%.pdf: %.py $(DATA) pyproject.toml
	$(PYTHON_RUN) $< $@

# Optional alternate deliverables: make figures/example_figure.svg
figures/%.svg figures/%.png: %.py $(DATA) pyproject.toml
	$(PYTHON_RUN) $< $@

clean:
	$(RM) $(REPORT).pdf $(addprefix figures/,$(foreach f,$(FIGURES),$(f).pdf $(f).svg $(f).png))
