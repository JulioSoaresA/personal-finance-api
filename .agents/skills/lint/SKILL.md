---
name: 'lint'
description: 'Triggers the Ruff linter across all files to detect code smells.'
---

# Objective
Run the lint review hook and interpret the results to ensure code quality.

# Pre-requisites
- Ensure you have read and understood the context from `.specify/extension.yml` and `pyproject.toml`.
- The current package manager for this project is uv. Always use `uv run` for python tools unless they run via Docker/make.

# Execution Workflow

Run the following command exactly as defined in the configuration:

```bash
make lint
```

# Interpretation & Output

Analyze the terminal output:
- **Exit Code 0**: The hook succeeded without violations. Output a success report.
- **Exit Code != 0**: The hook failed (e.g., code smells found, tests failed, or formatting issues). Output a failure report detailing what went wrong.

> **Note:** If this hook utilizes `--fix` (like `ruff` or `ruff-format`), note that files may have been automatically modified. Check `git status` or the command output to inform the user of auto-corrections.

# Integration
This skill can be invoked via the path `/lint` by the `review` agent.

# User Input Context
```text
$ARGUMENTS
```
