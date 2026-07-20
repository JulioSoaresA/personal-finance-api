# Naming Conventions

## Folders
- **Django Apps**: snake_case (e.g., `transactions`, `authentication`, `personal_finance_api`).

## Files
- **Standard Modules**: snake_case (e.g., `models.py`, `views.py`, `serializers.py`).
- **Test Files**: Must start with `test_` (e.g., `test_transactions.py`, `test_accounts.py`).

## Classes (Inferred based on Django/DRF standards)
- **Models**: PascalCase (e.g., `Transaction`, `User`).
- **Serializers**: PascalCase with `Serializer` suffix (e.g., `TransactionSerializer`).
- **Views**: PascalCase with `View` or `ViewSet` suffix.

## Evidence
- `src/transactions/tests/test_accounts.py`
- `src/transactions/tests/test_categories.py`
- `src/users/views.py`

<!-- created: 2026-07-20 | modified: 2026-07-20 -->
