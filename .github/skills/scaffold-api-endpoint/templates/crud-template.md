# CRUD Operations Template

Use this as a starting point for your CRUD functions. Add these to `backend/crud.py`.

## Complete Example: Project CRUD

```python
import uuid
from typing import Any

from sqlmodel import Session, col, func, select

from backend.models import Project, ProjectCreate, ProjectUpdate


def create_project(
    *,
    session: Session,
    project_in: ProjectCreate,
    owner_id: uuid.UUID,
) -> Project:
    """Create a new project for the given owner."""
    db_obj = Project.model_validate(
        project_in,
        update={"owner_id": owner_id},
    )
    session.add(db_obj)
    session.commit()
    session.refresh(db_obj)
    return db_obj


def read_projects(
    *,
    session: Session,
    owner_id: uuid.UUID,
    skip: int = 0,
    limit: int = 100,
) -> tuple[list[Project], int]:
    """Read paginated projects for a user."""
    # Get total count
    count_statement = select(func.count()).select_from(Project).where(
        Project.owner_id == owner_id
    )
    count = session.exec(count_statement).one()

    # Get paginated results, ordered by newest first
    statement = (
        select(Project)
        .where(Project.owner_id == owner_id)
        .order_by(col(Project.created_at).desc())
        .offset(skip)
        .limit(limit)
    )
    projects = session.exec(statement).all()

    return projects, count


def read_project(
    *,
    session: Session,
    owner_id: uuid.UUID,
    project_id: uuid.UUID,
) -> Project | None:
    """Read a single project by ID (owned by user)."""
    statement = select(Project).where(
        (Project.id == project_id) & (Project.owner_id == owner_id)
    )
    return session.exec(statement).first()


def update_project(
    *,
    session: Session,
    db_project: Project,
    project_in: ProjectUpdate,
) -> Project:
    """Update a project."""
    # Only update fields that were explicitly provided
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
    """Delete a project."""
    session.delete(db_project)
    session.commit()
```

## Pattern Notes

### Create
- Use `model_validate()` to convert Pydantic model to DB model
- Use `update={}` to add fields not in input (like `owner_id`)
- Always `session.commit()` and `session.refresh()`

### Read (List)
- Count total with `select(func.count())`
- Return tuple of `(items, count)` for pagination
- Order by `created_at` descending (newest first)
- Filter by `owner_id` for access control

### Read (Single)
- Filter by both ID and `owner_id` (prevents accessing other users' data)
- Return `None` if not found (let route handle 404)

### Update
- Use `model_dump(exclude_unset=True)` to only update provided fields
- Use `sqlmodel_update()` to apply changes
- Always refresh to get database defaults

### Delete
- Simple `session.delete()` + `commit()`
- Cascade deletes handled by database FK constraints

## Variations

### With Status Filter

```python
def read_active_projects(
    *,
    session: Session,
    owner_id: uuid.UUID,
) -> list[Project]:
    """Read only active (non-archived) projects."""
    statement = select(Project).where(
        (Project.owner_id == owner_id) & (Project.status == ProjectStatus.ACTIVE)
    ).order_by(col(Project.created_at).desc())
    return session.exec(statement).all()
```

### With Search

```python
def search_projects(
    *,
    session: Session,
    owner_id: uuid.UUID,
    search: str,
) -> list[Project]:
    """Search projects by title."""
    statement = select(Project).where(
        (Project.owner_id == owner_id)
        & (Project.title.ilike(f"%{search}%"))
    )
    return session.exec(statement).all()
```

### With Sorting

```python
def read_projects_sorted(
    *,
    session: Session,
    owner_id: uuid.UUID,
    sort_by: str = "created_at",
    skip: int = 0,
    limit: int = 100,
) -> tuple[list[Project], int]:
    """Read projects with custom sorting."""
    count_statement = select(func.count()).select_from(Project).where(
        Project.owner_id == owner_id
    )
    count = session.exec(count_statement).one()

    order_by_field = getattr(Project, sort_by, Project.created_at)
    statement = (
        select(Project)
        .where(Project.owner_id == owner_id)
        .order_by(order_by_field.desc())
        .offset(skip)
        .limit(limit)
    )
    projects = session.exec(statement).all()

    return projects, count
```

## After Creating CRUD Operations

1. Import the model at the top of `crud.py`
2. Register in route file with dependency injection
3. Write tests in `tests/api/routes/test_projects.py`
4. Run `./scripts/test.sh` to verify
