# Testing

## Framework
- **Pytest** with `pytest-django`.

## Directory Structure
- Tests are grouped by app inside a `tests/` subdirectory.
- Example: `src/transactions/tests/`

## Naming Conventions
- Files must be prefixed with `test_` (e.g., `test_models.py`, `test_views.py`, or feature-based `test_transactions.py`).

## Dependencies
- `factory-boy` is used for test data generation.
- `pytest-cov` for coverage.

## Evidence
- `pyproject.toml` dependencies and configurations.
- `src/transactions/tests/test_transactions.py`
- `src/users/tests/`

<!-- created: 2026-07-20 | modified: 2026-07-20 -->
