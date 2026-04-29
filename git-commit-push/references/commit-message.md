# Commit message rules (Conventional Commits)

## Type selection

Choose the dominant type based on the diff:

- feat: new feature, component, route, or API
- fix: bug fix
- refactor: restructure without behavior change
- docs: documentation changes
- chore: deps, config, build, scripts
- test: tests added or changed
- style: formatting only
- perf: performance improvement
- ci: CI/CD changes

## Optional scope

Use a module or area name, for example `feat(auth)` or `fix(checkout)`.

## Subject line format

```
<type>(<scope>): <imperative, lowercase summary>
```

Rules:
- Max 72 characters
- Imperative verbs: add, fix, update, remove, implement, configure
- No trailing period
- Match repo language (English unless the repo uses Italian)

Examples:

```
feat(checkout): implement stripe elements form
fix(webhook): handle idempotency key collisions
refactor(auth): extract token validation to service
```

## Body structure (optional sections)

Include only sections with content:

```
## Changes
<grouped file list with short reasons>

## Completed Steps
<steps from plan.md if present>

## Architecture Decisions
<decision notes>

## Commands Run
<non-obvious commands with side effects>

## Notes
<any extra context>
```

Rules:
- Omit empty sections
- Keep to ~25 lines total
- Use relative paths
- Do not include trivial commands like `git status`

## Commit command example

```bash
git commit \
  -m "feat(checkout): implement stripe elements form" \
  -m "## Changes
src/app/checkout/page.tsx - new checkout page
src/components/CheckoutForm.tsx - stripe form and validation

## Commands Run
npm install @stripe/stripe-js @stripe/react-stripe-js"
```
