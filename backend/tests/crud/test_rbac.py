"""Tests for RBAC (roles, permissions, and authorization)."""

import uuid

import pytest
from sqlmodel import Session

from backend.crud import create_user
from backend.crud_rbac import (
    add_permission_to_role,
    assign_role_to_user,
    create_permission,
    create_role,
    delete_role,
    get_all_permissions,
    get_all_roles,
    get_role_by_name,
    get_user_permissions,
    get_user_roles,
    remove_permission_from_role,
    remove_role_from_user,
    user_has_permission,
    user_has_role,
)
from backend.models import (
    PermissionCreate,
    RoleCreate,
    UserCreate,
)
from backend.tests.utils.utils import random_email, random_lower_string


@pytest.fixture
def admin_role(db: Session):
    """Create an admin role for testing."""
    role_data = RoleCreate(
        name=f"Admin_{random_lower_string()}",
        description="Administrator role",
        permission_ids=[],
    )
    return create_role(session=db, role_in=role_data, is_system=True)


@pytest.fixture
def editor_role(db: Session):
    """Create an editor role for testing."""
    role_data = RoleCreate(
        name=f"Editor_{random_lower_string()}",
        description="Editor role",
        permission_ids=[],
    )
    return create_role(session=db, role_in=role_data, is_system=False)


@pytest.fixture
def create_permission_fixture(db: Session):
    """Create permissions for testing."""

    def _create_permission(name: str, resource: str, description: str | None = None):
        perm_data = PermissionCreate(
            name=name,
            resource=resource,
            description=description or f"{name} permission",
        )
        return create_permission(session=db, permission_in=perm_data)

    return _create_permission


@pytest.fixture
def test_user(db: Session):
    """Create a test user."""
    user_in = UserCreate(
        email=random_email(),
        password="testpassword123",
        full_name="Test User",
    )
    return create_user(session=db, user_create=user_in)


class TestPermissions:
    """Test permission CRUD operations."""

    def test_create_permission(self, db: Session):
        """Test creating a permission."""
        name = f"items:read_{random_lower_string()}"
        perm_data = PermissionCreate(
            name=name,
            resource="items",
            description="Read items",
        )
        perm = create_permission(session=db, permission_in=perm_data)

        assert perm.id is not None
        assert perm.name == name
        assert perm.resource == "items"

    def test_get_all_permissions(self, db: Session, create_permission_fixture):
        """Test getting all permissions."""
        suffix = random_lower_string()
        name1 = f"items:read_{suffix}"
        name2 = f"items:write_{suffix}"
        perm1 = create_permission_fixture(name=name1, resource="items")
        perm2 = create_permission_fixture(name=name2, resource="items")

        perms, count = get_all_permissions(session=db)
        assert count >= 2
        perm_names = [p.name for p in perms]
        assert name1 in perm_names
        assert name2 in perm_names

    def test_get_all_permissions_with_pagination(
        self, db: Session, create_permission_fixture
    ):
        """Test pagination of permission list."""
        suffix = random_lower_string()
        for i in range(5):
            create_permission_fixture(name=f"perm:action{i}_{suffix}", resource="test")

        perms, count = get_all_permissions(session=db, skip=0, limit=2)
        assert len(perms) == 2
        assert count >= 5


class TestRoles:
    """Test role CRUD operations."""

    def test_create_role(self, db: Session):
        """Test creating a role."""
        name = f"Viewer_{random_lower_string()}"
        role_data = RoleCreate(
            name=name,
            description="View-only role",
            permission_ids=[],
        )
        role = create_role(session=db, role_in=role_data)

        assert role.id is not None
        assert role.name == name
        assert role.description == "View-only role"
        assert not role.is_system

    def test_create_system_role(self, db: Session):
        """Test creating a system role."""
        role_data = RoleCreate(
            name=f"SuperAdmin_{random_lower_string()}",
            description="Super admin role",
            permission_ids=[],
        )
        role = create_role(session=db, role_in=role_data, is_system=True)

        assert role.is_system is True

    def test_get_role_by_name(self, db: Session, admin_role):
        """Test getting role by name."""
        role = get_role_by_name(session=db, name=admin_role.name)
        assert role is not None
        assert role.name == admin_role.name

    def test_get_all_roles(self, db: Session, admin_role, editor_role):
        """Test getting all roles."""
        roles, count = get_all_roles(session=db)
        assert count >= 2
        role_names = [r.name for r in roles]
        assert admin_role.name in role_names
        assert editor_role.name in role_names

    def test_delete_role(self, db: Session):
        """Test deleting a non-system role."""
        name = f"TempRole_{random_lower_string()}"
        role_data = RoleCreate(
            name=name,
            description="Temporary role",
            permission_ids=[],
        )
        role = create_role(session=db, role_in=role_data, is_system=False)

        success = delete_role(session=db, role_id=role.id)
        assert success is True

        deleted_role = get_role_by_name(session=db, name=name)
        assert deleted_role is None

    def test_cannot_delete_system_role(self, db: Session, admin_role):
        """Test that system roles cannot be deleted."""
        success = delete_role(session=db, role_id=admin_role.id)
        assert success is False


class TestRolePermissions:
    """Test role-permission mapping."""

    def test_add_permission_to_role(
        self, db: Session, admin_role, create_permission_fixture
    ):
        """Test adding permission to role."""
        perm_name = f"items:delete_{random_lower_string()}"
        perm = create_permission_fixture(name=perm_name, resource="items")

        success = add_permission_to_role(
            session=db, role_id=admin_role.id, permission_id=perm.id
        )
        assert success is True

        # Verify permission was added
        role = get_role_by_name(session=db, name=admin_role.name)
        assert role is not None
        perm_names = [p.name for p in role.permissions or []]
        assert perm_name in perm_names

    def test_remove_permission_from_role(
        self, db: Session, admin_role, create_permission_fixture
    ):
        """Test removing permission from role."""
        perm_name = f"items:create_{random_lower_string()}"
        perm = create_permission_fixture(name=perm_name, resource="items")

        add_permission_to_role(
            session=db, role_id=admin_role.id, permission_id=perm.id
        )

        success = remove_permission_from_role(
            session=db, role_id=admin_role.id, permission_id=perm.id
        )
        assert success is True

        role = get_role_by_name(session=db, name=admin_role.name)
        assert role is not None
        perm_names = [p.name for p in role.permissions or []]
        assert perm_name not in perm_names

    def test_cannot_add_invalid_permission_to_role(self, db: Session, admin_role):
        """Test error when adding non-existent permission."""
        fake_perm_id = uuid.uuid4()
        success = add_permission_to_role(
            session=db, role_id=admin_role.id, permission_id=fake_perm_id
        )
        assert success is False


class TestUserRoles:
    """Test user-role mapping."""

    def test_assign_role_to_user(self, db: Session, test_user, admin_role):
        """Test assigning role to user."""
        success = assign_role_to_user(
            session=db, user_id=test_user.id, role_id=admin_role.id
        )
        assert success is True

        user_roles = get_user_roles(session=db, user_id=test_user.id)
        role_names = [r.name for r in user_roles]
        assert admin_role.name in role_names

    def test_remove_role_from_user(self, db: Session, test_user, admin_role):
        """Test removing role from user."""
        assign_role_to_user(
            session=db, user_id=test_user.id, role_id=admin_role.id
        )

        success = remove_role_from_user(
            session=db, user_id=test_user.id, role_id=admin_role.id
        )
        assert success is True

        user_roles = get_user_roles(session=db, user_id=test_user.id)
        assert len(user_roles) == 0

    def test_user_has_role(self, db: Session, test_user, admin_role):
        """Test checking if user has role."""
        assign_role_to_user(
            session=db, user_id=test_user.id, role_id=admin_role.id
        )

        has_admin = user_has_role(
            session=db, user_id=test_user.id, role_name=admin_role.name
        )
        assert has_admin is True

        has_editor = user_has_role(
            session=db, user_id=test_user.id, role_name=f"NonExistent_{random_lower_string()}"
        )
        assert has_editor is False


class TestUserPermissions:
    """Test user permissions through roles."""

    def test_get_user_permissions(
        self, db: Session, test_user, admin_role, create_permission_fixture
    ):
        """Test getting all permissions for a user."""
        suffix = random_lower_string()
        name1 = f"items:read_{suffix}"
        name2 = f"items:write_{suffix}"
        perm1 = create_permission_fixture(name=name1, resource="items")
        perm2 = create_permission_fixture(name=name2, resource="items")

        add_permission_to_role(
            session=db, role_id=admin_role.id, permission_id=perm1.id
        )
        add_permission_to_role(
            session=db, role_id=admin_role.id, permission_id=perm2.id
        )
        assign_role_to_user(
            session=db, user_id=test_user.id, role_id=admin_role.id
        )

        permissions = get_user_permissions(session=db, user_id=test_user.id)
        perm_names = [p.name for p in permissions]
        assert name1 in perm_names
        assert name2 in perm_names

    def test_user_has_permission(
        self, db: Session, test_user, admin_role, create_permission_fixture
    ):
        """Test checking if user has specific permission."""
        perm_name = f"users:manage_{random_lower_string()}"
        perm = create_permission_fixture(name=perm_name, resource="users")

        add_permission_to_role(
            session=db, role_id=admin_role.id, permission_id=perm.id
        )
        assign_role_to_user(
            session=db, user_id=test_user.id, role_id=admin_role.id
        )

        has_perm = user_has_permission(
            session=db, user_id=test_user.id, permission_name=perm_name
        )
        assert has_perm is True

        no_perm = user_has_permission(
            session=db, user_id=test_user.id, permission_name=f"nonexistent_{random_lower_string()}"
        )
        assert no_perm is False

    def test_user_permissions_with_multiple_roles(
        self,
        db: Session,
        test_user,
        admin_role,
        editor_role,
        create_permission_fixture,
    ):
        """Test user permissions with multiple roles."""
        suffix = random_lower_string()
        admin_perm_name = f"admin:manage_{suffix}"
        editor_perm_name = f"editor:edit_{suffix}"
        admin_perm = create_permission_fixture(name=admin_perm_name, resource="admin")
        editor_perm = create_permission_fixture(name=editor_perm_name, resource="editor")

        add_permission_to_role(
            session=db, role_id=admin_role.id, permission_id=admin_perm.id
        )
        add_permission_to_role(
            session=db,
            role_id=editor_role.id,
            permission_id=editor_perm.id,
        )

        assign_role_to_user(
            session=db, user_id=test_user.id, role_id=admin_role.id
        )
        assign_role_to_user(
            session=db, user_id=test_user.id, role_id=editor_role.id
        )

        permissions = get_user_permissions(session=db, user_id=test_user.id)
        perm_names = [p.name for p in permissions]
        assert admin_perm_name in perm_names
        assert editor_perm_name in perm_names
