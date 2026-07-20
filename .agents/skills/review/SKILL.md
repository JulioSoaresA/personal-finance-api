---
name: review
description: Performs an automated analysis of the proposed changes, looking for inconsistencies, ambiguities, and duplications, generating a consolidated report.
compatibility: 'Requires pattern configuration in the .specify/ directory'
---

# User Input

```text
$ARGUMENTS
```

You **must** analyze the arguments provided by the user, if any, before starting execution.

## Initial Validations

Before starting the code analysis, follow these preparatory steps:

1. **Environment Check**:
   - Inspect the project root for the `pyproject.toml` file to understand the available execution scripts (for example, prioritizing scripts defined in the project over generic commands).
   - Identify the dependency manager. The project standard is to use `uv`, so prioritize `uv run` and the defined `Makefile` targets (e.g., `make lint`, `make format`) over `poetry`.

2. **Pre-Hook Execution**:
   - Check for the existence of the `.specify/extension.yml` file. If it does not exist, silently skip this step.
   - If it exists, look for configurations in the `hooks.review` section.
   - Filter entries where the `enabled` property is strictly `true`.
   - For each listed command (e.g., `review.lint`), adapt the format by replacing dots with a slash (e.g., `/lint`).
   - Present the execution in the following format and wait for completion before continuing:

   ```text
   ## Hook Execution
   **Extension**: {extension_name}
   **Action**: `/{adapted_command}`
   **Original Command**: {original_command}
   
   Waiting for hook execution result...
   ```

## Main Goal

Compare the changes from the current branch against the base branch (defaulting to `dev` or `development`, unless otherwise specified in the user arguments) to identify:
- Duplicated code snippets or business rules.
- Ambiguous terms or inconsistencies in the implementation.

## Golden Rule (Restrictions)

- **Read-Only Mode**: You are strictly forbidden from creating, modifying, or deleting any source code project files during this process. Your role is exclusively analytical. You are, however, allowed and expected to write your final report to the `.specify/reviews/` directory and update the `.specify/review_ref.json` file.

## Execution Roadmap

### 1. Context Absorption
- Read the project patterns documentation located in the `.specify/pattern/` directory.
- Stop execution and return a clear error if no Markdown (`.md`) files are found in this directory.

### 2. Duplication Scan
- Map out nearly identical logic or specifications that could be abstracted.
- Flag these points as low-quality snippets requiring refactoring.

### 3. Ambiguity Scan
- Highlight generic terms, non-standard abbreviations, or vague adjectives that hinder comprehension.
- List areas of the code containing technical debt markers such as `TODO`, `FIXME`, `BUG`, or `HACK`.

### 4. Risk Classification (Severity)
Classify each finding from your scan using the following criteria:
- **CRITICAL**: Violates structural rules or directly fails the criteria established in the `pattern/` folder.
- **HIGH**: Presence of conflicting/duplicated logic or requirements, untestable acceptance criteria, or potential security/performance flaws.
- **MEDIUM**: Use of non-standard project nomenclature, lack of tests for alternative flows, or poorly specified use cases.
- **LOW**: Opportunities to improve readability, code style, or minor harmless redundancies.

### 5. Final Report Generation
- **Determine the Next Review Number**:
  1. Look at the files in `.specify/reviews/` matching `^\d{3}_.*\.md$`.
  2. Next number = `max(NNN) + 1`, or `001` if empty.
  3. Generate a **snake_case** slug based on the current branch or topic being reviewed.
- You must read the `.specify/templates/artifact-template.md` file (if it exists) before proceeding. Your report must strictly follow the structure defined there (header, hooks, summary, files to modify, findings table).
- **Save the Report**: You **must** save the report to disk at `.specify/reviews/{NNN}_{slug}.md`. Update `.specify/review_ref.json` with the current review path, similar to how specs are tracked.
- **Header**: Fill in with the real data of the analyzed diff (`current_branch` vs `dev`), date, change summary (via `git diff --stat`), and the detected package manager.
- **Affected Files**: List only the file paths that have at least one pending issue raised in your findings.
- **Findings Table**: Structure the points with the exact template columns:

| ID | Category | Severity | Location(s) | Summary | Recommendation |
|---|---|---|---|---|---|
| A01 | Duplication | HIGH | `src/*/*:L10-L15` | Repeated validation logic | Centralize in an auxiliary service |

- **Ideal Scenario**: If there are no actionable violations, replace the empty table with the **Report without issues** block present in the template.

### Expected Agent Behavior

- **Token Objectivity**: Focus only on real problems requiring developer action. Avoid excessive documentation or verbosity.
- **Smooth Progression**: Read files incrementally; do not load all content into your mental analysis at once.
- **Table Limitation**: If there are many errors, cap the table at a maximum of 50 rows, summarizing the rest to save tokens.
- **Precision, not Generalization**: Point out flaws using real code examples, citing exact locations, rather than listing general rules.
- **Absolute Integrity**: Never invent or hallucinate problems/sections and **NEVER modify the files**.
