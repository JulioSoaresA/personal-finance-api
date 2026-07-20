---
name: create-plan
description: Break features into GRANULAR, ATOMIC tasks. Creates numbered task specs in `.specify/specs/` and updates `.specify/spec_ref.json`. Use when planning tasks for a feature implementation.
---

# Tasks Spec Creation

**Goal**: Break the feature into GRANULAR, ATOMIC tasks. Establish clear dependencies, use the right tools, and create a sequential phase execution plan based on the project's architecture layers.

**Skip this phase when:** There are ≤3 obvious steps. In that case, tasks are implicit — go straight to Execute and list them inline in your implementation plan.

## Why Granular Tasks?

| Vague Task (BAD) | Granular Tasks (GOOD)             |
| ---------------- | --------------------------------- |
| "Create form"    | T1: Create email input component  |
|                  | T2: Add email validation function |
|                  | T3: Create submit button          |
|                  | T4: Add form state management     |
|                  | T5: Connect form to API           |
| "Implement auth" | T1: Create login form             |
|                  | T2: Create register form          |
|                  | T3: Add token storage utility     |
|                  | T4: Create auth API service       |
|                  | T5: Add route protection          |

**Benefits of granular:**
- **Agents don't err** - Single focus, no ambiguity
- **Easy to test** - Each task = one verifiable outcome
- **Clean commits** - Each task = one atomic, revertable commit
- **Errors isolated** - One failure doesn't block everything

**Rule**: One task = ONE of these:
- One component
- One function
- One API endpoint
- One file change

---

## Process

### 1. Read Current State (Mandatory)

Before doing anything, you must understand the current state and project patterns:
1. List files in `.specify/specs/` to understand existing specs.
2. Read `.specify/spec_ref.json` (if it exists).
3. Read `.specify/templates/spec-template.md`.
4. Read patterns in `.specify/pattern/feature-workflow.md` to understand the architectural layer order.

### 2. Determine the Next Spec Number

1. Look at the files in `.specify/specs/` matching `^\d{3}_.*\.md$`.
2. Next number = `max(NNN) + 1`, or `001` if empty.
3. Generate a **snake_case** slug based on the user's topic.

### 3. Generate the Test Coverage Matrix (ALWAYS)

This step ALWAYS runs. Look for documented quality and testing standards (`AGENTS.md`, `.github/`, test runner configs). If no guidelines are found, apply strong defaults (domain logic maps 1:1 to spec ACs, all edge cases covered).

**Output contract — render these two sections verbatim into the spec file**:

---

## Test Coverage Matrix

| Code Layer | Required Test Type | Coverage Expectation | Location Pattern | Run Command |
| ---------- | ------------------ | -------------------- | ---------------- | ----------- |
| [layer] | [unit/integration/e2e/none] | [depth target for this layer] | [glob or path pattern] | [command] |

## Gate Check Commands

| Gate Level | When to Use | Command |
| ---------- | ----------- | ------- |
| Quick | After tasks with unit tests only | [unit test command] |
| Full | After tasks with e2e/integration tests | [unit + e2e commands] |
| Build | After phase completion or config/entity-only tasks | [build + lint + all tests] |

---

### 4. Break Into Atomic Tasks & Create Execution Plan

**Task = ONE deliverable**.
- ✅ "Create UserService interface" (one file, one concept)
- ❌ "Implement user management" (too vague, multiple files)

Group tasks into ordered phases based on `.specify/pattern/feature-workflow.md`. Each phase depends on the ones before it; tasks execute sequentially within a phase.

### 5. Validate Before Presenting (MANDATORY)

Before showing tasks to the user, run ALL three pre-approval checks. If any check fails, restructure the tasks.

**Check 1: Task Granularity** — verify each task is atomic.
**Check 2: Diagram-Definition Cross-Check** — verify the execution diagram matches every task's `Depends on` field.
**Check 3: Test Co-location Validation** — verify every task's `Tests` field matches the **Test Coverage Matrix**.

### 6. Save the Spec

Use `.specify/templates/spec-template.md` (if available) or follow this standard markdown structure to write `.specify/specs/{NNN}_{slug}.md`:

```markdown
# [Feature] Tasks

**Design**: `.specs/features/[feature]/design.md`
**Status**: Draft | Approved | In Progress | Done

## Test Coverage Matrix
[Generated in step 3]

## Gate Check Commands
[Generated in step 3]

## Execution Plan
(Phase visual map)
```text
Phase 1 → Phase 2

Phase 1:  T1 ──→ T2
Phase 2:  T3 ──→ T4
```

## Task Breakdown

### T1: [Create X Interface]
**What**: [One sentence: exact deliverable]
**Where**: `src/path/to/file.ts`
**Depends on**: None
**Reuses**: `src/existing/BaseInterface.ts`
**Tools**: MCP `filesystem`
**Done when**:
- [ ] Interface defined
- [ ] Gate check passes
**Tests**: [from matrix]
**Gate**: [from gate commands]

<!-- created: YYYY-MM-DD | modified: YYYY-MM-DD -->
```

Update the state in `.specify/spec_ref.json`:

```json
{
  "name": "{NNN}_{slug}",
  "path": ".specify/specs/{NNN}_{slug}.md",
  "completedSession": null,
  "updatedAt": "{YYYY-MM-DD}"
}
```

### 7. Ask to Execute

Upon completing the creation, **ask the user** if they want to execute the plan now.
- **Yes, execute now** → invoke the `execute-plan` skill.
- **No, just save the plan** → end with a summary.

Do not start execution without explicit confirmation.

---

## Context

$ARGUMENTS
