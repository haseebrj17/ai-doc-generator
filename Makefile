# Makefile for documentation generation

.PHONY: help docs docs-full clean install

# Default target
help:
	@echo "Documentation Generator Commands:"
	@echo "  make install    - Install required dependencies"
	@echo "  make docs       - Generate/update documentation (incremental)"
	@echo "  make docs-full  - Regenerate all documentation"
	@echo "  make clean      - Remove generated documentation and state"
	@echo "  make serve      - Serve documentation locally (requires Python http.server)"

# Install dependencies
install:
	pip install -r requirements.txt

# Generate documentation (incremental)
docs:
	@echo "Generating documentation (incremental mode)..."
	cd ../.. && python scripts/generate_docs.py

# Generate full documentation
docs-full:
	@echo "Generating full documentation..."
	cd ../.. && python scripts/generate_docs.py --full

# Clean generated files
clean:
	@echo "Cleaning generated documentation..."
	rm -rf ../../docs/generated
	rm -f ../../.doc_state.json
	@echo "Clean complete."

# Serve documentation locally
serve:
	@echo "Serving documentation at http://localhost:8000"
	cd ../../docs/generated && python -m http.server 8000

# Check if API key is set
check-api-key:
	@if [ -z "$$OPENAI_API_KEY" ]; then \
		echo "Error: OPENAI_API_KEY environment variable is not set"; \
		exit 1; \
	else \
		echo "OpenAI API key is configured"; \
	fi

# Run with custom config
docs-with-config:
	cd ../.. && python scripts/generate_docs.py --config scripts/documentation/config.json