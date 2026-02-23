# Test Coverage Checklist

Use this checklist when adding tests to ensure comprehensive coverage.

## Planning Phase

- [ ] Identify what to test (new feature, bug fix, refactoring)
- [ ] Determine test levels needed:
  - [ ] Unit tests (CRUD functions, business logic)
  - [ ] Integration tests (full HTTP routes)
  - [ ] E2E tests (user workflows)
- [ ] List test scenarios:
  - [ ] Happy path (success case)
  - [ ] Validation failures
  - [ ] Not found scenarios
  - [ ] Permission/auth failures
  - [ ] Edge cases

## Backend Unit Tests

- [ ] Create test file: `backend/tests/crud/test_<feature>.py`
- [ ] Import required modules and fixtures
- [ ] **CRUD Operations:**
  - [ ] Test create with valid data
  - [ ] Test create with invalid data (validation)
  - [ ] Test read by ID
  - [ ] Test read returns None for non-existent
  - [ ] Test list with pagination
  - [ ] Test update full
  - [ ] Test update partial (exclude_unset)
  - [ ] Test delete
- [ ] **Access Control:**
  - [ ] Test query filters by owner_id
  - [ ] Test update checks owner
  - [ ] Test delete checks owner
- [ ] **Edge Cases:**
  - [ ] Test with empty strings
  - [ ] Test with very long strings
  - [ ] Test with None/null values
  - [ ] Test with duplicate values (if applicable)

## Backend Integration Tests

- [ ] Create test file: `backend/tests/api/routes/test_<feature>.py`
- [ ] **Success Cases:**
  - [ ] Test POST (create) returns 200, correct data
  - [ ] Test GET (list) returns 200, with pagination
  - [ ] Test GET (single) returns 200, correct data
  - [ ] Test PATCH (update) returns 200, updated data
  - [ ] Test DELETE returns 200
- [ ] **Validation:**
  - [ ] Test missing required fields → 422
  - [ ] Test invalid data types → 422
  - [ ] Test string length validation → 422
  - [ ] Test email format validation → 422 (if applicable)
- [ ] **Authentication:**
  - [ ] Test unauthenticated access → 403
  - [ ] Test with invalid token → 403
- [ ] **Authorization:**
  - [ ] Test user can't access other user's resource → 404
  - [ ] Test user can only update own resource
  - [ ] Test superuser can access others' resources (if applicable)
- [ ] **Not Found:**
  - [ ] Test GET with non-existent ID → 404
  - [ ] Test PATCH with non-existent ID → 404
  - [ ] Test DELETE with non-existent ID → 404
- [ ] **State Changes:**
  - [ ] Verify DB state after create
  - [ ] Verify DB state after update
  - [ ] Verify DB state after delete

## Frontend E2E Tests

- [ ] Create test file: `frontend/tests/<feature>.spec.ts`
- [ ] **Page Loading:**
  - [ ] Test page loads and displays content
  - [ ] Test header/title visible
  - [ ] Test main action buttons visible (Create, Edit, Delete)
- [ ] **Create Workflow:**
  - [ ] Test open create dialog/form
  - [ ] Test fill all form fields
  - [ ] Test submit form
  - [ ] Test success message shown
  - [ ] Test item appears in list
- [ ] **Read/View:**
  - [ ] Test click on item shows details
  - [ ] Test details page displays correct data
  - [ ] Test all required fields visible
- [ ] **Update Workflow:**
  - [ ] Test click edit button
  - [ ] Test form populated with current values
  - [ ] Test modify one field
  - [ ] Test submit
  - [ ] Test success message
  - [ ] Test updated value visible
- [ ] **Delete Workflow:**
  - [ ] Test click delete button
  - [ ] Test confirmation dialog appears
  - [ ] Test confirm deletion
  - [ ] Test success message
  - [ ] Test item removed from list
- [ ] **Search/Filter:**
  - [ ] Test type in search box
  - [ ] Test results filtered
  - [ ] Test clear search shows all
- [ ] **Pagination:**
  - [ ] Test pagination controls visible (if applicable)
  - [ ] Test click next/previous
  - [ ] Test page changes
- [ ] **Validation:**
  - [ ] Test form validation errors show
  - [ ] Test submit disabled until valid
  - [ ] Test error message for each field
- [ ] **Error Handling:**
  - [ ] Test error message on API failure
  - [ ] Test network error handled
  - [ ] Test retry option available (if applicable)
- [ ] **Navigation:**
  - [ ] Test breadcrumbs work
  - [ ] Test sidebar navigation works
  - [ ] Test back button works

## Coverage Metrics

- [ ] Backend: Run coverage report
  ```bash
  pytest --cov=app --cov-report=html
  ```
- [ ] Verify coverage >80% for new code
- [ ] Verify all critical paths (auth, CRUD) >95%
- [ ] Open `htmlcov/index.html` to review coverage by file
- [ ] Check for untested exception handlers
- [ ] Check for untested validation branches

## Code Quality

- [ ] All tests pass locally: `cd backend && ./scripts/test.sh`
- [ ] All tests pass locally: `cd frontend && npm run test`
- [ ] No Python syntax errors: `cd backend && ruff check tests/`
- [ ] No TypeScript errors: `cd frontend && npm run lint`
- [ ] No console errors in Playwright tests
- [ ] Descriptive test names (what is being tested, expected result)

## Test Organization

- [ ] Tests grouped by feature/resource
- [ ] Test files named consistently: `test_<feature>.py`, `<feature>.spec.ts`
- [ ] Test functions named clearly: `test_<action>_<scenario>_<result>`
- [ ] Common fixtures in `conftest.py`
- [ ] Utility functions in `tests/utils/`

## Before Submitting

- [ ] Run all tests one final time
- [ ] Verify no tests are skipped (no `@pytest.mark.skip`)
- [ ] Check coverage hasn't decreased
- [ ] Add test documentation in PR description
- [ ] List tests added in commit message

## Common Test Counts

**Small Feature (e.g., new field):**
- 2-3 unit tests (CRUD operations)
- 3-5 route tests (success, validation, auth)
- 2-3 E2E tests (view, create, verify)
- **Total: 7-11 tests**

**Medium Feature (e.g., new resource):**
- 10-12 unit tests (all CRUD, multiple scenarios)
- 15-20 route tests (all endpoints, errors, permissions)
- 8-12 E2E tests (create, read, update, delete, search)
- **Total: 33-44 tests**

**Large Feature (e.g., full module):**
- 30+ unit tests (complex logic, edge cases)
- 40+ route tests (all endpoint variations)
- 20+ E2E tests (all user workflows)
- **Total: 90+ tests**

## References

- [Backend Instructions - Testing](../../../instructions/backend.instructions.md#testing-patterns)
- [Frontend Instructions - Testing](../../../instructions/frontend.instructions.md#testing-with-playwright)
- [Backend Test Template](../templates/backend-test-template.py)
- [Frontend Test Template](../templates/frontend-test-template.tsx)
