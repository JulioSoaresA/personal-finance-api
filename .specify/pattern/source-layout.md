# Source Code Layout

The project uses a standard Django multi-app structure localized inside a `src/` directory.

## Tree
```text
src/
├── authentication/        # Authentication logic and views
├── core/                  # Shared models, exceptions, and base logic
├── locale/                # Translation files
├── personal_finance_api/  # Django project configuration (settings, asgi, wsgi, urls)
├── transactions/          # Domain app for managing accounts, categories, and transactions
└── users/                 # Domain app for user management
```

## Variations
- Most domain apps (e.g., `transactions`, `users`) contain standard Django modules: `models.py`, `views.py`, `urls.py`, `serializers.py`, `admin.py`.
- Some apps use a `services.py` layer to extract business logic from views (e.g., `transactions`).
- Custom errors are placed in `errors.py` (or `exceptions.py` in `core`).
- Tests are typically located inside a `tests/` subdirectory within the app.

## Evidence
- `src/transactions/` includes `services.py`, `errors.py`, and `tests/`.
- `src/users/` includes `errors.py`, `tests/`, and `tests.py`.
- `src/core/` uses `exceptions.py` instead of `errors.py`.

<!-- created: 2026-07-20 | modified: 2026-07-20 -->
