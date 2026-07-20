# High-Level Repository Structure

## Stack and Tools
- **Language**: Python 3.11+
- **Framework**: Django 5.2.5 with Django REST Framework
- **Dependency Manager**: uv
- **Linting/Formatting**: Ruff, Black, pre-commit
- **Testing**: Pytest (with pytest-django, pytest-cov, pytest-celery)

## Evidence
- `pyproject.toml` containing project dependencies and tool configs.
- `uv.lock` for dependency locking.
- `.pre-commit-config.yaml` for pre-commit hooks.

## Repository Tree
```text
.
├── .agents/          # Custom AI agent skills and configurations
├── .specify/         # Pattern specifications and extension configurations
├── docs/             # Project documentation
├── src/              # Main source code (Django apps and project config)
├── .pre-commit-config.yaml # Pre-commit hooks
├── Dockerfile        # Docker setup
├── Makefile          # Common task commands
├── docker-compose.yml # Local services configuration
├── pyproject.toml    # Python project configuration (uv, pytest, ruff)
└── uv.lock           # Locked dependencies
```

<!-- created: 2026-07-20 | modified: 2026-07-20 -->
