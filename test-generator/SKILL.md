---
name: test-generator
description: "Generate and run automated tests (unit, integration, API, E2E) adapted to the project stack. Use when the user asks to add tests, improve coverage, or test specific modules or flows. Runs a three-subagent pipeline: stack analysis -> test generation -> execution with report and user confirmation."
allowed-tools: Read, Glob, Grep, Bash, Write, Edit, Task
model: claude-sonnet-4-5
---

# Test generator (three subagents)

## When to use

- Missing tests or low coverage
- Before refactoring (safety net)
- After implementing a feature
- Explicit requests to add or generate tests

## Goal

Generate realistic, stack-aligned tests and run them only after explicit user approval.

## Pipeline overview

```
Parent Agent
  -> Subagent 1: Stack Analyzer (write /tmp/test-context.md)
  -> Subagent 2: Test Generator (write tests, /tmp/test-manifest.md)
  -> Pause for user approval
  -> Subagent 3: Test Runner (write TEST_REPORT.md)
```

## Phase 1: Parent reconnaissance

1. Identify scope from the prompt (file, module, or test type)
2. Inspect project config (package.json, pyproject.toml, etc.)
3. Find existing tests and conventions
4. Provide scope/context to Subagent 1

## Phase 2: Subagent 1 (Stack Analyzer)

Detect language, test frameworks, conventions, and target files. Write `/tmp/test-context.md`.

## Phase 3: Subagent 2 (Test Generator)

Use the patterns in [references/test-patterns.md](references/test-patterns.md). Write tests and
record a manifest in `/tmp/test-manifest.md` with file paths, test types, coverage, and run commands.

## Phase 4: Pause and confirm

Summarize generated tests and ask whether to run all tests, only a category, or none.

## Phase 5: Subagent 3 (Test Runner)

Run approved suites, capture failures, and write `TEST_REPORT.md`. Clean up temp files.

## Notes

- Use realistic domain data in tests.
- Align with existing test style when present.
- Never run tests without explicit user confirmation.
