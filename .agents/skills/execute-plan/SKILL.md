---
name: execute-plan
description: Executes the active plan in `.specify/specs/` referenced by `.specify/spec_ref.json`. Implements tasks from the current phase, updates checkboxes and `completedSession`, ensures strict test adequacy, and commits atomically.
---

# Execute Spec Plan

**Goal**: Implement ONE task at a time. Surgical changes. Verify. Commit. Mark as done in the spec. Repeat.

This is where code gets written. Every task follows the same cycle: read state → plan → implement & test → verify (gate check) → commit → update markdown.

---

## 1. Read State (Mandatory)

Read the following files to establish context:
- `.specify/spec_ref.json`
- The spec markdown file pointed to by `spec_ref.json`.
- Project patterns in `.specify/pattern/feature-workflow.md` or `.specify/extension.yml` (if they exist).

**Identify the current phase**:
1. Check `completedSession` in `spec_ref.json`.
2. If `null`, start at **Phase 1** (or the first phase).
3. Otherwise, find the next phase title in the spec markdown that still has `- [ ]` unchecked tasks.
4. If all phases are done, inform the user the spec is complete.

Execute **one phase per invocation**, unless the user explicitly asks for more.

---

## 2. Execute Tasks (One by One)

For each unchecked task (`- [ ]`) in the current phase, execute the following cycle. Do not batch multiple tasks at once.

### A. Pre-Implementation Planning
Before writing code, explicitly state in your thought process:
- **Assumptions**: What are you assuming?
- **Files to touch**: ONLY list files this task requires.
- **Success criteria**: How will you verify this works?

### B. Write Tests & Implement Code
1. If the task includes tests (as per the spec), write the test files covering the acceptance criteria. **Tests must be derived from the spec, not the implementation.**
2. Write the minimum code needed to satisfy the success criteria.
3. Follow the layer order (e.g., models → repositories → services → API) and create migrations (`poetry run python manage.py makemigrations`) if the task modifies models.

**HARD CONSTRAINTS**:
- Do NOT weaken assertions or delete test cases.
- Do NOT use the test framework's skip/disable mechanism to bypass failing tests.
- Do NOT sneak in "while I'm here" changes (scope creep). Touch only the listed files.

### C. Gate Check (Verify)
Run the project's validation commands. You must pass these before committing.
- **Local (dev)**: `poetry run ruff check src --fix`, `poetry run ruff format src`
- **Tests**: `poetry run pytest src/tests/<app>/ -n0` for specific scopes, or `make test` for the full suite.
- **Review Hooks**: `poetry run pre-commit run ruff --all-files`

Non-zero exit code = STOP. Fix the failure and re-run.

### D. Test Adequacy Review (Mandatory)
A task cannot be committed until these checks pass:
- **Check A (Sufficient coverage)**: Every "Done when" criterion / spec AC must be covered by a test with `file:line` evidence and exact assertions.
- **Check B (Non-shallow)**: No `expect(true)` tautologies or "No error thrown" shallow tests.
- **Check C (Necessary)**: Every test must map back to a requirement. Remove tests that test unrelated things.

### E. Atomic Git Commit
Commit the changes using Conventional Commits. ONE task = ONE commit.
Format: `<type>(<scope>): <description>` (e.g., `feat(transactions): add deposit service logic`).
Include only the files for this task.

### F. Update Spec Markdown
After a successful commit, modify the spec file:
- Change the task's checkbox from `- [ ]` to `- [x]`.

---

## 3. Finalize the Phase

When **all** tasks in the current phase are marked as `[x]`:

1. Update the phase title in the markdown file by appending a checkmark: `## Phase N — Name ✅`.
2. Update the `completedSession` in `.specify/spec_ref.json`:
```json
{
  "name": "{unchanged}",
  "path": "{unchanged}",
  "completedSession": "Phase N — Name",
  "updatedAt": "{YYYY-MM-DD}"
}
```
3. Update the modification footer in the spec markdown file: `<!-- created: ... | modified: YYYY-MM-DD -->`.

---

## 4. Next Step

Upon successfully completing a phase, inform the user of the **next pending phase** and ask if they want to continue the execution.

## Expected Chat Output

```markdown
## execute-plan — Complete

- **Spec**: `{name}`
- **Executed Phase**: {Phase Title}
- **Completed Tasks**: {n}/{total in phase}
- **Session Recorded**: {completedSession}
- **Validation**: {commands run and result}
- **Next Phase**: {Title or "Spec Complete"}
```

If blocked (ambiguous phase, validation failed), explain and list pending items.

## Context

$ARGUMENTS
