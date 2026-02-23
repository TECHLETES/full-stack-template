---
name: add-test-coverage
description: 'Add comprehensive test coverage with pytest (backend unit + integration tests) and Playwright (frontend E2E tests). Use when adding new features, fixing bugs, or improving coverage.'
argument-hint: 'Feature/component to test (e.g., projects list page, user authentication)'
user-invocable: true
---

# Add Test Coverage

Implement comprehensive test coverage for your features using pytest (backend) and Playwright (frontend E2E).

## When to Use

- **New feature**: Write tests before or alongside implementation (TDD)
- **Bug fix**: Add regression tests to prevent future issues
- **Coverage gaps**: Identify and fill untested code paths
- **Refactoring**: Ensure behavior doesn't change with confidence
- **Pull requests**: Require tests for all new code

## What You'll Learn

- ✅ Unit test patterns (CRUD operations, business logic)
- ✅ Integration test patterns (full route testing with auth)
- ✅ E2E test patterns (user workflows through UI)
- ✅ Test organization and structure
- ✅ Mocking and fixtures
- ✅ Coverage measurement and reporting
- ✅ Common pitfalls and solutions

---

## Testing Strategy Overview

### Backend (pytest)

**Two levels of testing:**

1. **Unit Tests** — Test CRUD functions in isolation
   - Fast, no database needed (can mock)
   - Test business logic directly
   - Located: `tests/crud/`

2. **Integration Tests** — Test full HTTP routes with auth
   - Slower, use real database
   - Test API contracts
   - Test error handling
   - Located: `tests/api/routes/`

### Frontend (Playwright)

**E2E Tests** — Test user workflows through the UI
- Slow, use real browser
- Test complete user journeys
- Verify UI interactions
- Located: `frontend/tests/`

**Pattern:** Setup auth once → reuse for all tests ([auth.setup.ts](../../tests/auth.setup.ts))

---

## Backend Testing (pytest)

### Test Structure

```
backend/tests/
├── conftest.py                    # Shared fixtures (client, db, auth)
├── api/
│   ├── routes/
│   │   ├── test_users.py         # Route tests (HTTP level)
│   │   ├── test_items.py
│   │   └── test_projects.py
│   └── test_deps.py              # Dependency injection tests
├── crud/
│   ├── test_user.py              # CRUD tests (business logic)
│   ├── test_item.py
│   └── test_project.py
└── utils/
    ├── user.py                    # User creation utilities
    ├── item.py                    # Item creation utilities
    └── project.py                # Project creation utilities
```

### Level 1: Unit Tests (CRUD)

Test database operations directly:

```python
# backend/tests/crud/test_project.py
import uuid
import pytest
from sqlmodel import Session
from app.models import ProjectCreate
from app import crud


def test_create_project(db: Session) -> None:
    """Test creating a project via CRUD."""
    from tests.utils.project import create_random_user
    
    user = create_random_user(db)
    project_in = ProjectCreate(title="Test", description="Desc")
    
    project = crud.create_project(
        session=db,
        project_in=project_in,
        owner_id=user.id,
    )
    
    assert project.id
    assert project.title == "Test"
    assert project.owner_id == user.id


def test_read_project_returns_none_if_not_found(db: Session) -> None:
    """Test reading non-existent project."""
    from tests.utils.project import create_random_user
    
    user = create_random_user(db)
    project = crud.read_project(
        session=db,
        owner_id=user.id,
        project_id=uuid.uuid4(),
    )
    
    assert project is None


def test_update_project(db: Session) -> None:
    """Test updating a project."""
    from tests.utils.project import create_random_project
    
    project = create_random_project(db)
    updated = ProjectUpdate(title="Updated")
    
    result = crud.update_project(
        session=db,
        db_project=project,
        project_in=updated,
    )
    
    assert result.title == "Updated"


def test_delete_project(db: Session) -> None:
    """Test deleting a project."""
    from tests.utils.project import create_random_project
    
    project = create_random_project(db)
    crud.delete_project(session=db, db_project=project)
    
    # Verify deleted
    result = crud.read_project(
        session=db,
        owner_id=project.owner_id,
        project_id=project.id,
    )
    assert result is None
```

**Key Patterns:**
- Use `create_random_*` utilities to set up test data
- Test one scenario per function
- Descriptive names: `test_<action>_<scenario>`
- Assert specific values, not just truthiness

### Level 2: Integration Tests (API Routes)

Test full HTTP endpoints:

```python
# backend/tests/api/routes/test_projects.py
import uuid
import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session
from app.models import ProjectCreate


def test_create_project_succeeds(
    client: TestClient,
    normal_user_token_headers: dict[str, str],
) -> None:
    """Test creating a project via POST endpoint."""
    data = {"title": "My Project", "description": "Desc"}
    response = client.post(
        "/api/v1/projects/",
        headers=normal_user_token_headers,
        json=data,
    )
    
    assert response.status_code == 200
    content = response.json()
    assert content["title"] == data["title"]
    assert content["owner_id"]


def test_create_project_validation_fails(
    client: TestClient,
    normal_user_token_headers: dict[str, str],
) -> None:
    """Test creation fails with invalid data."""
    data = {"description": "Missing title"}  # title is required
    response = client.post(
        "/api/v1/projects/",
        headers=normal_user_token_headers,
        json=data,
    )
    
    assert response.status_code == 422  # Validation error


def test_read_projects_requires_auth(client: TestClient) -> None:
    """Test that unauthenticated requests are rejected."""
    response = client.get("/api/v1/projects/")
    assert response.status_code == 403


def test_read_project_forbidden_for_other_user(
    client: TestClient,
    normal_user_token_headers: dict[str, str],
    superuser_token_headers: dict[str, str],
    db: Session,
) -> None:
    """Test user can't read another user's project."""
    from tests.utils.project import create_random_project
    
    # Create as superuser (different user)
    project = create_random_project(db)
    
    # Normal user tries to read
    response = client.get(
        f"/api/v1/projects/{project.id}",
        headers=normal_user_token_headers,
    )
    
    assert response.status_code == 404  # Treated as not found


def test_update_project_partial(
    client: TestClient,
    normal_user_token_headers: dict[str, str],
    db: Session,
) -> None:
    """Test partial update (only title, description stays same)."""
    from tests.utils.project import create_random_project
    
    project = create_random_project(db)
    original_desc = project.description
    
    response = client.patch(
        f"/api/v1/projects/{project.id}",
        headers=normal_user_token_headers,
        json={"title": "New Title"},
    )
    
    assert response.status_code == 200
    content = response.json()
    assert content["title"] == "New Title"
    assert content["description"] == original_desc


def test_delete_project_succeeds(
    client: TestClient,
    normal_user_token_headers: dict[str, str],
    db: Session,
) -> None:
    """Test deleting a project."""
    from tests.utils.project import create_random_project
    
    project = create_random_project(db)
    
    response = client.delete(
        f"/api/v1/projects/{project.id}",
        headers=normal_user_token_headers,
    )
    
    assert response.status_code == 200
    
    # Verify deleted
    response = client.get(
        f"/api/v1/projects/{project.id}",
        headers=normal_user_token_headers,
    )
    assert response.status_code == 404
```

**Key Patterns:**
- Use `TestClient` for HTTP requests
- Use `*_token_headers` fixtures for authentication
- Test both success and error scenarios
- Test validation failures (422)
- Test authorization (403/404)
- Test state changes (verify with GET after DELETE)

### Test Fixtures

Common fixtures in `backend/tests/conftest.py`:

```python
import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, delete

from app.core.config import settings
from app.core.db import engine, init_db
from app.main import app
from app.models import User, Item

@pytest.fixture(scope="session", autouse=True)
def db() -> Generator[Session, None, None]:
    """Database session (shared for all tests)."""
    with Session(engine) as session:
        init_db(session)
        yield session
        # Cleanup
        for table in [Item, User]:
            session.execute(delete(table))
        session.commit()

@pytest.fixture(scope="module")
def client() -> Generator[TestClient, None, None]:
    """FastAPI test client."""
    with TestClient(app) as c:
        yield c

@pytest.fixture(scope="module")
def superuser_token_headers(client: TestClient) -> dict[str, str]:
    """Auth headers for superuser."""
    return get_superuser_token_headers(client)

@pytest.fixture(scope="module")
def normal_user_token_headers(client: TestClient, db: Session) -> dict[str, str]:
    """Auth headers for normal user."""
    return authentication_token_from_email(
        client=client,
        email=settings.EMAIL_TEST_USER,
        db=db,
    )
```

### Running Backend Tests

```bash
cd backend

# Run all tests
./scripts/test.sh

# Run specific file
pytest tests/api/routes/test_projects.py -v

# Run specific test
pytest tests/api/routes/test_projects.py::test_create_project_succeeds -v

# Run with coverage
pytest --cov=app --cov-report=html
# Open htmlcov/index.html

# Run only CRUD tests (fast)
pytest tests/crud/ -v

# Run only route tests (slower, uses DB)
pytest tests/api/routes/ -v

# Run with markers
pytest -m "not slow" -v  # Skip slow tests
```

---

## Frontend Testing (Playwright)

### Test Structure

```
frontend/tests/
├── auth.setup.ts          # Shared auth setup (runs once)
├── config.ts              # Test configuration
├── login.spec.ts          # Login/auth tests
├── admin.spec.ts          # Admin panel tests
├── items.spec.ts          # Items page tests
├── user-settings.spec.ts  # Settings page tests
└── utils/
    ├── mailcatcher.ts     # Email testing
    ├── privateApi.ts      # API helper functions
    └── random.ts          # Random data generators
```

### Auth Setup (Run Once)

```typescript
// frontend/tests/auth.setup.ts
import { test as setup } from "@playwright/test"
import { firstSuperuser, firstSuperuserPassword } from "./config.ts"

const authFile = "playwright/.auth/user.json"

setup("authenticate", async ({ page }) => {
  await page.goto("/login")
  await page.getByTestId("email-input").fill(firstSuperuser)
  await page.getByTestId("password-input").fill(firstSuperuserPassword)
  await page.getByRole("button", { name: "Log In" }).click()
  await page.waitForURL("/")
  await page.context().storageState({ path: authFile })
})
```

**Key:**
- Runs once per test session
- Saves auth state to file
- Other tests reuse this state

### Page E2E Tests

```typescript
// frontend/tests/items.spec.ts
import { expect, test } from "@playwright/test"

test("User can create an item", async ({ page }) => {
  await page.goto("/items")
  
  // Click create button
  await page.getByRole("button", { name: "Add Item" }).click()
  
  // Fill form
  await page.getByLabel("Title").fill("Test Item")
  await page.getByLabel("Description").fill("A test item")
  
  // Submit
  await page.getByRole("button", { name: "Create" }).click()
  
  // Verify success
  await expect(
    page.getByText("Item created successfully")
  ).toBeVisible()
  
  // Verify item in list
  await expect(page.getByText("Test Item")).toBeVisible()
})

test("User can edit an item", async ({ page }) => {
  await page.goto("/items")
  
  // Find item row
  const row = page.locator("table tbody tr").first()
  
  // Click edit
  await row.getByRole("button", { name: "Edit" }).click()
  
  // Update title
  await page.getByLabel("Title").fill("Updated Title")
  
  // Submit
  await page.getByRole("button", { name: "Save" }).click()
  
  // Verify
  await expect(page.getByText("Item updated successfully")).toBeVisible()
  await expect(page.getByText("Updated Title")).toBeVisible()
})

test("User can delete an item", async ({ page }) => {
  await page.goto("/items")
  
  // Count initial items
  const initialCount = await page.locator("table tbody tr").count()
  
  // Delete first item
  const row = page.locator("table tbody tr").first()
  await row.getByRole("button", { name: "Delete" }).click()
  
  // Accept confirmation
  await page.getByRole("button", { name: "Confirm" }).click()
  
  // Verify success message
  await expect(page.getByText("Item deleted successfully")).toBeVisible()
  
  // Verify count decreased
  const newCount = await page.locator("table tbody tr").count()
  expect(newCount).toBe(initialCount - 1)
})

test("Search filters items", async ({ page }) => {
  await page.goto("/items")
  
  // Type in search
  await page.getByPlaceholder("Search items...").fill("test")
  
  // Wait for results
  await page.waitForTimeout(500)
  
  // Verify only matching items shown
  const rows = page.locator("table tbody tr")
  const count = await rows.count()
  expect(count).toBeGreaterThanOrEqual(0)
  
  // Each visible row should contain "test"
  for (let i = 0; i < count; i++) {
    const row = rows.nth(i)
    const text = await row.textContent()
    expect(text?.toLowerCase()).toContain("test")
  }
})
```

**Key Patterns:**
- `getByRole()` — Query accessible elements (most reliable)
- `getByLabel()` — Query form fields
- `getByText()` — Query text content
- `getByTestId()` — Query by test data attribute (use when role/label not available)
- `expect().toBeVisible()` — Assert element visibility
- `waitForURL()` — Wait for navigation
- `waitForTimeout()` — Wait for async updates

### API Helper Tests

```typescript
// frontend/tests/utils/privateApi.ts
import { UsersService } from "@/client"

export const createTestUser = async (data: UserRegister) => {
  return await UsersService.registerUser({ requestBody: data })
}

export const deleteTestUser = async (userId: string) => {
  // Use API to clean up
  const response = await fetch(`/api/v1/users/${userId}`, {
    method: "DELETE",
  })
  return response.ok
}

// Usage in test:
test("Admin can delete user", async ({ page }) => {
  const newUser = await createTestUser({
    email: "test@example.com",
    password: "password123",
    full_name: "Test User",
  })
  
  await page.goto("/admin")
  await page.getByText(newUser.email).click()
  await page.getByRole("button", { name: "Delete" }).click()
  
  // Cleanup
  await deleteTestUser(newUser.id)
})
```

### Running Frontend Tests

```bash
cd frontend

# Run Playwright tests interactively
npm run test:ui

# Run all tests headless
npm run test

# Run specific test file
npx playwright test tests/items.spec.ts

# Run specific test
npx playwright test tests/items.spec.ts -g "create an item"

# Debug mode
npx playwright test --debug

# Generate report after run
npx playwright show-report
```

---

## Test Coverage Measurement

### Backend Coverage

```bash
cd backend

# Generate coverage report
pytest --cov=app --cov-report=html --cov-report=term

# View report
open htmlcov/index.html
```

**Target coverage:**
- **80%+** — Good
- **90%+** — Excellent
- **Critical paths** (auth, CRUD) — 100%

### Coverage by Module

```bash
# Coverage by file
pytest --cov=app --cov-report=term -- tests/

# Only show missing lines
pytest --cov=app --cov-report=term-missing tests/
```

### Ignore Coverage

Mark code that shouldn't be covered:

```python
if some_rare_error:  # pragma: no cover
    log_and_crash()
```

---

## Testing Checklist

### For New Features

- [ ] Unit tests for business logic (CRUD functions)
- [ ] Integration tests for API routes
- [ ] Edge case tests (validation errors, not found, permissions)
- [ ] E2E tests for user workflows (frontend)
- [ ] Error handling tests (400/403/404 responses)
- [ ] Coverage >80% for new code
- [ ] No console errors in browser tests

### For Bug Fixes

- [ ] Add regression test (would have caught bug)
- [ ] Verify fix with existing tests
- [ ] Add edge case tests if applicable

### For Refactoring

- [ ] All existing tests pass
- [ ] Coverage doesn't decrease
- [ ] No behavioral changes

---

## Common Testing Patterns

### Parametrized Tests

Test multiple scenarios efficiently:

```python
import pytest

@pytest.mark.parametrize("title,valid", [
    ("Valid Title", True),
    ("", False),  # Empty
    ("x" * 300, False),  # Too long
])
def test_project_title_validation(title: str, valid: bool, db: Session) -> None:
    project_in = ProjectCreate(title=title)
    
    if not valid:
        with pytest.raises(ValidationError):
            project_in.model_validate(project_in.model_dump())
    else:
        # Should work
        assert project_in.title == title
```

### Mocking External Services

```python
from unittest.mock import patch

@patch("app.utils.send_email")
def test_user_creation_sends_email(mock_send: Mock, db: Session) -> None:
    user_in = UserCreate(email="new@example.com", password="pass")
    crud.create_user(session=db, user_create=user_in)
    
    # Verify email was called
    mock_send.assert_called_once()
    call_args = mock_send.call_args
    assert "new@example.com" in call_args[1]["email_to"]
```

### Testing Error Scenarios

```python
def test_create_duplicate_email_fails(db: Session) -> None:
    from tests.utils.user import create_random_user
    
    # Create first user
    user1 = create_random_user(db)
    
    # Try to create with same email
    user_in = UserCreate(email=user1.email, password="password")
    
    with pytest.raises(IntegrityError):
        crud.create_user(session=db, user_create=user_in)
```

---

## Troubleshooting

| Issue | Cause | Solution |
|-------|-------|----------|
| **Tests pass locally, fail in CI** | Different env variables | Check .env, add defaults |
| **Flaky Playwright tests** | Race conditions, timing | Add `waitFor`, increase timeout |
| **Database not cleaning up** | Cleanup code not running | Add `skipdb` fixture cleanup |
| **Import errors** | Package not installed | Run `cd backend && uv sync` or `cd frontend && npm install` |
| **Tests can't find fixtures** | Fixture not in conftest.py | Move to root `conftest.py` |
| **Coverage not including file** | File not imported by tests | Import in test or conftest |
| **Auth token expired** | Long test runs | Use longer expiry in test env |
| **Playwright can't find element** | Selector too specific | Use `getByRole` or `getByLabel` instead |

---

## Test Writing Tips

✅ **Good practices:**
- One scenario per test (single responsibility)
- Descriptive name: `test_<action>_<scenario>_<result>`
- Arrange → Act → Assert pattern
- Test behavior, not implementation
- Use fixtures for setup
- Test error paths
- Verify side effects (DB state, emails sent)

❌ **Avoid:**
- Testing third-party libraries
- Brittle selectors (XPath, precise element counts)
- Sleeping instead of waiting (`time.sleep()`)
- Testing too many scenarios per test
- Hardcoded IDs/values instead of fixtures
- Skipping tests (`@pytest.mark.skip`)

---

## References

- **Backend Instructions**: [../../../instructions/backend.instructions.md#testing-patterns](../../../instructions/backend.instructions.md#testing-patterns)
- **Frontend Instructions**: [../../../instructions/frontend.instructions.md#testing-with-playwright](../../../instructions/frontend.instructions.md#testing-with-playwright)
- **Pytest Docs**: https://docs.pytest.org/
- **Playwright Docs**: https://playwright.dev/python/
- **FastAPI Testing**: https://fastapi.tiangolo.com/advanced/testing-dependencies/
- **SQLModel Testing**: https://sqlmodel.tiangolo.com/tutorial/testing/

## Quick Commands

```bash
# Backend: Run all tests
cd backend && ./scripts/test.sh

# Backend: Run with coverage
pytest --cov=app --cov-report=html

# Backend: Run specific test
pytest tests/api/routes/test_projects.py::test_create_project -v

# Frontend: Run E2E tests with UI
cd frontend && npm run test:ui

# Frontend: Run headless
npm run test

# Frontend: Run specific test
npx playwright test tests/items.spec.ts -g "create"

# Frontend: Debug mode
npx playwright test --debug
```
