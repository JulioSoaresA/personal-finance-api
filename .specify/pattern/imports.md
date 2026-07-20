# Import Rules & Dependencies

| Layer / File | Permitted Imports | Restrictions |
| --- | --- | --- |
| `views.py` | `serializers`, `models`, `services` | Should not contain complex business logic. Delegate to `services.py`. |
| `serializers.py` | `models` | Should not import `views`. |
| `services.py` | `models`, other `services` | Should not handle HTTP requests/responses or import `views`. |
| `models.py` | Django DB utilities, other `models` | Should not import `serializers` or `views` to avoid circular dependencies. |

**Cross-App Imports:**
- Domain apps can import shared utilities from `core`.
- Avoid circular dependencies between domain apps.

## Evidence
- Typical Django and DRF architecture observed across `src/transactions/` and `src/users/`.
- `services.py` exists in `src/transactions/` decoupling logic from `views.py`.

<!-- created: 2026-07-20 | modified: 2026-07-20 -->
