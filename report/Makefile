# Makefile for LaTeX Report Compilation

# Main document
MAIN = main
TEX = pdflatex
BIB = bibtex

# Output directory
OUT_DIR = build

.PHONY: all pdf clean view help

# Default target
all: pdf

# Compile PDF
pdf:
	@echo "Compiling LaTeX document..."
	$(TEX) $(MAIN).tex
	$(BIB) $(MAIN)
	$(TEX) $(MAIN).tex
	$(TEX) $(MAIN).tex
	@echo "Compilation complete! Output: $(MAIN).pdf"

# Quick compile (no bibliography)
quick:
	@echo "Quick compile (no bibliography)..."
	$(TEX) $(MAIN).tex

# Clean auxiliary files
clean:
	@echo "Cleaning auxiliary files..."
	rm -f *.aux *.log *.out *.toc *.bbl *.blg *.synctex.gz *.fls *.fdb_latexmk
	rm -f sections/*.aux
	@echo "Clean complete!"

# Clean everything including PDF
cleanall: clean
	rm -f $(MAIN).pdf
	@echo "All files removed!"

# View PDF (cross-platform)
view: pdf
	@echo "Opening PDF..."
ifeq ($(OS),Windows_NT)
	start $(MAIN).pdf
else
	@if command -v xdg-open > /dev/null; then \
		xdg-open $(MAIN).pdf; \
	elif command -v open > /dev/null; then \
		open $(MAIN).pdf; \
	else \
		echo "No PDF viewer found"; \
	fi
endif

# Continuous compilation (requires latexmk)
watch:
	@echo "Starting continuous compilation..."
	latexmk -pdf -pvc $(MAIN).tex

# Word count (approximate)
wordcount:
	@echo "Approximate word count:"
	@texcount -total $(MAIN).tex

# Spell check (requires aspell)
spell:
	@echo "Spell checking..."
	@aspell -t -c $(MAIN).tex

# Help
help:
	@echo "LaTeX Report Makefile"
	@echo ""
	@echo "Usage:"
	@echo "  make          - Compile PDF with bibliography"
	@echo "  make quick    - Quick compile (no bibliography)"
	@echo "  make clean    - Remove auxiliary files"
	@echo "  make cleanall - Remove all generated files"
	@echo "  make view     - Compile and open PDF"
	@echo "  make watch    - Continuous compilation (latexmk required)"
	@echo "  make wordcount- Count words"
	@echo "  make spell    - Spell check (aspell required)"
	@echo "  make help     - Show this help message"
