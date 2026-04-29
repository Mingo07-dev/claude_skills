---
name: project-startup
description: "Analyze a project and generate .agent files for onboarding. Use to map the codebase, summarize docs, and bootstrap .agent/main.md, .agent/planning.md, and plans."
argument-hint: "Path or focus (e.g., 'analyze repo', 'include docs')"
---

# Project analysis and .agent bootstrap

## When to use

- Quick onboarding for a new project
- Mapping the codebase and key docs
- Setting up .agent rules and plans

## Expected output

- .agent/main.md with concise, useful context
- .agent/planning.md (empty)
- .agent/plans/ for multi-step plans only
- .agent/claude.md, .agent/codex.md, .agent/copilot.md with a minimal rule
- Use template: [assets/main-template.md](./assets/main-template.md)

## Procedure

1. Gather context
   - Read README, docs, and key config files
   - Identify entrypoints, core modules, scripts, and critical flows

2. Map the codebase
   - List relevant folders and files
   - Add one-line descriptions for key items

3. Create the .agent folder
   - Create .agent/ and .agent/plans/
   - Create empty .agent/planning.md

4. Write .agent/main.md (minimal but complete)
   Include:
   - Project purpose and goals
   - High-level flow
   - Rules, formats, and conventions
   - Full codebase structure
   - Key docs and locations

   Add these rules (concise):
   - Do not create a plan for small, simple fixes.
   - For multi-step tasks, read .agent/planning.md and write a plan to .agent/plans/.
   - Ask questions when critical details are missing.
   - Update .agent/main.md if you change its knowledge base and notify the user.
   - If a git repo exists, record current commit hash and date and keep it updated.
   - If asked to verify freshness, compare current state to the commit recorded in .agent/main.md.

5. Create agent files
   - .agent/claude.md, .agent/codex.md, .agent/copilot.md
   - Minimal content like: "Read .agent/main.md on every prompt."

6. Plans
   - Create a plan file only when needed for multi-step work.
   - Suggested name: YYYYMMDD-HHMM-<slug>.md

## Quality criteria

- Concise, no duplicates
- Complete but readable structure
- Consistent with project docs
- Update .agent/main.md as knowledge changes
