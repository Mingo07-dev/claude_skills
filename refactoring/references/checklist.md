# Refactoring checklist and plan format

## Code smell checklist

### Readability
- Non-descriptive names (a, b, tmp, data, val, flag)
- Misleading names (name does not match behavior)
- Cryptic abbreviations
- Magic numbers or strings without context
- Missing or noisy comments

### Structure
- Long functions (> 20-30 lines)
- Multiple responsibilities in one function
- Deep nesting (> 3-4 levels)
- Duplicated logic (DRY violations)
- God functions or objects
- Feature envy

### Formatting
- Inconsistent indentation or spacing
- Disorganized imports
- Very large files (> 300-400 lines)

### Design
- Mixed responsibilities (business logic in controllers)
- Hardcoded dependencies instead of injection
- Error handling missing or inconsistent
- Missing early returns

## Plan format (write to /tmp/refactoring-plan.md)

```
FILE: src/path/to/file.ext
PRIORITY: HIGH/MEDIUM/LOW
RISK: HIGH/MEDIUM/LOW

PLANNED CHANGES:
1. [Rename function X -> descriptiveName]
   Reason: X is ambiguous

2. [Extract validation into validateInput()]
   Reason: validation is mixed with saving logic

3. [Replace magic number 86400 with SECONDS_IN_DAY]
   Reason: number is not self-explanatory

ORDER OF EXECUTION:
[optimal sequence]

DEPENDENCIES:
[if change A depends on change B]
```

## Summary format

- Total files to change: N
- High-risk changes: list
- Safe changes (rename/format only): list
- Complexity estimate: SIMPLE / MODERATE / COMPLEX
- Recommendation: one batch or multiple batches
