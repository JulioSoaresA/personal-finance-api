# Layers & Responsibilities

| File Type | Responsibility | Restrictions | Example Path |
| --- | --- | --- | --- |
| `models.py` | Defines database schema and relationships. | No presentation or external API logic. | `src/transactions/models.py` |
| `views.py` | Handles HTTP requests, validation orchestration, and responses. | No complex business logic. | `src/transactions/views.py` |
| `serializers.py` | Converts complex data types (models) to/from native Python datatypes. | Should not perform database side-effects outside of `create/update`. | `src/transactions/serializers.py` |
| `services.py` | Contains core business logic and cross-model orchestration. | Agnostic to HTTP/web layer context. | `src/transactions/services.py` |
| `errors.py` / `exceptions.py` | Defines domain-specific custom exception classes. | None. | `src/transactions/errors.py` |
| `urls.py` | Maps URL routes to view functions or classes. | No business logic. | `src/transactions/urls.py` |

## Evidence
- `src/transactions/models.py`
- `src/transactions/views.py`
- `src/transactions/serializers.py`
- `src/transactions/services.py`
- `src/transactions/errors.py`

<!-- created: 2026-07-20 | modified: 2026-07-20 -->
