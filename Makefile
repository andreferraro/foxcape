# Foxcape — local quality gates (GitFlow: develop → release/* → main)
# Requires: make, uv (https://docs.astral.sh/uv/)
#
#   make install      sync deps (incl. dev)
#   make format       ruff format src/ tests/
#   make lint         ruff check src/ tests/
#   make typecheck    mypy src/foxcape
#   make test         pytest offline markers only
#   make check        format + lint + typecheck + test
#   make pre-commit   run all pre-commit hooks

.PHONY: help install sync format lint typecheck test check pre-commit build clean

ROOT := $(abspath $(dir $(lastword $(MAKEFILE_LIST))))
UV ?= uv
SRC := src/foxcape
TESTS := tests

help:
	@echo "Foxcape make targets"
	@echo "  install      uv sync --all-groups"
	@echo "  format       ruff format $(SRC) $(TESTS)"
	@echo "  lint         ruff check $(SRC) $(TESTS)"
	@echo "  typecheck    mypy $(SRC)"
	@echo "  test         pytest (offline; excludes @live)"
	@echo "  check        format + lint + typecheck + test"
	@echo "  pre-commit   pre-commit run --all-files"
	@echo "  build        uv build"
	@echo "  clean        remove build artifacts and caches"

install sync:
	cd "$(ROOT)" && $(UV) sync --all-groups

format:
	cd "$(ROOT)" && $(UV) run ruff format $(SRC) $(TESTS)

lint:
	cd "$(ROOT)" && $(UV) run ruff check $(SRC) $(TESTS)

typecheck:
	cd "$(ROOT)" && $(UV) run mypy $(SRC)

test:
	cd "$(ROOT)" && $(UV) run pytest

check: format lint typecheck test

pre-commit:
	cd "$(ROOT)" && $(UV) run pre-commit run --all-files

build:
	cd "$(ROOT)" && $(UV) build

clean:
	cd "$(ROOT)" && rm -rf build dist .pytest_cache .mypy_cache .ruff_cache htmlcov .coverage
	find "$(ROOT)" -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
