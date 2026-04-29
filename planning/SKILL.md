---
name: planning
description: "Create detailed multi-session plans with a single-pass analysis of files and changes. Use when a task needs a structured plan to be executed in later sessions or across multiple files/modules."
argument-hint: "Task or focus (e.g., 'refactor auth', 'new APIs')"
---

# Multi-session planning

## When to use

- The work will be executed in future sessions
- You need a reproducible plan without prior context
- The task spans multiple files or distinct logic areas

## Goal

- Analyze files once
- Produce plans that are executable without prior memory

## Rules

- Plans must be detailed and step-by-step.
- Split into separate plan files when distinct features or areas are involved.
- Group steps by shared files or logic to keep each plan focused.

## Procedure

1. Ask clarifying questions if details are missing
2. Analyze repo, files, and dependencies in a single pass
3. List files involved and the changes per block
4. Split into multiple plans when needed
5. For each plan include:
   - Scope and purpose
   - Files involved
   - Detailed changes per file
   - Sequential steps with expected output
   - Suggested verifications/tests

## Output

- One or more plan files, grouped by file/logic
- Use the template: [assets/plan-template.md](./assets/plan-template.md)