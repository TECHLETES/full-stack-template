# API Endpoint Scaffolding Checklist

Use this checklist when scaffolding a new CRUD endpoint. Check items off as you complete them.

## Phase 1: Planning
- [ ] Decide resource name (lowercase, singular): `project`
- [ ] List primary properties: `title`, `description`, `status`
- [ ] Plan relationships: Owner (User → Project)
- [ ] Identify unique constraints: Title (per user, not global)
- [ ] Validation rules: Min/max lengths, required fields, enums

## Phase 2: Database Model
- [ ] Create Base model (shared properties)
- [ ] Create XCreate model (for POST requests)
- [ ] Create XUpdate model (for PATCH requests, all fields optional)
- [ ] Create X database model (table=True, with ID, timestamps, FK, relationships)
- [ ] Create XPublic model (for responses, no secrets)
- [ ] Create XsPublic wrapper (for paginated lists: data + count)
- [ ] Add model import to `backend/app/models.py`
- [ ] Add relationship to parent model (e.g., User.projects)

## Phase 3: Database Migration
- [ ] Run: `cd backend && alembic revision --autogenerate -m "add project model"`
- [ ] Review generated migration file
- [ ] Test apply: `alembic upgrade head`
- [ ] Test rollback: `alembic downgrade -1`
- [ ] Test re-apply: `alembic upgrade head`

## Phase 4: CRUD Operations
- [ ] Create `create_project()` in `crud.py`
- [ ] Create `read_projects()` (paginated, filtered by owner_id)
- [ ] Create `read_project()` (single item, access control)
- [ ] Create `update_project()` (partial updates with exclude_unset)
- [ ] Create `delete_project()` (simple delete)
- [ ] Test each CRUD function locally if possible

## Phase 5: API Routes
- [ ] Create `backend/app/api/routes/projects.py`
- [ ] Add `GET /projects/` (list with pagination)
- [ ] Add `POST /projects/` (create)
- [ ] Add `GET /projects/{id}` (read single)
- [ ] Add `PATCH /projects/{id}` (update)
- [ ] Add `DELETE /projects/{id}` (delete)
- [ ] Add docstrings to each route
- [ ] Register router in `backend/app/api/main.py`

## Phase 6: Linting & Type Checking
- [ ] Run: `cd backend && ./scripts/lint.sh`
- [ ] Fix any ruff errors
- [ ] Fix any mypy errors
- [ ] No import errors or unused variables

## Phase 7: Testing
- [ ] Create test utility in `backend/tests/utils/project.py`
- [ ] Create `backend/tests/api/routes/test_projects.py`
- [ ] Test create endpoint
- [ ] Test create validation (required fields, constraints)
- [ ] Test list endpoint (pagination, ordering)
- [ ] Test read single endpoint (success, not found)
- [ ] Test access control (user can't read other's project)
- [ ] Test update endpoint (full and partial)
- [ ] Test delete endpoint (success, not found)
- [ ] Run: `cd backend && ./scripts/test.sh`
- [ ] All tests pass
- [ ] Coverage acceptable (>80%)

## Phase 8: API Verification
- [ ] Start backend: `cd backend && uv run fastapi dev app/main.py`
- [ ] Open `http://localhost:8000/docs`
- [ ] Verify `/projects` endpoint appears
- [ ] Test each endpoint in interactive docs
- [ ] Verify request/response schemas
- [ ] Test with valid and invalid data

## Phase 9: Frontend Client
- [ ] Run: `cd frontend && npm run generate-client`
- [ ] Verify `ProjectsService` exists in generated client
- [ ] Verify types: `ProjectPublic`, `ProjectCreate`, `ProjectUpdate`, `ProjectsPublic`
- [ ] Check `src/client/schemas.gen.ts` for correct types

## Phase 10: Frontend Integration (Optional)
- [ ] Create route file: `frontend/src/routes/_layout/projects.tsx`
- [ ] Create component folder: `frontend/src/components/Projects/`
- [ ] Add page component with:
  - [ ] useQuery for list page
  - [ ] useMutation for create/update/delete
  - [ ] useCustomToast for notifications
  - [ ] Form with react-hook-form + Zod
  - [ ] shadcn/ui components
- [ ] Create test in `frontend/tests/projects.spec.ts`
- [ ] Run: `cd frontend && npm run test`
- [ ] Frontend tests pass

## Final Checks
- [ ] Backend tests passing
- [ ] Frontend tests passing (if created)
- [ ] No console errors or warnings
- [ ] No TypeScript errors
- [ ] Linting passes
- [ ] Code follows project patterns from instructions
- [ ] Access control working (users can't access others' data)
- [ ] Pagination working
- [ ] Validation working
- [ ] Cascade deletes working (delete user → deletes their projects)

## Common Issues & Fixes

| Issue | Fix |
|-------|-----|
| Migration not generated | Verify `table=True` on DB model in models.py |
| Import errors | Run `cd backend && uv sync` |
| Route not appearing in docs | Verify router registered in `app/api/main.py` |
| Tests fail with 404 | Check route registered, check auth headers |
| Type errors in CRUD | Use `model_validate()`, not direct instantiation |
| Frontend types not updated | Run `npm run generate-client` |
| Cascade delete not working | Verify `cascade_delete=True` on Relationship and `ondelete="CASCADE"` on FK |
| User can access other's data | Check `read_project()` filters by both ID and owner_id |

## Testing Commands

```bash
# Run all backend tests
cd backend && ./scripts/test.sh

# Run specific test file
pytest tests/api/routes/test_projects.py -v

# Run specific test
pytest tests/api/routes/test_projects.py::test_create_project -v

# Run with coverage
pytest tests/api/routes/test_projects.py --cov=app --cov-report=html

# Lint and format
cd backend && ./scripts/lint.sh

# Type check only
mypy app/

# Frontend tests
cd frontend && npm run test

# Frontend E2E tests with UI
npm run test:ui
```

## File Locations Reference

| File | Path |
|------|------|
| Database model | `backend/app/models.py` |
| CRUD operations | `backend/app/crud.py` |
| API routes | `backend/app/api/routes/projects.py` |
| Route registration | `backend/app/api/main.py` |
| Migration | `backend/alembic/versions/xxxx_add_project_model.py` |
| Tests | `backend/tests/api/routes/test_projects.py` |
| Test utilities | `backend/tests/utils/project.py` |
| Frontend page | `frontend/src/routes/_layout/projects.tsx` (optional) |
| Frontend components | `frontend/src/components/Projects/` (optional) |
| Generated types | `frontend/src/client/schemas.gen.ts` (auto-generated) |

## Template Files

| Template | Path |
|----------|------|
| Model example | `.github/skills/scaffold-api-endpoint/templates/model-template.py` |
| CRUD example | `.github/skills/scaffold-api-endpoint/templates/crud-template.py` |
| Routes example | `.github/skills/scaffold-api-endpoint/templates/routes-template.py` |
| Tests example | `.github/skills/scaffold-api-endpoint/templates/tests-template.py` |
