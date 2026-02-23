# API Routes Template

Use this as a starting point for your route file. Create as `backend/app/api/routes/projects.py`.

## Complete Example: Project Routes

```python
import uuid
from typing import Any

from fastapi import APIRouter, HTTPException
from sqlmodel import Session

from app import crud
from app.api.deps import CurrentUser, SessionDep
from app.models import (
    Message,
    Project,
    ProjectCreate,
    ProjectPublic,
    ProjectsPublic,
    ProjectUpdate,
)

router = APIRouter(prefix="/projects", tags=["projects"])


@router.get("/", response_model=ProjectsPublic)
def read_projects(
    session: SessionDep,
    current_user: CurrentUser,
    skip: int = 0,
    limit: int = 100,
) -> Any:
    """
    Retrieve projects for the current user.
    
    Returns paginated list with total count.
    """
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
        raise HTTPException(
            status_code=404,
            detail="Project not found",
        )
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
        raise HTTPException(
            status_code=404,
            detail="Project not found",
        )
    
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
        raise HTTPException(
            status_code=404,
            detail="Project not found",
        )
    
    crud.delete_project(session=session, db_project=project)
    return Message(message="Project deleted successfully")
```

## Route Registration

After creating `backend/app/api/routes/projects.py`, register in `backend/app/api/main.py`:

```python
from .routes import projects

api_router = APIRouter()
api_router.include_router(projects.router)
# ... other routers
```

## Pattern Notes

### Dependency Injection
- `SessionDep` — database session
- `CurrentUser` — authenticated user from JWT
- These prevent repetition and ensure consistency

### Error Responses
- Use `HTTPException(status_code=404)` for not found
- Use `status_code=403` for permission denied
- Let FastAPI handle 400 validation errors automatically

### Response Models
- Always specify `response_model` in decorator
- FastAPI validates response against model
- Prevents accidentally leaking internal fields

### Authorization
- Always pass `owner_id` from `current_user.id` to CRUD
- Never trust path params for access control
- Check ownership before modifying

### Documentation
- Add docstrings to each route (shown in `/docs`)
- Describe what the route does, not how

## Common Variations

### With Filtering

```python
@router.get("/", response_model=ProjectsPublic)
def read_projects(
    session: SessionDep,
    current_user: CurrentUser,
    status: ProjectStatus | None = None,
    skip: int = 0,
    limit: int = 100,
) -> Any:
    """Retrieve projects, optionally filtered by status."""
    if status:
        projects, count = crud.read_projects_by_status(
            session=session,
            owner_id=current_user.id,
            status=status,
            skip=skip,
            limit=limit,
        )
    else:
        projects, count = crud.read_projects(
            session=session,
            owner_id=current_user.id,
            skip=skip,
            limit=limit,
        )
    return ProjectsPublic(data=projects, count=count)
```

### With Search

```python
@router.get("/", response_model=ProjectsPublic)
def read_projects(
    session: SessionDep,
    current_user: CurrentUser,
    search: str | None = None,
    skip: int = 0,
    limit: int = 100,
) -> Any:
    """Search and list projects."""
    if search:
        projects, count = crud.search_projects(
            session=session,
            owner_id=current_user.id,
            search=search,
            skip=skip,
            limit=limit,
        )
    else:
        projects, count = crud.read_projects(
            session=session,
            owner_id=current_user.id,
            skip=skip,
            limit=limit,
        )
    return ProjectsPublic(data=projects, count=count)
```

### Admin-Only Endpoints

```python
from app.api.deps import get_current_active_superuser

@router.delete("/{project_id}", dependencies=[Depends(get_current_active_superuser)])
def admin_delete_project(
    session: SessionDep,
    project_id: uuid.UUID,
) -> Message:
    """Admin: Delete any project."""
    project = session.get(Project, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    crud.delete_project(session=session, db_project=project)
    return Message(message="Project deleted successfully")
```

## After Creating Routes

1. Save as `backend/app/api/routes/projects.py`
2. Register in `backend/app/api/main.py`
3. Run `cd backend && ./scripts/lint.sh` to format
4. Start server: `uv run fastapi dev app/main.py`
5. Check `/docs` → "projects" should appear
6. Test endpoints in interactive docs
