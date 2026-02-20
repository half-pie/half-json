.PHONY: install sync lint format test check type-check all

# Install dependencies
install:
	uv sync

# Sync dependencies (remove old and install fresh)
sync:
	uv sync

# Run ruff linter
lint:
	uv run ruff check half_json tests

# Run ruff linter with auto-fix
lint-fix:
	uv run ruff check half_json tests --fix

# Run ruff formatter
format:
	uv run ruff format half_json tests

# Run ruff formatter check (CI mode)
format-check:
	uv run ruff format half_json tests --check

# Run type checker
type-check:
	uv run mypy half_json

# Run tests
test:
	uv run pytest

# Run all checks (CI mode)
check: lint format-check type-check test

# Run all checks with auto-fix (local development)
all: lint-fix format type-check test
