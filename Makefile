# Cursor Mover - common development tasks.
# Run `make help` for the list.

.DEFAULT_GOAL := help
.PHONY: help install run test lint format check icon app dmg clean

PYTHON ?= python3

help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) \
		| awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-10s\033[0m %s\n", $$1, $$2}'

install: ## Install the package and dev dependencies (editable)
	$(PYTHON) -m pip install -e ".[dev,build]"

run: ## Launch the app from source
	cursor-mover --verbose

test: ## Run the test suite with coverage
	pytest --cov=cursor_mover --cov-report=term-missing

lint: ## Check formatting and lint rules
	ruff check .
	ruff format --check .

format: ## Apply formatting and safe lint fixes
	ruff check --fix .
	ruff format .

check: lint test ## Everything CI runs

icon: ## Regenerate assets/icon.png and assets/icon.icns
	$(PYTHON) assets/render_icon.py
	./assets/make_icns.sh

app: ## Build dist/CursorMover.app
	./packaging/build_app.sh

dmg: app ## Build dist/CursorMover-macOS.dmg
	./packaging/create_dmg.sh

clean: ## Remove build and cache artifacts
	rm -rf build dist *.egg-info src/*.egg-info
	rm -rf .pytest_cache .ruff_cache .coverage htmlcov
	find . -name __pycache__ -type d -prune -exec rm -rf {} +
