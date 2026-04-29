# Planning format for fixes

Write the plan to `/tmp/optimization-plan.md`.

## Design criteria

- Solve the issue without introducing new ones
- Prefer minimal effective changes
- Respect dependencies between fixes
- Estimate regression risk
- Note relevant tests

## Per-issue format

```
### Fix [ID] - [Title]
Priority order: 1..N
Depends on: [IDs]
Regression risk: HIGH | MEDIUM | LOW
Complexity: SIMPLE (< 10 lines) | MODERATE | COMPLEX

Proposed solution:
[Clear approach]

Corrected code:
```lang
// full fix implementation
```

Why this solution:
[Technical rationale]

Tests to run/add:
- [existing test]
- [new test]

Expected side effects:
[Observable behavior change]
```

## Execution summary section

```
## Execution plan

### Recommended order
[Ordered list with time/risk notes]

### Fixes to group (same file/module)
[Group related fixes to reduce churn]

### Backlog
[Low severity fixes to defer]

### Warnings before execution
[Critical notes, for example public API changes]
```
