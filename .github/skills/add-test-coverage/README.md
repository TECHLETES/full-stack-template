# Testing Playbook Skill

**Objective**: Add comprehensive test coverage for new features, bug fixes, and refactoring using pytest (backend) and Playwright (frontend E2E).

## Quick Start

### For a New Backend Feature

```bash
cd backend

# 1. Copy unit test template
cp ../../../.github/skills/add-test-coverage/templates/backend-test-template.py tests/crud/test_myfeature.py

# 2. Edit and add unit tests for CRUD operations
# 3. Run tests
pytest tests/crud/test_myfeature.py -v

# 4. Copy integration test template
cp ../../../.github/skills/add-test-coverage/templates/backend-test-template.py tests/api/routes/test_myfeature.py

# 5. Edit and add route tests
# 6. Run tests
pytest tests/api/routes/test_myfeature.py -v

# 7. Check coverage
./scripts/test.sh
```

### For a New Frontend Feature

```bash
cd frontend

# 1. Copy E2E test template
cp ../../.github/skills/add-test-coverage/templates/frontend-test-template.tsx tests/myfeature.spec.ts

# 2. Edit and add user workflow tests
# 3. Run tests
npm run test:ui  # or: npm run test (headless)

# 4. Verify no console errors
npm run test 2>&1 | grep -i "error\|warning"
```

## File Locations

```
.github/skills/add-test-coverage/
├── SKILL.md                              # Main guide (you are here)
├── README.md                             # Quick start
├── templates/
│   ├── backend-test-template.py          # Pytest patterns (~200 lines)
│   └── frontend-test-template.tsx        # Playwright patterns (~250 lines)
└── references/
    └── CHECKLIST.md                      # Pre-test checklist (80+ items)
```

**Related Documentation:**
- [Backend Instructions](../../../instructions/backend.instructions.md#testing-patterns) — Full testing patterns
- [Frontend Instructions](../../../instructions/frontend.instructions.md#testing-with-playwright) — Full E2E guide
- [Scaffold API Endpoint](../scaffold-api-endpoint/SKILL.md) — How to add new resources (includes test section)

## Real Example: Items Resource

### Backend Unit Test

```python
# backend/tests/crud/test_item.py
def test_create_item(db: Session) -> None:
    from app import crud
    from backend.models import ItemCreate
    from tests.utils.user import create_random_user

    user = create_random_user(db)
    item_in = ItemCreate(title="Laptop", description="Dell XPS")

    item = crud.create_item(session=db, item_in=item_in, owner_id=user.id)

    assert item.id
    assert item.title == "Laptop"
    assert item.owner_id == user.id
```

### Backend Integration Test

```python
# backend/tests/api/routes/test_items.py
def test_create_item_endpoint_success(
    client: TestClient,
    normal_user_token_headers: dict[str, str],
) -> None:
    data = {"title": "Laptop", "description": "Dell XPS"}
    response = client.post(
        "/api/v1/items/",
        headers=normal_user_token_headers,
        json=data,
    )

    assert response.status_code == 200
    content = response.json()
    assert content["title"] == data["title"]
    assert content["owner_id"]
```

### Frontend E2E Test

```typescript
// frontend/tests/items.spec.ts
test("User can create an item", async ({ page }) => {
  await page.goto("/items")
  await page.getByRole("button", { name: "Add Item" }).click()
  await page.getByLabel("Title").fill("Laptop")
  await page.getByLabel("Description").fill("Dell XPS")
  await page.getByRole("button", { name: "Create" }).click()

  await expect(page.getByText("Item created successfully")).toBeVisible()
  await expect(page.getByText("Laptop")).toBeVisible()
})
```

## Test Levels Explained

| Level | Tool | Speed | Scope | When to Use |
|-------|------|-------|-------|------------|
| **Unit** | pytest | Fast | CRUD functions | Business logic, validation |
| **Integration** | pytest + TestClient | Slow | HTTP routes | API contracts, auth, errors |
| **E2E** | Playwright | Slower | Full UI workflow | User journeys, UI interactions |

**Recommended Distribution:**
- 50% unit tests (CRUD)
- 30% integration tests (routes)
- 20% E2E tests (UI)

## Key Patterns

### Pattern 1: Test Success Path First

```python
# ✅ GOOD: Test happy path first, then errors
def test_create_item_success(db: Session) -> None:
    item = crud.create_item(session=db, ...)
    assert item.id

def test_create_item_validation_fails(db: Session) -> None:
    with pytest.raises(ValidationError):
        crud.create_item(session=db, item_in=invalid_data, ...)
```

### Pattern 2: Test Access Control

```python
# ✅ GOOD: Always verify access control
def test_user_cant_read_other_user_item(
    client: TestClient,
    normal_user_headers: dict,
    db: Session,
) -> None:
    # Create as different user
    item = create_random_item(db)

    # Try to read as normal user
    response = client.get(f"/api/v1/items/{item.id}", headers=normal_user_headers)
    assert response.status_code == 404  # Treated as not found
```

### Pattern 3: Verify State Changes

```python
# ✅ GOOD: Verify database state after operations
def test_delete_item(db: Session) -> None:
    item = create_random_item(db)
    crud.delete_item(session=db, db_item=item)

    # Verify deleted
    result = crud.read_item(session=db, item_id=item.id, owner_id=item.owner_id)
    assert result is None
```

### Pattern 4: Use Fixtures for Setup

```python
# ✅ GOOD: Use conftest.py fixtures
@pytest.fixture(scope="module")
def normal_user_token_headers(client: TestClient) -> dict[str, str]:
    return authentication_token_from_email(
        client=client,
        email=settings.EMAIL_TEST_USER,
    )

# Use in test
def test_something(client: TestClient, normal_user_token_headers: dict[str, str]) -> None:
    response = client.get("/api/v1/items/", headers=normal_user_token_headers)
```

### Pattern 5: Use `getByRole()` in E2E Tests

```typescript
// ✅ GOOD: Prefer getByRole (most accessible, reliable)
await page.getByRole("button", { name: "Create" }).click()
await page.getByLabel("Title").fill("Test")

// ❌ AVOID: Brittle selectors
await page.click("#create-btn")
await page.evaluate(() => document.querySelector("#title-input").value = "Test")
```

## Test Data Utilities

### Backend

```python
# tests/utils/user.py
def create_random_user(db: Session) -> User:
    email = f"test-{uuid4()}@example.com"
    user_in = UserCreate(email=email, password="password123")
    return crud.create_user(session=db, user_create=user_in)

# tests/utils/item.py
def create_random_item(db: Session, *, owner_id: UUID | None = None) -> Item:
    if not owner_id:
        owner = create_random_user(db)
        owner_id = owner.id
    item_in = ItemCreate(title=f"Item {uuid4()}", description="Test")
    return crud.create_item(session=db, item_in=item_in, owner_id=owner_id)
```

### Frontend

```typescript
// tests/utils/privateApi.ts
export const createTestUser = async (data: UserRegister) => {
  return await UsersService.registerUser({ requestBody: data })
}

export const deleteTestUser = async (userId: string) => {
  const response = await fetch(`/api/v1/users/${userId}`, {
    method: "DELETE",
  })
  return response.ok
}
```

## Commands Reference

### Backend Testing

```bash
cd backend

# Run all tests
./scripts/test.sh

# Run specific file
pytest tests/crud/test_item.py -v

# Run specific test
pytest tests/crud/test_item.py::test_create_item -v

# Run with coverage
pytest --cov=app --cov-report=html

# Run only fast tests
pytest tests/crud/ -v

# Run only route tests
pytest tests/api/routes/ -v

# Watch mode (requires pytest-watch)
ptw -- -v
```

### Frontend Testing

```bash
cd frontend

# Run all tests (headless)
npm run test

# Run with UI
npm run test:ui

# Run specific file
npx playwright test tests/items.spec.ts

# Run specific test
npx playwright test tests/items.spec.ts -g "create"

# Debug mode
npx playwright test --debug

# Generate report
npx playwright show-report
```

## Troubleshooting

| Issue | Solution |
|-------|----------|
| **Pytest can't find module** | Run `cd backend && uv sync` |
| **Test fixture not found** | Move to `conftest.py` in parent directory |
| **Database state leaked between tests** | Add cleanup in fixture teardown |
| **Playwright test times out** | Increase timeout in `playwright.config.ts` or add `await page.waitForTimeout()` |
| **Flaky E2E test** | Replace `time.sleep()` with `waitFor()`, use proper selectors |
| **Can't generate coverage** | Ensure import at module level, not inside functions |

## Next Steps

1. **Use templates** — Start with [backend-test-template.py](templates/backend-test-template.py) or [frontend-test-template.tsx](templates/frontend-test-template.tsx)
2. **Follow checklist** — Use [CHECKLIST.md](references/CHECKLIST.md) to ensure comprehensive coverage
3. **Refer to instructions** — Check [Backend Instructions](../../../instructions/backend.instructions.md) and [Frontend Instructions](../../../instructions/frontend.instructions.md) for detailed patterns
4. **Check examples** — Look at existing tests in `backend/tests/` and `frontend/tests/`
5. **Run tests regularly** — Make testing part of your development workflow

## Coverage Goals

- **New code**: 80%+ coverage
- **Critical paths** (auth, CRUD): 100% coverage
- Aim for 90%+ project-wide coverage

---

**See also:**
- [Scaffold API Endpoint](../scaffold-api-endpoint/SKILL.md) — Create new resources with tests
- [Backend Instructions](../../../instructions/backend.instructions.md) — Detailed patterns and examples
- [Frontend Instructions](../../../instructions/frontend.instructions.md) — React, TypeScript, hooks patterns
