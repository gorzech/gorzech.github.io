PYTHON ?= python3
QUARTO ?= quarto

.PHONY: help test check gen-pubs render preview clean

help:
	@echo "Targets:"
	@echo "  make test      - run unit tests"
	@echo "  make check     - validate publications.bib"
	@echo "  make gen-pubs  - regenerate publication pages"
	@echo "  make render    - generate publications and render full Quarto site"
	@echo "  make preview   - generate publications and start local Quarto preview"
	@echo "  make clean     - remove local _site output"

test:
	$(PYTHON) -m unittest discover -s tests -p 'test_*.py'

check:
	$(PYTHON) scripts/gen_publications.py --check

gen-pubs:
	$(PYTHON) scripts/gen_publications.py

render: gen-pubs
	$(QUARTO) render

preview: gen-pubs
	$(QUARTO) preview --no-browser

clean:
	rm -rf _site
