---
name: code-optimizer
description: "Deep code optimization and bug hunting. Use when the user asks to optimize performance, find bugs, analyze edge cases, detect memory leaks, or review code quality. Runs a three-subagent pipeline: analyzer -> planner -> executor with explicit user confirmation before changes."
allowed-tools: Read, Glob, Grep, Bash, Edit, Write, Task
model: claude-opus-4-5
---

# Code optimizer (three subagents)

## When to use

- Performance problems or slow code
- Suspected memory leaks or resource misuse
- Silent bugs or edge cases
- Deep code review before release

## Goal

Identify and fix bugs, inefficiencies, and resource issues using a three-stage pipeline with required user confirmation before applying changes.

## Pipeline overview

```
Parent Agent
  -> Subagent 1: Analyzer (write /tmp/code-analysis.md)
  -> Subagent 2: Planner (write /tmp/optimization-plan.md)
  -> Pause for user approval
  -> Subagent 3: Executor (apply fixes, write OPTIMIZATION_REPORT.md)
```

## Phase 1: Parent reconnaissance

1. Determine scope (files, directory, or full codebase)
2. Collect context (CLAUDE.md, package.json, requirements.txt, etc.)
3. Run baseline tests if present
4. Pass scope and context to Subagent 1

## Phase 2: Subagent 1 (Analyzer)

Use the analysis checklist and output format in [references/analysis-checklist.md](references/analysis-checklist.md).
Write `/tmp/code-analysis.md`.

## Phase 3: Subagent 2 (Planner)

Use the plan template in [references/plan-format.md](references/plan-format.md).
Write `/tmp/optimization-plan.md`.

## Phase 4: Pause and confirm

Present the plan summary and ask the user whether to apply all fixes, only critical/high, or a subset. Do not continue without explicit confirmation.

## Phase 5: Subagent 3 (Executor)

Apply only approved fixes, run tests for high-risk changes, and write `OPTIMIZATION_REPORT.md`.

## Notes

- Subagents 1 and 2 never modify files.
- The pause before execution is mandatory.
- This skill complements `refactoring` (structure/readability) with correctness and performance focus.
