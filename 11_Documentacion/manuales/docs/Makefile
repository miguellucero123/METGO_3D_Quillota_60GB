# 🌾 METGO 3D - Sphinx Makefile
# Sistema Meteorológico Agrícola Quillota - Versión Operativa 2.0

# Minimal makefile for Sphinx documentation
#

# You can set these variables from the command line, and also
# from the environment for the first two.
SPHINXOPTS    ?=
SPHINXBUILD   ?= sphinx-build
SOURCEDIR     = .
BUILDDIR      = _build

# Put it first so that "make" without argument is like "make help".
help:
	@$(SPHINXBUILD) -M help "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)

.PHONY: help Makefile

# Catch-all target: route all unknown targets to Sphinx using the new
# "make mode" option.  $(O) is meant as a shortcut for $(SPHINXOPTS).
%: Makefile
	@$(SPHINXBUILD) -M $@ "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)

# Custom targets for METGO 3D documentation
.PHONY: clean html pdf epub

clean:
	rm -rf $(BUILDDIR)/*

html:
	@$(SPHINXBUILD) -M html "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)

pdf:
	@$(SPHINXBUILD) -M latexpdf "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)

epub:
	@$(SPHINXBUILD) -M epub "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)

# Install documentation dependencies
install-docs:
	pip install sphinx sphinx-rtd-theme myst-parser

# Build all documentation formats
build-all: html pdf epub

# Serve documentation locally
serve:
	python -m http.server 8000 --directory $(BUILDDIR)/html

# Check documentation for errors
check:
	@$(SPHINXBUILD) -M html "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O) -W

# Update documentation
update:
	git pull origin main
	@$(SPHINXBUILD) -M html "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)

# Deploy documentation
deploy:
	@$(SPHINXBUILD) -M html "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)
	# Add deployment commands here

# Help for custom targets
help-custom:
	@echo "Custom targets for METGO 3D documentation:"
	@echo "  clean       - Remove build directory"
	@echo "  html        - Build HTML documentation"
	@echo "  pdf         - Build PDF documentation"
	@echo "  epub        - Build EPUB documentation"
	@echo "  install-docs - Install documentation dependencies"
	@echo "  build-all   - Build all documentation formats"
	@echo "  serve       - Serve documentation locally"
	@echo "  check       - Check documentation for errors"
	@echo "  update      - Update and build documentation"
	@echo "  deploy      - Deploy documentation"
	@echo "  help-custom - Show this help message"
