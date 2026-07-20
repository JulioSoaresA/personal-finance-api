---
name: 'init'
description: 'Bootstraps and configures review hooks (lint, format, test) based on the project extension specifications using templates.'
compatibility: 'Requires .specify/extension.yml'
metadata:
  author: 'juliosoares@b2bit.company'
---

# User Input
```text
$ARGUMENTS
```

## Objective
Initialize or update the review hook skills (`lint`, `format`, `test`) using the configuration defined in `.specify/extension.yml`.

## Instructions

1. **Parse Configuration**
   - Read `.specify/extension.yml` and inspect the `hooks.review` block.
   - Identify all hooks (e.g., `lint`, `format`, `test`) where `enabled: true`.

2. **Read Skill Template**
   - Load the template file located at `.agents/skills/init/resources/skill_template.md`.

3. **Scaffold Skills**
   For each enabled hook:
   - Create the directory `.agents/skills/<hook_name>/` if it does not already exist.
   - Using the template, replace the following placeholders with data from `extension.yml`:
     - `{{HOOK_NAME}}` -> The name of the hook (e.g., `lint`)
     - `{{DESCRIPTION}}` -> The `description` field from the YAML
     - `{{COMMAND}}` -> The `command` field from the YAML
   - Save the populated text to `.agents/skills/<hook_name>/SKILL.md`.

4. **Completion Report**
   After processing, present a short markdown table to the user summarizing:
   - Which skills were created or updated.
   - The command configured for each skill.
   - Advise the user that they can now invoke `/review`.

## Constraints
- **Do not modify** `.specify/extension.yml`.
- Do not create a skill for a hook if it is `enabled: false`.
- Only use the exact commands specified in the configuration file.
