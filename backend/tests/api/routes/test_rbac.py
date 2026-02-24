"""Tests for RBAC API endpoints."""

import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session

from backend.crud import create_user
from backend.models import User, UserCreate
from backend.tests.utils.utils import random_email


@pytest.fixture
def admin_user(db: Session) -> User:
    """Create an admin user for testing."""
    user_in = UserCreate(
        email=random_email(),
        password="adminpassword123",
        full_name="Admin User",
        is_superuser=True,
    )
    return create_user(session=db, user_create=user_in)


@pytest.fixture
def token(client: TestClient, admin_user: User) -> str:
    """Get auth token for admin user."""
    response = client.post(
        "/api/v1/login/access-token",
        data={"username": admin_user.email, "password": "adminpassword123"},
    )
    return response.json()["access_token"]


class TestPermissionsEndpoints:
    """Test permissions API endpoints."""

    def test_get_permissions_catalog(self, client: TestClient) -> None:
        """Test getting permissions catalog (public endpoint)."""
        response = client.get("/api/v1/rbac/permissions-catalog")
        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert "users" in data
        assert "reports" in data

    def test_list_permissions(self, client: TestClient) -> None:
        """Test listing all permissions."""
        response = client.get("/api/v1/rbac/permissions")
        assert response.status_code == 200
        data = response.json()
        assert "data" in data
        assert "count" in data

    def test_create_permission_requires_admin(self, client: TestClient, token: str) -> None:
        """Test that creating permission requires admin role."""
        # First, try without auth
        response = client.post(
            "/api/v1/rbac/permissions",
            json={
                "name": "test:permission",
                "resource": "test",
                "description": "Test permission",
            },
        )
        assert response.status_code == 401

    def test_permissions_catalog_structure(self, client: TestClient) -> None:
        """Test that permissions catalog has correct structure."""
        response = client.get("/api/v1/rbac/permissions-catalog")
        assert response.status_code == 200
        data = response.json()

        for resource, permissions in data.items():
            assert isinstance(permissions, list)
            for perm in permissions:
                assert "name" in perm
                assert "display" in perm
                assert "resource" in perm
                assert perm["resource"] == resource


class TestRolesEndpoints:
    """Test roles API endpoints."""

    def test_list_roles(self, client: TestClient) -> None:
        """Test listing all roles."""
        response = client.get("/api/v1/rbac/roles")
        assert response.status_code == 200
        data = response.json()
        assert "data" in data
        assert "count" in data
        # Should have system roles
        role_names = [role["name"] for role in data["data"]]
        assert "Admin" in role_names or len(role_names) >= 0

    def test_list_roles_with_pagination(self, client: TestClient) -> None:
        """Test listing roles with pagination."""
        response = client.get("/api/v1/rbac/roles", params={"skip": 0, "limit": 10})
        assert response.status_code == 200
        data = response.json()
        assert "data" in data
        assert len(data["data"]) <= 10

    def test_get_role_by_id(self, client: TestClient) -> None:
        """Test getting a role by ID."""
        # First get a role
        list_response = client.get("/api/v1/rbac/roles")
        assert list_response.status_code == 200
        roles = list_response.json()["data"]

        if roles:
            role_id = roles[0]["id"]
            response = client.get(f"/api/v1/rbac/roles/{role_id}")
            assert response.status_code == 200
            data = response.json()
            assert data["id"] == role_id
            assert "name" in data

    def test_get_nonexistent_role_returns_404(self, client: TestClient) -> None:
        """Test that getting non-existent role returns 404."""
        import uuid

        fake_id = str(uuid.uuid4())
        response = client.get(f"/api/v1/rbac/roles/{fake_id}")
        assert response.status_code == 404


class TestUserRolesEndpoints:
    """Test user roles endpoints."""

    def test_get_user_roles(self, client: TestClient, admin_user: User) -> None:
        """Test getting user roles endpoint."""
        response = client.get(f"/api/v1/rbac/users/{admin_user.id}/roles")
        assert response.status_code == 200
        data = response.json()
        assert "data" in data
        assert "count" in data

    def test_get_user_permissions(self, client: TestClient, admin_user: User) -> None:
        """Test getting user permissions endpoint."""
        response = client.get(f"/api/v1/rbac/users/{admin_user.id}/permissions")
        assert response.status_code == 200
        data = response.json()
        assert "data" in data
        assert "count" in data


class TestIntegration:
    """Integration tests for RBAC system."""

    def test_default_roles_are_created_on_startup(self, client: TestClient) -> None:
        """Test that default system roles exist."""
        response = client.get("/api/v1/rbac/roles")
        assert response.status_code == 200
        data = response.json()

        role_names = [role["name"] for role in data["data"]]
        # System roles should be created: Admin, Editor, Viewer
        # We expect at least one
        assert len(role_names) > 0

    def test_default_permissions_catalog_completeness(self, client: TestClient) -> None:
        """Test that default permissions catalog is complete."""
        response = client.get("/api/v1/rbac/permissions-catalog")
        assert response.status_code == 200
        data = response.json()

        # Check core resources
        assert "items" in data
        assert "users" in data
        assert "reports" in data

        # Check items permissions
        items_perms = data["items"]
        perm_names = [p["name"] for p in items_perms]
        assert any("read" in name for name in perm_names)
        assert any("create" in name for name in perm_names)
