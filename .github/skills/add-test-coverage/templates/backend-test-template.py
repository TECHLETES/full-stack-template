# Backend Test Template
# Use this as a starting point for new test files.
# Copy this template and adapt it for your feature.

import uuid
import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session

# ============================================================================
# UNIT TESTS - Test CRUD functions in isolation (fast)
# ============================================================================


def test_create_resource(db: Session) -> None:
    """Test creating a resource via CRUD.
    
    Pattern:
    1. Create prerequisites (user, parent resource)
    2. Create target resource
    3. Assert success and properties
    """
    from app import crud
    from backend.models import ResourceCreate
    from tests.utils.resource import create_random_user
    
    user = create_random_user(db)
    resource_in = ResourceCreate(
        title="Test Resource",
        description="A test resource",
    )
    
    resource = crud.create_resource(
        session=db,
        resource_in=resource_in,
        owner_id=user.id,
    )
    
    assert resource.id
    assert resource.title == "Test Resource"
    assert resource.owner_id == user.id
    assert resource.created_at


def test_read_resource_by_id(db: Session) -> None:
    """Test reading a specific resource."""
    from app import crud
    from tests.utils.resource import create_random_resource
    
    resource = create_random_resource(db)
    
    db_resource = crud.read_resource(
        session=db,
        resource_id=resource.id,
        owner_id=resource.owner_id,
    )
    
    assert db_resource
    assert db_resource.id == resource.id
    assert db_resource.title == resource.title


def test_read_resource_returns_none_if_not_found(db: Session) -> None:
    """Test reading non-existent resource returns None."""
    from app import crud
    from tests.utils.resource import create_random_user
    
    user = create_random_user(db)
    
    resource = crud.read_resource(
        session=db,
        resource_id=uuid.uuid4(),
        owner_id=user.id,
    )
    
    assert resource is None


def test_read_resources_list(db: Session) -> None:
    """Test listing all resources for a user with pagination."""
    from app import crud
    from tests.utils.resource import create_random_resource
    
    # Create multiple resources
    for _ in range(5):
        create_random_resource(db)
    
    # Read first page
    resources, count = crud.read_resources(
        session=db,
        owner_id=uuid.uuid4(),  # Use real owner ID in practice
        skip=0,
        limit=10,
    )
    
    assert isinstance(resources, list)
    assert isinstance(count, int)
    assert count >= 0


def test_update_resource_full(db: Session) -> None:
    """Test full update of a resource."""
    from app import crud
    from backend.models import ResourceUpdate
    from tests.utils.resource import create_random_resource
    
    resource = create_random_resource(db)
    update_data = ResourceUpdate(
        title="Updated Title",
        description="Updated Description",
    )
    
    updated = crud.update_resource(
        session=db,
        db_resource=resource,
        resource_in=update_data,
    )
    
    assert updated.title == "Updated Title"
    assert updated.description == "Updated Description"


def test_update_resource_partial(db: Session) -> None:
    """Test partial update (only some fields).
    
    Pattern:
    1. Create resource with original values
    2. Update only one field
    3. Assert updated field and unchanged field
    """
    from app import crud
    from backend.models import ResourceUpdate
    from tests.utils.resource import create_random_resource
    
    resource = create_random_resource(db)
    original_description = resource.description
    
    # Update only title, leave description unchanged
    update_data = ResourceUpdate(title="New Title")
    
    updated = crud.update_resource(
        session=db,
        db_resource=resource,
        resource_in=update_data,
    )
    
    assert updated.title == "New Title"
    assert updated.description == original_description


def test_delete_resource(db: Session) -> None:
    """Test deleting a resource.
    
    Pattern:
    1. Create resource
    2. Delete it
    3. Verify it no longer exists
    """
    from app import crud
    from tests.utils.resource import create_random_resource
    
    resource = create_random_resource(db)
    resource_id = resource.id
    owner_id = resource.owner_id
    
    crud.delete_resource(session=db, db_resource=resource)
    
    # Verify deleted
    result = crud.read_resource(
        session=db,
        resource_id=resource_id,
        owner_id=owner_id,
    )
    assert result is None


@pytest.mark.parametrize("title,valid", [
    ("Valid Title", True),
    ("Another Valid", True),
    ("", False),  # Empty title invalid
    ("x" * 500, False),  # Too long
])
def test_create_resource_validation(title: str, valid: bool, db: Session) -> None:
    """Test resource creation validates input.
    
    Pattern:
    - Use parametrize to test multiple scenarios
    - Test valid and invalid cases
    """
    from backend.models import ResourceCreate
    from pydantic import ValidationError
    
    try:
        resource_in = ResourceCreate(title=title, description="test")
        if not valid:
            pytest.fail(f"Should have raised ValidationError for title: {title}")
    except ValidationError:
        if valid:
            pytest.fail(f"Should not raise ValidationError for title: {title}")


# ============================================================================
# INTEGRATION TESTS - Test full HTTP routes (slower, use real DB)
# ============================================================================


def test_create_resource_endpoint_success(
    client: TestClient,
    normal_user_token_headers: dict[str, str],
) -> None:
    """Test creating resource via HTTP endpoint.
    
    Pattern:
    1. POST to endpoint with auth headers
    2. Assert 200 response
    3. Assert response contains expected data
    """
    data = {
        "title": "Test Resource",
        "description": "A test resource",
    }
    
    response = client.post(
        "/api/v1/resources/",
        headers=normal_user_token_headers,
        json=data,
    )
    
    assert response.status_code == 200
    content = response.json()
    assert content["title"] == data["title"]
    assert content["description"] == data["description"]
    assert content["owner_id"]
    assert content["id"]


def test_create_resource_endpoint_validation(
    client: TestClient,
    normal_user_token_headers: dict[str, str],
) -> None:
    """Test endpoint validation rejects invalid data.
    
    Pattern:
    - Test missing required fields → 422
    - Test invalid data types → 422
    """
    # Missing title (required)
    response = client.post(
        "/api/v1/resources/",
        headers=normal_user_token_headers,
        json={"description": "Missing title"},
    )
    
    assert response.status_code == 422


def test_create_resource_endpoint_requires_auth(client: TestClient) -> None:
    """Test endpoint requires authentication.
    
    Pattern:
    - Request without auth headers → 403
    """
    response = client.post(
        "/api/v1/resources/",
        json={"title": "Test"},
    )
    
    assert response.status_code == 403


def test_read_resources_endpoint_success(
    client: TestClient,
    normal_user_token_headers: dict[str, str],
    db: Session,
) -> None:
    """Test listing resources."""
    from tests.utils.resource import create_random_resource
    
    # Create test data
    for _ in range(3):
        create_random_resource(db)
    
    response = client.get(
        "/api/v1/resources/",
        headers=normal_user_token_headers,
    )
    
    assert response.status_code == 200
    content = response.json()
    assert "data" in content
    assert "count" in content
    assert isinstance(content["data"], list)
    assert isinstance(content["count"], int)


def test_read_resources_pagination(
    client: TestClient,
    normal_user_token_headers: dict[str, str],
) -> None:
    """Test pagination parameters work."""
    response = client.get(
        "/api/v1/resources/?skip=0&limit=10",
        headers=normal_user_token_headers,
    )
    
    assert response.status_code == 200


def test_read_resource_endpoint_not_found(
    client: TestClient,
    normal_user_token_headers: dict[str, str],
) -> None:
    """Test reading non-existent resource.
    
    Pattern:
    - Request with invalid ID → 404
    """
    response = client.get(
        f"/api/v1/resources/{uuid.uuid4()}",
        headers=normal_user_token_headers,
    )
    
    assert response.status_code == 404


def test_read_resource_forbidden_if_not_owner(
    client: TestClient,
    normal_user_token_headers: dict[str, str],
    superuser_token_headers: dict[str, str],
    db: Session,
) -> None:
    """Test user can't read another user's resource.
    
    Pattern:
    - Create resource as superuser
    - Try to read as normal user
    - Should be 404 (not 403 for security)
    """
    from tests.utils.resource import create_random_resource
    
    # Create as superuser
    resource = create_random_resource(db)
    
    # Read as normal user (different user)
    response = client.get(
        f"/api/v1/resources/{resource.id}",
        headers=normal_user_token_headers,
    )
    
    assert response.status_code == 404


def test_update_resource_endpoint_success(
    client: TestClient,
    normal_user_token_headers: dict[str, str],
    db: Session,
) -> None:
    """Test updating a resource."""
    from tests.utils.resource import create_random_resource
    
    resource = create_random_resource(db)
    
    response = client.patch(
        f"/api/v1/resources/{resource.id}",
        headers=normal_user_token_headers,
        json={"title": "Updated Title"},
    )
    
    assert response.status_code == 200
    content = response.json()
    assert content["title"] == "Updated Title"


def test_delete_resource_endpoint_success(
    client: TestClient,
    normal_user_token_headers: dict[str, str],
    db: Session,
) -> None:
    """Test deleting a resource."""
    from tests.utils.resource import create_random_resource
    
    resource = create_random_resource(db)
    
    response = client.delete(
        f"/api/v1/resources/{resource.id}",
        headers=normal_user_token_headers,
    )
    
    assert response.status_code == 200
    
    # Verify deleted
    response = client.get(
        f"/api/v1/resources/{resource.id}",
        headers=normal_user_token_headers,
    )
    assert response.status_code == 404
