---
name: code-pattern
description: Extracts and documents the project's codebase architectural and stylistic patterns.
compatibility: Agnostic to framework. Requires project source code directory.
---

<user_context>
$ARGUMENTS
</user_context>

You **must** evaluate the `<user_context>` before proceeding if it is provided.

<objective>
- **Analyze** the repository to infer its architectural and stylistic patterns.
- **Generate and write** the project's codebase pattern specifications into Markdown files located within the `.specify/pattern/` directory.
- These generated files act as the single source of truth for automated review skills. They must accurately reflect the existing structure, providing actionable rules for validating file locations, naming conventions, module responsibilities, and anti-patterns.
- **Framework Agnostic**: Do not assume any specific framework (like Django, React, Express, etc.). You must deduce the language, framework, and package manager from the configuration files present.
</objective>

<operational_restrictions>
1. **Read-Only Mode for Code**: Do not modify existing source code during the analysis phase.
2. **Target Directory**: Only create or update files inside `.specify/pattern/`.
3. **No Hallucination**: Do not assume tech stacks, architectures, folders, or aliases without concrete evidence in the repository. Do not copy patterns from external projects.
4. **Ambiguity Handling**: If a pattern is unclear, document it as "inferred with low confidence" and reference the files used as evidence.
5. **Tool Usage**: Prefer using specific tools like `list_dir` for directory exploration and `grep_search` for finding configurations, instead of broad or expensive commands.
</operational_restrictions>

<execution_steps>
### 1. Stack and Environment Discovery
Determine the project's stack by inspecting root configuration files.
- **Language/Framework**: Look for package manifests (`package.json`, `pyproject.toml`, `requirements.txt`, `go.mod`, `Cargo.toml`, etc.).
- **Dependency Manager**: Look for lock files (`package-lock.json`, `yarn.lock`, `uv.lock`, `poetry.lock`, etc.).
- **Lint/Format/Tests**: Identify configurations for testing and styling.
Record this finding in a single summary line in the final artifact (e.g., "Node.js + NestJS, Jest, npm").

### 2. High-Level Structure Discovery
Scan the repository root (e.g., using `list_dir`) and output an ASCII tree consisting exclusively of existing key directories.
- Highlight folder roles rather than listing every file.
- Identify where the main source code resides (e.g., `src/`, `app/`, `lib/`).
- Identify where tests reside (e.g., `tests/`, `spec/`, or co-located).

### 3. Source Code Structure Discovery
For the main source directory, generate a tree layout reflecting actual found domain boundaries, modules, or apps.
- Map real directories up to a reasonable depth.
- Identify recurring patterns (e.g., do most modules have `controllers/`, `services/`, `models/`? Or is it feature-based like `auth/`, `users/`?).
- Document any anomalies or variations across the codebase in a `source-layout.md` file.

### 4. Naming Convention Inference
Analyze a representative sample of files across different modules and document:
- **Folder Names**: e.g., snake_case, kebab-case.
- **File Names**: e.g., PascalCase for classes, camelCase for utilities.
- **Suffixes**: e.g., `*Service`, `*Controller`, `*.test.ts`.
Rule: Every inferred convention requires at least 2 occurrences to be considered a rule.

### 5. Layer Responsibilities
For each recurring folder or file type, document:
- **Responsibility**: A single sentence explaining its purpose.
- **Permitted Imports**: What it is allowed to depend on (e.g., "services can import models, but not controllers").
- **Restrictions**: What it must not do.
- **Example**: A real path from the current project.

### 6. Anti-Patterns Identification
Derive anti-patterns by comparing the observed structure against common architectural violations for the detected stack.
Recommend a severity level for review:
- **CRITICAL**: Architecture/layering violations.
- **HIGH**: Missing routes/exports, missing core flow tests.
- **MEDIUM**: Naming deviations.
- **LOW**: Minor stylistic issues.
</execution_steps>

<artifacts_to_generate>
Create or update the following files in `.specify/pattern/`:

| File | Required Content |
| --- | --- |
| `README.md` | Index, analyzed scope, date/branch, project summary. |
| `structure.md` | High-level repository tree and tooling summary. |
| `source-layout.md` | Detailed trees for the source code, noting variations. |
| `naming.md` | Inferred conventions for folders, files, and suffixes. |
| `imports.md` | Import rules and layer dependency constraints. |
| `layers.md` | Responsibilities and restrictions per layer. |
| `testing.md` | Test frameworks, directory structures, and conventions. |
| `feature-workflow.md` | Recommended checklist for implementing a new feature. |
| `anti-patterns.md` | List of derived anti-patterns with severity ratings. |

**Artifact Format:**
1. H1 title denoting the scope.
2. Code trees in ` ```text ` blocks.
3. Tables for imports, layers, and severities.
4. An **Evidence** section detailing 3-10 real paths used for inference.
5. **Metadata Footer** (Mandatory) — Must be the last line of the file, preceded by a blank line:
   `<!-- created: YYYY-MM-DD | modified: YYYY-MM-DD -->`
</artifacts_to_generate>

<acceptance_criteria>
[ ] Stack correctly identified from configuration files
[ ] Structure mapped from actual code (no assumptions)
[ ] Conventions backed by evidence (≥ 2 occurrences)
[ ] Layer responsibilities and restrictions clearly defined
[ ] Anti-patterns listed alongside severity ratings
[ ] All files written to .specify/pattern/
[ ] README.md indexes all generated artifacts
[ ] Every .md file includes the metadata footer
</acceptance_criteria>

<final_output>
After saving the files, output the following to the chat:
1. A list of created/updated files.
2. A brief summary of the detected stack and patterns.
3. Any divergences or uncertainties encountered.
4. The completed acceptance checklist.
</final_output>
