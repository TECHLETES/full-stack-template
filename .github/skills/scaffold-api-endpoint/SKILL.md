---
name: scaffold-api-endpoint
description: 'Scaffold a complete FastAPI CRUD endpoint with SQLModel, routes, CRUD operations, and tests. Use when adding a new API resource (users, items, projects, etc.).'
argument-hint: 'Resource name (e.g., projects, comments, tags)'
user-invocable: true
---

# Scaffold API Endpoint

Generate a full-stack CRUD endpoint for a new resource: database model, CRUD operations, API routes, and tests.

## When to Use

- **Adding a new resource** to the API (users, items, projects, posts, tags, etc.)
- **Need complete CRUD**: Create, Read (list + single), Update, Delete operations
- **Starting from scratch**: Model → CRUD → Routes → Tests
- **Following project patterns**: Ensure consistency with existing resources

## What You'll Get

- ✅ SQLModel database model with relationships and validation
- ✅ CRUD operations in `crud.py` (create, read, update, delete patterns)
- ✅ API routes in `api/routes/` with dependency injection
- ✅ Input/output models (Create, Update, Public, list wrapper)
- ✅ Integration tests in `tests/api/routes/`
- ✅ Database migration (Alembic)
- ✅ Frontend client types (auto-generated)

## Procedure

### 1. Gather Requirements

Before starting, clarify:
- **Resource name** (singular, lowercase): `project`, `comment`, `tag`
- **Primary properties**: What fields does it need?
- **Owner/parent relationship**: Does it belong to a user? Another resource?
- **Unique constraints**: Email-like uniqueness? Index requirements?
- **Validation rules**: Min/max lengths, patterns, custom validators?

**Example for "Project":**
- Fields: `title`, `description`, `status` (enum: active/archived), `owner_id`
- Owner: User (one user → many projects, cascade delete)
- Unique: title per user (not globally unique)
- Validation: title 1-255 chars, status in enum

### 2. Define the Database Model

Use the SQLModel template: [model-template.py](./templates/model-template.py)

**In `backend/models.py`, add:**

```python
import uuid
from datetime import datetime, timezone
from enum import Enum
from sqlmodel import Field, Relationship, SQLModel

# Enum for status
class ProjectStatus(str, Enum):
    ACTIVE = "active"
    ARCHIVED = "archived"

# 1. Base properties (shared)
class ProjectBase(SQLModel):
    title: str = Field(min_length=1, max_length=255)
    description: str | None = Field(default=None, max_length=500)
    status: ProjectStatus = ProjectStatus.ACTIVE

# 2. Create input
class ProjectCreate(ProjectBase):
    pass

# 3. Update input (all fields optional)
class ProjectUpdate(ProjectBase):
    title: str | None = Field(default=None, min_length=1, max_length=255)  # type: ignore

# 4. Database model
class Project(ProjectBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    created_at: datetime | None = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_type=DateTime(timezone=True),
    )
    owner_id: uuid.UUID = Field(
        foreign_key="user.id",
        nullable=False,
        ondelete="CASCADE",
    )
    owner: User | None = Relationship(back_populates="projects")

# 5. Output model (public response)
class ProjectPublic(ProjectBase):
    id: uuid.UUID
    owner_id: uuid.UUID
    created_at: datetime | None = None

# 6. Response wrapper (for lists)
class ProjectsPublic(SQLModel):
    data: list[ProjectPublic]
    count: int
```

**Update User model** to include the relationship:

```python
class User(UserBase, table=True):
    # ... existing fields ...
    projects: list["Project"] = Relationship(back_populates="owner", cascade_delete=True)
```

### 3. Generate Database Migration

After adding the model to `models.py`, create an Alembic migration:

```bash
cd backend
alembic revision --autogenerate -m "add project model"
```

Review and test the generated migration:

```bash
alembic upgrade head      # Apply migration
alembic downgrade -1      # Test rollback
alembic upgrade head      # Re-apply
```

### 4. Add CRUD Operations

Use the CRUD template: [crud-template.py](./templates/crud-template.py)

**In `backend/crud.py`, add:**

```python
import uuid
from sqlmodel import Session, select, func, col
from backend.models import Project, ProjectCreate, ProjectUpdate

def create_project(
    *,
    session: Session,
    project_in: ProjectCreate,
    owner_id: uuid.UUID,
) -> Project:
    db_project = Project.model_validate(
        project_in,
        update={"owner_id": owner_id},
    )
    session.add(db_project)
    session.commit()
    session.refresh(db_project)
    return db_project

def read_projects(
    *,
    session: Session,
    owner_id: uuid.UUID,
    skip: int = 0,
    limit: int = 100,
) -> tuple[list[Project], int]:
    # Count total
    count_stmt = select(func.count()).select_from(Project).where(Project.owner_id == owner_id)
    count = session.exec(count_stmt).one()
    
    # Get paginated results
    stmt = (
        select(Project)
        .where(Project.owner_id == owner_id)
        .order_by(col(Project.created_at).desc())
        .offset(skip)
        .limit(limit)
    )
    projects = session.exec(stmt).all()
    return projects, count

def read_project(
    *,
    session: Session,
    owner_id: uuid.UUID,
    project_id: uuid.UUID,
) -> Project | None:
    stmt = select(Project).where(
        (Project.id == project_id) & (Project.owner_id == owner_id)
    )
    return session.exec(stmt).first()

def update_project(
    *,
    session: Session,
    db_project: Project,
    project_in: ProjectUpdate,
) -> Project:
    project_data = project_in.model_dump(exclude_unset=True)
    db_project.sqlmodel_update(project_data)
    session.add(db_project)
    session.commit()
    session.refresh(db_project)
    return db_project

def delete_project(
    *,
    session: Session,
    db_project: Project,
) -> None:
    session.delete(db_project)
    session.commit()
```

### 5. Create API Routes

Use the route template: [routes-template.py](./templates/routes-template.py)

**Create `backend/api/routes/projects.py`:**

```python
import uuid
from typing import Any

from fastapi import APIRouter, HTTPException
from sqlmodel import Session

from app import crud
from backend.api.deps import CurrentUser, SessionDep, get_current_active_superuser
from backend.models import (
    Project,
    ProjectCreate,
    ProjectPublic,
    ProjectsPublic,
    ProjectUpdate,
    Message,
)

router = APIRouter(prefix="/projects", tags=["projects"])

@router.get("/", response_model=ProjectsPublic)
def read_projects(
    session: SessionDep,
    current_user: CurrentUser,
    skip: int = 0,
    limit: int = 100,
) -> Any:
    """Retrieve projects for the current user."""
    projects, count = crud.read_projects(
        session=session,
        owner_id=current_user.id,
        skip=skip,
        limit=limit,
    )
    return ProjectsPublic(data=projects, count=count)

@router.post("/", response_model=ProjectPublic)
def create_project(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    project_in: ProjectCreate,
) -> Any:
    """Create a new project."""
    project = crud.create_project(
        session=session,
        project_in=project_in,
        owner_id=current_user.id,
    )
    return project

@router.get("/{project_id}", response_model=ProjectPublic)
def read_project(
    session: SessionDep,
    current_user: CurrentUser,
    project_id: uuid.UUID,
) -> Any:
    """Get a project by ID."""
    project = crud.read_project(
        session=session,
        owner_id=current_user.id,
        project_id=project_id,
    )
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project

@router.patch("/{project_id}", response_model=ProjectPublic)
def update_project(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    project_id: uuid.UUID,
    project_in: ProjectUpdate,
) -> Any:
    """Update a project."""
    project = crud.read_project(
        session=session,
        owner_id=current_user.id,
        project_id=project_id,
    )
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    project = crud.update_project(
        session=session,
        db_project=project,
        project_in=project_in,
    )
    return project

@router.delete("/{project_id}")
def delete_project(
    session: SessionDep,
    current_user: CurrentUser,
    project_id: uuid.UUID,
) -> Message:
    """Delete a project."""
    project = crud.read_project(
        session=session,
        owner_id=current_user.id,
        project_id=project_id,
    )
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    crud.delete_project(session=session, db_project=project)
    return Message(message="Project deleted successfully")
```

**Register the route** in `backend/api/main.py`:

```python
from backend.api.routes import projects

api_router = APIRouter()
api_router.include_router(projects.router)
```

### 6. Add Tests

Use the test template: [tests-template.py](./templates/tests-template.py)

**Create `backend/tests/api/routes/test_projects.py`:**

```python
import uuid

import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session

from backend.models import ProjectCreate


def test_create_project(
    client: TestClient,
    normal_user_token_headers: dict[str, str],
) -> None:
    data = {"title": "Test Project", "description": "A test project"}
    response = client.post(
        "/api/v1/projects/",
        headers=normal_user_token_headers,
        json=data,
    )
    assert response.status_code == 200
    content = response.json()
    assert content["title"] == data["title"]
    assert content["description"] == data["description"]
    assert content["owner_id"]
    assert "id" in content
    assert "created_at" in content


def test_read_projects(
    client: TestClient,
    normal_user_token_headers: dict[str, str],
) -> None:
    response = client.get(
        "/api/v1/projects/",
        headers=normal_user_token_headers,
    )
    assert response.status_code == 200
    content = response.json()
    assert "data" in content
    assert "count" in content
    assert isinstance(content["data"], list)


def test_read_project(
    client: TestClient,
    normal_user_token_headers: dict[str, str],
    db: Session,
) -> None:
    from tests.utils.project import create_random_project
    
    project = create_random_project(db)
    response = client.get(
        f"/api/v1/projects/{project.id}",
        headers=normal_user_token_headers,
    )
    assert response.status_code == 200
    content = response.json()
    assert content["id"] == str(project.id)
    assert content["title"] == project.title


def test_update_project(
    client: TestClient,
    normal_user_token_headers: dict[str, str],
    db: Session,
) -> None:
    from tests.utils.project import create_random_project
    
    project = create_random_project(db)
    data = {"title": "Updated Title"}
    response = client.patch(
        f"/api/v1/projects/{project.id}",
        headers=normal_user_token_headers,
        json=data,
    )
    assert response.status_code == 200
    content = response.json()
    assert content["title"] == data["title"]


def test_delete_project(
    client: TestClient,
    normal_user_token_headers: dict[str, str],
    db: Session,
) -> None:
    from tests.utils.project import create_random_project
    
    project = create_random_project(db)
    response = client.delete(
        f"/api/v1/projects/{project.id}",
        headers=normal_user_token_headers,
    )
    assert response.status_code == 200
    
    # Verify it's deleted
    response = client.get(
        f"/api/v1/projects/{project.id}",
        headers=normal_user_token_headers,
    )
    assert response.status_code == 404
```

**Create test utility** in `backend/tests/utils/project.py`:

```python
import uuid
from sqlmodel import Session
from backend.models import Project, ProjectCreate
from tests.utils.user import create_random_user

def create_random_project(db: Session) -> Project:
    user = create_random_user(db)
    project_in = ProjectCreate(
        title=f"Project {uuid.uuid4()}",
        description="Test project",
    )
    from app import crud
    project = crud.create_project(
        session=db,
        project_in=project_in,
        owner_id=user.id,
    )
    return project
```

### 7. Run Tests & Verify

```bash
cd backend

# Run all tests
./scripts/test.sh

# Run specific route tests
pytest tests/api/routes/test_projects.py -v

# Run coverage
pytest tests/api/routes/test_projects.py --cov=app --cov-report=term
```

### 8. Check Linting & Type Errors

```bash
cd backend

# Format code
./scripts/lint.sh

# Or manually
ruff check --fix
mypy
```

### 9. Generate Frontend Client

After backend is running, regenerate TypeScript client:

```bash
cd frontend
npm run generate-client
```

New types available: `ProjectPublic`, `ProjectCreate`, `ProjectUpdate`, `ProjectsPublic`, and `ProjectsService` class.

### 10. Add Frontend Page (Optional)

Create a new frontend page to consume the API:

```bash
# Create route file
touch frontend/src/routes/_layout/projects.tsx

# Create component folder
mkdir -p frontend/src/components/Projects

# Generate types
npm run generate-client
```

Then implement the page using patterns from [Frontend Instructions](../.../../instructions/frontend.instructions.md).

## Common Design Patterns

### Owner-Based Access Control

Always filter by `owner_id` in read operations:

```python
def read_project(*, session: Session, owner_id: uuid.UUID, project_id: uuid.UUID) -> Project | None:
    stmt = select(Project).where(
        (Project.id == project_id) & (Project.owner_id == owner_id)
    )
    return session.exec(stmt).first()
```

### Unique Constraints Per Owner

For uniqueness per user (not globally):

```python
class ProjectBase(SQLModel):
    title: str = Field(min_length=1, max_length=255)  # Indexed but not unique globally
    # Enforce uniqueness in read/create operations instead
```

### Cascading Deletes

Ensure orphans are deleted when parent is deleted:

```python
# In User model:
projects: list["Project"] = Relationship(back_populates="owner", cascade_delete=True)

# In Project model:
owner_id: uuid.UUID = Field(foreign_key="user.id", ondelete="CASCADE")
```

### Soft Deletes (Optional)

If you need to preserve records:

```python
class Project(ProjectBase, table=True):
    # ... fields ...
    deleted_at: datetime | None = Field(default=None)

def read_projects(...):
    stmt = select(Project).where(Project.deleted_at.is_(None))  # Only active projects
```

## Troubleshooting

| Issue | Solution |
|-------|----------|
| **Migration not generated** | Check that `backend/models.py` has `table=True` on DB model |
| **Import errors after changes** | Run `cd backend && uv sync` |
| **Tests fail with 404** | Verify route is registered in `api/main.py` |
| **TypeScript types not updated** | Run `cd frontend && npm run generate-client` |
| **Unique constraint violations** | Check for duplicate titles; implement deduplication logic |
| **Cascade delete not working** | Verify `cascade_delete=True` on Relationship and `ondelete="CASCADE"` on FK |
| **Type errors in CRUD** | Ensure `model_validate()` is used, not direct instantiation |

## Next Steps

1. ✅ **Frontend integration**: Create page + components using generated types
2. ✅ **Permissions**: Add role-based or resource-level permissions if needed
3. ✅ **Email notifications**: Send emails on create/update/delete if applicable
4. ✅ **Search/filtering**: Add query parameters for advanced filtering
5. ✅ **Caching**: Add Redis caching for frequently accessed projects

## Reference

- [Backend Instructions: CRUD Patterns](../../../instructions/backend.instructions.md#crud-patterns)
- [Backend Instructions: API Routes](../../../instructions/backend.instructions.md#api-route-patterns)
- [Backend Instructions: Database Migrations](../../../instructions/backend.instructions.md#database-migrations-alembic)
- [Backend Instructions: Testing](../../../instructions/backend.instructions.md#testing-patterns)
