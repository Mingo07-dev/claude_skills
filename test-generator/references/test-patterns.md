# Test patterns and conventions

## Quality rules

- Test names should describe behavior and condition: "should [behavior] when [condition]"
- One conceptual assertion per test (multiple expects allowed if related)
- Use realistic domain data, avoid placeholders
- Mock external dependencies only (DB, API, filesystem, timers)
- Add setup/teardown where needed

## Unit tests

Focus on a single function or class with external dependencies mocked.

Jest/Vitest:

```typescript
import { describe, it, expect, vi } from "vitest";
import { myFunction } from "../path/to/module";

describe("myFunction", () => {
  it("should return null when user email is not found", () => {
    // ...
  });
});
```

pytest:

```python
import pytest
from path.to.module import my_function

class TestMyFunction:
    def test_should_return_none_when_user_email_missing(self):
        ...
```

## Integration tests

Use real infrastructure or in-memory substitutes (SQLite, testcontainers).

```typescript
describe("UserRepository Integration", () => {
  let db: TestDatabase;

  beforeAll(async () => { db = await createTestDatabase(); });
  afterAll(async () => { await db.destroy(); });
  afterEach(async () => { await db.truncate("users"); });

  it("should persist and retrieve user correctly", async () => {
    // ...
  });
});
```

## API tests

Validate status codes, response shape, headers, and error cases.

```typescript
describe("POST /api/payments", () => {
  it("should return 201 with payment id when payload is valid", async () => {
    const res = await request(app)
      .post("/api/payments")
      .set("Authorization", `Bearer ${testToken}`)
      .send({ amount: 1000, currency: "eur" });
    expect(res.status).toBe(201);
    expect(res.body).toMatchObject({ id: expect.any(String) });
  });
});
```

Include:
- auth (valid token, expired token, missing auth)
- validation (missing fields, wrong types)
- edge cases (not found, conflict, payload too large)

## E2E tests

Use Playwright or Cypress for critical flows (login, checkout, signup).

```typescript
test("user can complete checkout flow", async ({ page }) => {
  await page.goto("/checkout");
  await page.getByRole("button", { name: "Pay now" }).click();
  await page.getByLabel("Card number").fill("4242424242424242");
  await expect(page.getByText("Payment confirmed")).toBeVisible();
});
```

Use page object models for complex flows and avoid fixed sleeps.

## Manifest format

Write to `/tmp/test-manifest.md`:

- Test file path
- Test type (unit/integration/api/e2e)
- Functions or endpoints covered
- Number of test cases
- Command to run the suite

## Stack detection defaults

| Language | Test framework | E2E | Default command |
| --- | --- | --- | --- |
| TypeScript/JS | Jest | Playwright | `npx jest` / `npx playwright test` |
| TypeScript/JS | Vitest | Playwright | `npx vitest` |
| TypeScript/JS | Mocha | Cypress | `npx mocha` |
| Python | pytest | Playwright | `python -m pytest` |
| Python | unittest | - | `python -m unittest` |
| Go | testing | - | `go test ./...` |
| Rust | cargo test | - | `cargo test` |
| Java | JUnit 5 | Selenium | `mvn test` / `gradle test` |
| Ruby | RSpec | Capybara | `bundle exec rspec` |
