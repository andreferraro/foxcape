# Foxcape — local quality gates (GitFlow: develop → release/* → main)
# Requires: make, uv (https://docs.astral.sh/uv/)
#
#   make install      sync deps (incl. dev)
#   make format       ruff format
#   make lint         ruff check
#   make typecheck    mypy on src/foxcape
#   make test         pytest offline markers only
#   make check        format + lint + typecheck + test
#   make pre-commit   run all pre-commit hooks

.PHONY: help install sync format lint typecheck test check pre-commit build clean

ROOT := $(abspath $(dir $(lastword $(MAKEFILE_LIST))))
UV ?= uv
SRC := src/foxcape
TESTS := tests
MYPY_TARGETS := $(SRC) config.py models.py scraper.py async_scraper.py profiles.py humanizer.py \
	noise_injector.py hardware_spoofing.py turnstile_and_typing.py cadence.py parsers.py proxy_pool.py __init__.py

help:
	@echo "Foxcape make targets"
	@echo "  install      uv sync --all-groups"
	@echo "  format       ruff format ."
	@echo "  lint         ruff check ."
	@echo "  typecheck    mypy $(SRC)"
	@echo "  test         pytest (offline; excludes @live)"
	@echo "  check        format + lint + typecheck + test"
	@echo "  pre-commit   pre-commit run --all-files"
	@echo "  build        uv build"
	@echo "  clean        remove build artifacts and caches"

install sync:
	cd "$(ROOT)" && $(UV) sync --all-groups

lint:
	cd "$(ROOT)" && $(UV) run ruff check src tests *.py

format:
	cd "$(ROOT)" && $(UV) run ruff format src tests *.py

typecheck:
	cd "$(ROOT)" && $(UV) run mypy $(MYPY_TARGETS)

test:
	cd "$(ROOT)" && $(UV) run pytest

check: format lint typecheck test

pre-commit:
	cd "$(ROOT)" && $(UV) run pre-commit run --all-files

build:
	cd "$(ROOT)" && $(UV) run python -m build

clean:
	cd "$(ROOT)" && rm -rf build dist .pytest_cache .mypy_cache .ruff_cache htmlcov .coverage
	find "$(ROOT)" -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
