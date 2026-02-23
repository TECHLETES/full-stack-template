# Scaffold API Endpoint Skill

This skill helps you generate a complete CRUD API endpoint from scratch, including:
- SQLModel database model with validation
- CRUD operations
- FastAPI routes with dependency injection
- Integration tests
- Database migrations
- Frontend TypeScript types (auto-generated)

## Contents

### Main Skill File
- **SKILL.md** — Start here! Contains the full 10-step procedure for scaffolding an endpoint

### Template References
Use these as starting points when creating your files:

- **templates/model-template.py** — SQLModel pattern with Base, Create, Update, Database, Public, and wrapper models
- **templates/crud-template.py** — CRUD operation patterns with pagination, filtering, and access control
- **templates/routes-template.py** — FastAPI route patterns with dependency injection and error handling
- **templates/tests-template.py** — Pytest patterns for testing routes and edge cases

### Checklists & References
- **references/CHECKLIST.md** — Step-by-step checklist for the entire scaffolding process

## Quick Start

1. **Read the main procedure**: Open `SKILL.md`
2. **Follow the 10-step workflow**:
   - Step 1: Gather requirements
   - Step 2: Define database model (reference `templates/model-template.py`)
   - Step 3: Create migration
   - Step 4: Add CRUD operations (reference `templates/crud-template.py`)
   - Step 5: Create API routes (reference `templates/routes-template.py`)
   - Step 6: Run linting
   - Step 7: Write tests (reference `templates/tests-template.py`)
   - Step 8: Verify in FastAPI docs
   - Step 9: Generate frontend client
   - Step 10: (Optional) Create frontend page

3. **Use the checklist**: `references/CHECKLIST.md` helps you track progress

## Example: Scaffolding a "Projects" Resource

Real example following this skill:

```bash
# Step 1: Requirements gathered
# - Resource: project
# - Fields: title, description, status (enum)
# - Owner: User (one user → many projects)

# Step 2-3: Model + migration (see templates/model-template.py)
# Add to backend/app/models.py:
class Project(ProjectBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    owner_id: uuid.UUID = Field(foreign_key="user.id", ondelete="CASCADE")
    owner: User | None = Relationship(back_populates="projects")

# Generator migration:
alembic revision --autogenerate -m "add project model"

# Step 4-5: CRUD + routes (see templates/crud-template.py, routes-template.py)
# Add crud.create_project(), crud.read_projects(), etc. to backend/app/crud.py
# Create backend/app/api/routes/projects.py with GET/POST/PATCH/DELETE endpoints
# Register in backend/app/api/main.py

# Step 6-7: Lint + test
./scripts/lint.sh          # Format code
./scripts/test.sh          # Run tests

# Step 9: Generate client
cd frontend && npm run generate-client
# Now types available: ProjectPublic, ProjectsService, etc.
```

## File Structure

```
.github/skills/scaffold-api-endpoint/
├── SKILL.md                          # Main procedure
├── templates/
│   ├── model-template.py             # SQLModel pattern
│   ├── crud-template.py              # CRUD patterns
│   ├── routes-template.py            # Route patterns
│   └── tests-template.py             # Test patterns
└── references/
    └── CHECKLIST.md                  # Progress tracking
```

## Key Concepts from Backend Instructions

This skill implements the patterns defined in [Backend Instructions](../../../instructions/backend.instructions.md):

- **SQLModel Modeling** — Base → Create/Update → Public → Database pattern
- **CRUD Patterns** — `model_validate()`, `exclude_unset=True`, pagination
- **API Routes** — Dependency injection, error handling, access control
- **Testing** — Fixtures, parametrized tests, coverage tracking
- **Migrations** — Auto-generate, test apply/rollback

## When to Use

✅ **Good use cases:**
- Adding a new resource to the API (projects, categories, posts, etc.)
- Need complete CRUD operations
- Want to follow project patterns
- Need tests from day one

❌ **Not needed for:**
- Simple one-off endpoints
- Modifying existing resources
- Complex custom queries (use CRUD templates as reference instead)

## Common Workflow

1. **Planning** (5 min) — Define resource, properties, relationships
2. **Model + Migration** (10 min) — Use model template, generate migration
3. **CRUD Operations** (15 min) — Copy from crud template, customize
4. **Routes** (15 min) — Copy from routes template, customize
5. **Tests** (20 min) — Copy from tests template, add more cases
6. **Verification** (10 min) — Check linting, run tests, test in docs
7. **Frontend** (30 min, optional) — Generate client, create page

**Total: ~1.5 hours for end-to-end with frontend**

## Troubleshooting

See `SKILL.md` section **Troubleshooting** or `references/CHECKLIST.md` for common issues and fixes.

## References

- **Backend Instructions**: [../../../instructions/backend.instructions.md](../../../instructions/backend.instructions.md)
- **FastAPI Documentation**: https://fastapi.tiangolo.com
- **SQLModel Documentation**: https://sqlmodel.tiangolo.com
- **Alembic Documentation**: https://alembic.sqlalchemy.org
- **Pytest Documentation**: https://docs.pytest.org
