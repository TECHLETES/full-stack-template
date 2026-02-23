# Testing Template

Use this as a starting point for your route tests. Create as `backend/tests/api/routes/test_projects.py`.

## Complete Example: Project Tests

```python
import uuid
from typing import Any

import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session

from app.models import ProjectCreate


def test_create_project(
    client: TestClient,
    normal_user_token_headers: dict[str, str],
) -> None:
    """Test creating a project."""
    data = {"title": "My Project", "description": "A test project"}
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


def test_create_project_needs_title(
    client: TestClient,
    normal_user_token_headers: dict[str, str],
) -> None:
    """Test validation: title is required."""
    data = {"description": "No title"}
    response = client.post(
        "/api/v1/projects/",
        headers=normal_user_token_headers,
        json=data,
    )
    assert response.status_code == 422  # Validation error


def test_read_projects(
    client: TestClient,
    normal_user_token_headers: dict[str, str],
) -> None:
    """Test listing projects."""
    response = client.get(
        "/api/v1/projects/",
        headers=normal_user_token_headers,
    )
    assert response.status_code == 200
    content = response.json()
    assert "data" in content
    assert "count" in content
    assert isinstance(content["data"], list)
    assert isinstance(content["count"], int)


def test_read_projects_pagination(
    client: TestClient,
    normal_user_token_headers: dict[str, str],
) -> None:
    """Test pagination parameters."""
    # Create 3 projects
    for i in range(3):
        client.post(
            "/api/v1/projects/",
            headers=normal_user_token_headers,
            json={"title": f"Project {i}"},
        )
    
    # Test skip and limit
    response = client.get(
        "/api/v1/projects/?skip=0&limit=2",
        headers=normal_user_token_headers,
    )
    assert response.status_code == 200
    content = response.json()
    assert len(content["data"]) == 2
    assert content["count"] == 3


def test_read_project(
    client: TestClient,
    normal_user_token_headers: dict[str, str],
    db: Session,
) -> None:
    """Test reading a single project."""
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


def test_read_project_not_found(
    client: TestClient,
    normal_user_token_headers: dict[str, str],
) -> None:
    """Test reading non-existent project."""
    fake_id = uuid.uuid4()
    response = client.get(
        f"/api/v1/projects/{fake_id}",
        headers=normal_user_token_headers,
    )
    assert response.status_code == 404


def test_read_project_permission_denied(
    client: TestClient,
    normal_user_token_headers: dict[str, str],
    superuser_token_headers: dict[str, str],
    db: Session,
) -> None:
    """Test accessing another user's project."""
    from tests.utils.project import create_random_project
    
    # Create project as superuser
    project = create_random_project(db)  # This will use random user, not current
    
    # Normal user should not see it
    response = client.get(
        f"/api/v1/projects/{project.id}",
        headers=normal_user_token_headers,
    )
    assert response.status_code == 404  # Treated as not found for security


def test_update_project(
    client: TestClient,
    normal_user_token_headers: dict[str, str],
    db: Session,
) -> None:
    """Test updating a project."""
    from tests.utils.project import create_random_project
    
    project = create_random_project(db)
    data = {"title": "Updated Title", "description": "Updated description"}
    response = client.patch(
        f"/api/v1/projects/{project.id}",
        headers=normal_user_token_headers,
        json=data,
    )
    assert response.status_code == 200
    content = response.json()
    assert content["title"] == data["title"]
    assert content["description"] == data["description"]


def test_update_project_partial(
    client: TestClient,
    normal_user_token_headers: dict[str, str],
    db: Session,
) -> None:
    """Test partial update (only some fields)."""
    from tests.utils.project import create_random_project
    
    project = create_random_project(db)
    original_description = project.description
    
    # Update only title
    data = {"title": "New Title"}
    response = client.patch(
        f"/api/v1/projects/{project.id}",
        headers=normal_user_token_headers,
        json=data,
    )
    assert response.status_code == 200
    content = response.json()
    assert content["title"] == "New Title"
    # Description should remain unchanged
    assert content["description"] == original_description


def test_delete_project(
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
    
    # Verify it's deleted
    response = client.get(
        f"/api/v1/projects/{project.id}",
        headers=normal_user_token_headers,
    )
    assert response.status_code == 404


def test_delete_project_not_found(
    client: TestClient,
    normal_user_token_headers: dict[str, str],
) -> None:
    """Test deleting non-existent project."""
    fake_id = uuid.uuid4()
    response = client.delete(
        f"/api/v1/projects/{fake_id}",
        headers=normal_user_token_headers,
    )
    assert response.status_code == 404


def test_unauthorized_requires_token(client: TestClient) -> None:
    """Test that endpoints require authentication."""
    response = client.get("/api/v1/projects/")
    assert response.status_code == 403  # Forbidden
```

## Test Utility

Create `backend/tests/utils/project.py`:

```python
import uuid

from sqlmodel import Session

from app import crud
from app.models import Project, ProjectCreate
from tests.utils.user import create_random_user


def create_random_project(db: Session) -> Project:
    """Create a random project for testing."""
    user = create_random_user(db)
    project_in = ProjectCreate(
        title=f"Project {uuid.uuid4()}",
        description="Test project description",
    )
    project = crud.create_project(
        session=db,
        project_in=project_in,
        owner_id=user.id,
    )
    return project
```

## Pattern Notes

### Test Fixtures
- `client: TestClient` — FastAPI test client
- `normal_user_token_headers` — auth headers for regular user
- `superuser_token_headers` — auth headers for admin
- `db: Session` — database session for setup

### Naming Convention
- `test_<action>_<scenario>` (e.g., `test_create_project`)
- `test_<action>_<scenario>_<edge_case>` (e.g., `test_read_project_not_found`)

### Status Codes
- `200` — Success
- `201` — Created (optional, FastAPI defaults to 200 for POST)
- `204` — No Content (DELETE can return this)
- `400` — Bad Request (validation error)
- `403` — Forbidden (no token or wrong permissions)
- `404` — Not Found (resource doesn't exist)
- `422` — Unprocessable Entity (validation error detail)

### Test Organization
1. **Happy path**: Normal successful operations
2. **Validation**: Missing/invalid required fields
3. **Not found**: Non-existent resources
4. **Permission**: Access control (other user's resources)
5. **Edge cases**: Pagination, partial updates, etc.

## Running Tests

```bash
# Run all tests
cd backend && ./scripts/test.sh

# Run specific test file
pytest tests/api/routes/test_projects.py -v

# Run specific test
pytest tests/api/routes/test_projects.py::test_create_project -v

# Run with coverage
pytest tests/api/routes/test_projects.py --cov=app
```

## After Creating Tests

1. Save utility as `backend/tests/utils/project.py`
2. Save tests as `backend/tests/api/routes/test_projects.py`
3. Run `./scripts/test.sh` to verify
4. Check coverage: `pytest --cov=app`
5. All tests should pass before committing
