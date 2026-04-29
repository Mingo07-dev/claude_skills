---
name: refactoring
description: "Refactor code for readability and structure without changing behavior. Use when the user asks to refactor, clean up, improve readability, rename variables, extract functions, or reduce code smells. Runs a two-subagent pipeline: reader/planner then executor."
allowed-tools: Read, Glob, Grep, Bash, Edit, Write, Task
model: claude-sonnet-4-5
---

# Refactoring pipeline (two subagents)

## When to use

- Code is hard to read or maintain
- Functions are too long or doing too many things
- Naming is unclear or inconsistent
- The user explicitly asks for refactoring or clean code

## Goal

Produce human-readable, well-structured code without behavior changes.

## Pipeline overview

```
Parent Agent
  -> Subagent 1: Reader/Planner (analyze, plan, no edits)
  -> Subagent 2: Executor (apply plan, run tests, report)
```

## Phase 1: Parent scope and baseline

1. Determine scope (files, directory, or full codebase)
2. Scan for existing tests
3. Run tests if present and save baseline output
4. Pass scope and context to Subagent 1

## Phase 2: Subagent 1 (Reader/Planner)

Use the checklist and plan format in [references/checklist.md](references/checklist.md).
Write the plan to `/tmp/refactoring-plan.md`.

## Phase 3: Subagent 2 (Executor)

Apply the plan from `/tmp/refactoring-plan.md` and follow the execution rules in
[references/execution.md](references/execution.md). Write `REFACTORING_REPORT.md`.

## Phase 4: Parent validation

1. Read `REFACTORING_REPORT.md`
2. Compare tests vs baseline (if any)
3. Summarize changes and deviations

## Notes

- Subagent 1 never edits files.
- Subagent 2 must follow the plan exactly.
- Do not rename public APIs without explicit confirmation.
