# Cursor Mover - common development tasks.
# Run `make help` for the list.
#
# Build targets are per-platform: PyInstaller cannot cross-compile, so each
# artifact must be built on its own OS.

.DEFAULT_GOAL := help
.PHONY: help install run test lint format check icon icons app dmg linux deb apt flatpak windows clean

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

icons: ## Regenerate every icon format from cursor_mover.artwork
	$(PYTHON) -m cursor_mover.artwork --size 1024 -o assets/icon.png
	$(PYTHON) -m cursor_mover.artwork -o assets/icon.ico
	./assets/make_icns.sh

icon: icons ## Alias for `icons`

app: ## macOS: build dist/CursorMover.app
	./packaging/build_macos.sh

dmg: app ## macOS: build dist/CursorMover-macOS.dmg
	./packaging/create_dmg.sh

linux: ## Linux: build dist/cursor-mover and the tarball
	./packaging/build_linux.sh

deb: ## Linux: build the .deb package
	./packaging/build_deb.sh

apt: deb ## Linux: build the signed APT repository in dist/apt
	./packaging/build_apt_repo.sh

flatpak: ## Linux: build and install the Flatpak locally
	flatpak-builder --user --install --force-clean build \
		packaging/flatpak/io.github.iaaquibjawed.CursorMover.yml

windows: ## Windows: build dist/CursorMover.exe and the zip (run in PowerShell)
	@echo "Run this in PowerShell instead: .\\packaging\\build_windows.ps1"
	@exit 1

clean: ## Remove build and cache artifacts
	rm -rf build dist *.egg-info src/*.egg-info
	rm -rf .pytest_cache .ruff_cache .coverage htmlcov
	find . -name __pycache__ -type d -prune -exec rm -rf {} +
