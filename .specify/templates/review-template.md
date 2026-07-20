# Automated Review — {current-branch} vs {base-branch}

**Date**: YYYY-MM-DD
**Branch**: {current-branch}
**Base**: {base-branch}
**Scope**: {N} files · +{lines-added} / −{lines-removed} lines · {M} commits
**Package Manager**: uv

> Fill the placeholders with real comparison data (`git diff`, `git log`, etc.).
> If the default base branch (`dev`) does not exist, use the project's alternative (e.g., `development`, `main`) and note it in **Base**.

---

## Hooks

> Include only when hooks from `hooks.automated-review` (in `.specify/extension.yml`) are executed.

| Extension | Command               | Status                |
| --------- | --------------------- | --------------------- |
| {name}    | `{executed command}`  | ✅ passed / ❌ failed |

---

## Summary

{1–3 sentences with the verdict: approved, approved with reservations, or blocked. Include totals by severity.}

- **CRITICAL**: {n}
- **HIGH**: {n}
- **MEDIUM**: {n}
- **LOW**: {n}

---

## Files Requiring Modification

> List only unique paths with pending actions, extracted from the findings. Omit files with no necessary changes.

- `{relative/path/to/file1.ext}`
- `{relative/path/to/file2.ext}`

---

## Findings

> Limit the table to **50 rows**; summarize the excess at the end of the section.
>
> **Suggested Categories**: `Code Standard`, `Duplication`, `Ambiguity`, `Test Coverage`, `Pending Marker` (TODO/FIX/BUG).
>
> **Severities**: `CRITICAL`, `HIGH`, `MEDIUM`, `LOW`.

| ID  | Category          | Severity | Location(s)                            | Summary                        | Recommendation              |
| --- | ----------------- | -------- | -------------------------------------- | ------------------------------ | --------------------------- |
| A1  | Code Standard     | CRITICAL | `src/transactions/api/views.py`:L10-25 | {objective description}        | {concrete and actionable}   |
| A2  | Duplication       | HIGH     | `src/transactions/services.py`:L1-20; `src/transactions/services.py`:L5-24 | {description} | {action} |
| A3  | Ambiguity         | MEDIUM   | `src/transactions/serializers.py`:L42  | {description}                  | {action}                    |
| A4  | Pending Marker    | MEDIUM   | `src/core/utils.py`:L7                 | `# TODO: …`                    | {action}                    |
| A5  | Code Standard     | LOW      | `src/tests/transactions/api/test_views.py`:L3 | {description}           | {action}                    |

---

## Report Without Issues

> Use this block **instead of** **Files Requiring Modification** and **Findings** when there are no actionable violations.

**Status**: ✅ Approved — no relevant violations found.

| Metric              | Value                                                     |
| ------------------- | --------------------------------------------------------- |
| Analyzed files      | {N}                                                       |
| Consulted patterns  | {sources read in `.specify/pattern/`}                     |
| Executed hooks      | {n}                                                       |
| Findings            | 0                                                         |

---

## Notes

> Optional. Analysis limitations, restricted scope, unread files, disabled hooks, etc.

- {optional note}

<!-- created: 2026-06-23 | modified: 2026-06-25 -->