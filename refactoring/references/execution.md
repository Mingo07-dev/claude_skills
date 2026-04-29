# Refactoring execution rules

## Before starting

- Read the full plan
- Identify high-risk changes
- Run tests if available to capture baseline

## During execution

For each file (in plan order):
1. Read the full file before edits
2. Apply changes in order
3. Verify syntax after each change
4. If high risk and tests exist, run tests
5. Do not add unplanned features
6. Do not modify files outside the plan
7. If you find an unplanned issue, document and continue

## Quality rules

### Naming
- Functions: verb + descriptive noun (getUserById, calculateDiscount)
- Variables: descriptive nouns (userCount, not cnt)
- Booleans: is/has/should/can prefix
- Constants: UPPER_SNAKE_CASE
- Avoid abbreviations (usr -> user, cfg -> config)

### Function structure
- Aim for ~25 lines or less
- Single responsibility
- Use early returns to reduce nesting
- Keep parameters to 3-4 (group in objects when needed)

### Formatting
- Follow project conventions (tabs/spaces, quotes)
- Use blank lines to separate logical sections
- Group imports (stdlib -> external -> internal)

## After execution

1. Run tests if present
2. Write `REFACTORING_REPORT.md`:
   - Files changed with short descriptions
   - Deviations from plan and reasons
   - Failed tests (if any)
   - Follow-up recommendations
3. Delete `/tmp/refactoring-plan.md`
