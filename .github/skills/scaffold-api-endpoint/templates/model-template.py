# SQLModel Template

Use this as a starting point for your database model. Copy and modify for your resource.

## Complete Example: Project

```python
import uuid
from datetime import datetime, timezone
from enum import Enum
from pydantic import Field
from sqlalchemy import DateTime
from sqlmodel import Relationship, SQLModel

def get_datetime_utc() -> datetime:
    return datetime.now(timezone.utc)

# Optional: Enum for fixed values
class ProjectStatus(str, Enum):
    ACTIVE = "active"
    ARCHIVED = "archived"

# 1. Shared properties (Base)
class ProjectBase(SQLModel):
    title: str = Field(min_length=1, max_length=255)
    description: str | None = Field(default=None, max_length=500)
    status: ProjectStatus = ProjectStatus.ACTIVE

# 2. Properties to receive on creation
class ProjectCreate(ProjectBase):
    pass  # Can override specific fields

# 3. Properties to receive on update (all optional)
class ProjectUpdate(ProjectBase):
    title: str | None = Field(default=None, min_length=1, max_length=255)  # type: ignore
    description: str | None = Field(default=None, max_length=500)  # type: ignore
    status: ProjectStatus | None = None  # type: ignore

# 4. Database model (table=True, inferred from class name: "project")
class Project(ProjectBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    created_at: datetime | None = Field(
        default_factory=get_datetime_utc,
        sa_type=DateTime(timezone=True),  # type: ignore
    )
    owner_id: uuid.UUID = Field(
        foreign_key="user.id",
        nullable=False,
        ondelete="CASCADE",
    )
    owner: "User | None" = Relationship(back_populates="projects")

# 5. Properties to return via API (id is required)
class ProjectPublic(ProjectBase):
    id: uuid.UUID
    owner_id: uuid.UUID
    created_at: datetime | None = None

# 6. Response wrapper for lists
class ProjectsPublic(SQLModel):
    data: list[ProjectPublic]
    count: int
```

## Pattern Notes

- **Base**: Shared across all models (input, output, database)
- **Create**: No ID (auto-generated), no timestamps
- **Update**: All fields optional, use `# type: ignore` on optional overrides
- **Database**: Uses `table=True`, has ID + timestamps + FK + relationships
- **Public**: No secrets, has ID + timestamps, no hashed_password/sensitive data
- **Wrapper**: For paginated lists (data + count)

## Key Field Validation

```python
# String constraints
title: str = Field(min_length=1, max_length=255)

# Numeric constraints
priority: int = Field(ge=1, le=10)  # 1-10

# Email (imported from pydantic)
from pydantic import EmailStr
email: EmailStr = Field(unique=True, index=True)

# Optional with default
description: str | None = Field(default=None, max_length=500)

# Enum
status: ProjectStatus = ProjectStatus.ACTIVE

# Boolean
is_archived: bool = Field(default=False)

# Database constraints
Field(unique=True, index=True)      # Unique + indexed
Field(foreign_key="user.id", nullable=False, ondelete="CASCADE")
```

## Relationship Patterns

### One-to-Many (User → Projects)

```python
# In User model:
projects: list["Project"] = Relationship(back_populates="owner", cascade_delete=True)

# In Project model:
owner_id: uuid.UUID = Field(foreign_key="user.id", nullable=False, ondelete="CASCADE")
owner: "User | None" = Relationship(back_populates="projects")
```

### Many-to-Many (Users ↔ Teams)

```python
# Define association table
class ProjectUser(SQLModel, table=True):
    project_id: uuid.UUID = Field(foreign_key="project.id", primary_key=True)
    user_id: uuid.UUID = Field(foreign_key="user.id", primary_key=True)

# In Project model:
users: list["User"] = Relationship(back_populates="projects", link_model=ProjectUser)

# In User model:
projects: list["Project"] = Relationship(back_populates="users", link_model=ProjectUser)
```

### Nested Response

Include related data in API response:

```python
class ProjectPublic(ProjectBase):
    id: uuid.UUID
    owner_id: uuid.UUID
    created_at: datetime | None = None
    # Optionally include nested
    owner: UserPublic | None = None
```

## After Creating the Model

1. Add model to `backend/app/models.py`
2. Add relationship to parent model (e.g., add to `User`)
3. Create migration: `alembic revision --autogenerate -m "add project model"`
4. Test migration: `alembic upgrade head` then `alembic downgrade -1` then `alembic upgrade head`
