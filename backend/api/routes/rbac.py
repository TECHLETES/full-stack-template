"""RBAC endpoints for managing roles and permissions."""

import uuid
from typing import cast

from fastapi import APIRouter, Depends, HTTPException, Query

from backend.api.deps import SessionDep
from backend.api.deps_rbac import require_role
from backend.core.rbac import DEFAULT_PERMISSIONS, PermissionDefinition
from backend.crud_rbac import (
    add_permission_to_role,
    assign_role_to_user,
    create_permission,
    create_role,
    delete_permission,
    delete_role,
    get_all_permissions,
    get_all_roles,
    get_permission,
    get_role,
    get_user_permissions,
    get_user_roles,
    remove_permission_from_role,
    remove_role_from_user,
    update_permission,
    update_role,
)
from backend.models import (
    PermissionCreate,
    PermissionPublic,
    PermissionsPublic,
    PermissionUpdate,
    RoleCreate,
    RolePublic,
    RolesPublic,
    RoleUpdate,
)

router = APIRouter(prefix="/rbac", tags=["rbac"])


# --- Permissions Endpoints ---


@router.get("/permissions", response_model=PermissionsPublic)
def list_permissions(
    *,
    session: SessionDep,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
) -> PermissionsPublic:
    """List all permissions with pagination."""
    permissions, count = get_all_permissions(session=session, skip=skip, limit=limit)
    return PermissionsPublic(
        data=[PermissionPublic.model_validate(p) for p in permissions], count=count
    )


@router.get("/permissions/{permission_id}", response_model=PermissionPublic)
def get_permission_endpoint(
    *, session: SessionDep, permission_id: uuid.UUID
) -> PermissionPublic:
    """Get permission by ID."""
    permission = get_permission(session=session, permission_id=permission_id)
    if not permission:
        raise HTTPException(status_code=404, detail="Permission not found")
    return cast(PermissionPublic, PermissionPublic.model_validate(permission))


@router.post(
    "/permissions",
    response_model=PermissionPublic,
    dependencies=[Depends(require_role("Admin"))],
)
def create_permission_endpoint(
    *, session: SessionDep, permission_in: PermissionCreate
) -> PermissionPublic:
    """Create a new permission (Admin only)."""
    permission = create_permission(session=session, permission_in=permission_in)
    return cast(PermissionPublic, PermissionPublic.model_validate(permission))


@router.patch(
    "/permissions/{permission_id}",
    response_model=PermissionPublic,
    dependencies=[Depends(require_role("Admin"))],
)
def update_permission_endpoint(
    *,
    session: SessionDep,
    permission_id: uuid.UUID,
    permission_in: PermissionUpdate,
) -> PermissionPublic:
    """Update a permission (Admin only)."""
    permission = get_permission(session=session, permission_id=permission_id)
    if not permission:
        raise HTTPException(status_code=404, detail="Permission not found")
    updated = update_permission(
        session=session, db_permission=permission, permission_in=permission_in
    )
    return cast(PermissionPublic, PermissionPublic.model_validate(updated))


@router.delete(
    "/permissions/{permission_id}",
    dependencies=[Depends(require_role("Admin"))],
)
def delete_permission_endpoint(
    *, session: SessionDep, permission_id: uuid.UUID
) -> dict[str, str]:
    """Delete a permission (Admin only)."""
    if not delete_permission(session=session, permission_id=permission_id):
        raise HTTPException(status_code=404, detail="Permission not found")
    return {"message": "Permission deleted"}


# --- Roles Endpoints ---


@router.get("/roles", response_model=RolesPublic)
def list_roles(
    *,
    session: SessionDep,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
) -> RolesPublic:
    """List all roles with pagination."""
    roles, count = get_all_roles(session=session, skip=skip, limit=limit)
    return RolesPublic(
        data=[RolePublic.model_validate(r, from_attributes=True) for r in roles],
        count=count,
    )


@router.get("/roles/{role_id}", response_model=RolePublic)
def get_role_endpoint(*, session: SessionDep, role_id: uuid.UUID) -> RolePublic:
    """Get role by ID."""
    role = get_role(session=session, role_id=role_id)
    if not role:
        raise HTTPException(status_code=404, detail="Role not found")
    return cast(RolePublic, RolePublic.model_validate(role, from_attributes=True))


@router.post(
    "/roles",
    response_model=RolePublic,
    dependencies=[Depends(require_role("Admin"))],
)
def create_role_endpoint(*, session: SessionDep, role_in: RoleCreate) -> RolePublic:
    """Create a new role (Admin only)."""
    role = create_role(session=session, role_in=role_in)
    return cast(RolePublic, RolePublic.model_validate(role, from_attributes=True))


@router.patch(
    "/roles/{role_id}",
    response_model=RolePublic,
    dependencies=[Depends(require_role("Admin"))],
)
def update_role_endpoint(
    *,
    session: SessionDep,
    role_id: uuid.UUID,
    role_in: RoleUpdate,
) -> RolePublic:
    """Update a role (Admin only)."""
    role = get_role(session=session, role_id=role_id)
    if not role:
        raise HTTPException(status_code=404, detail="Role not found")
    updated = update_role(session=session, db_role=role, role_in=role_in)
    return cast(RolePublic, RolePublic.model_validate(updated, from_attributes=True))


@router.delete(
    "/roles/{role_id}",
    dependencies=[Depends(require_role("Admin"))],
)
def delete_role_endpoint(*, session: SessionDep, role_id: uuid.UUID) -> dict[str, str]:
    """Delete a role (Admin only)."""
    if not delete_role(session=session, role_id=role_id):
        raise HTTPException(
            status_code=404, detail="Role not found or cannot delete system role"
        )
    return {"message": "Role deleted"}


# --- Role-Permission Mapping ---


@router.post(
    "/roles/{role_id}/permissions/{permission_id}",
    dependencies=[Depends(require_role("Admin"))],
)
def add_permission_to_role_endpoint(
    *,
    session: SessionDep,
    role_id: uuid.UUID,
    permission_id: uuid.UUID,
) -> dict[str, str]:
    """Add permission to role (Admin only)."""
    if not add_permission_to_role(
        session=session, role_id=role_id, permission_id=permission_id
    ):
        raise HTTPException(status_code=404, detail="Role or permission not found")
    return {"message": "Permission added to role"}


@router.delete(
    "/roles/{role_id}/permissions/{permission_id}",
    dependencies=[Depends(require_role("Admin"))],
)
def remove_permission_from_role_endpoint(
    *,
    session: SessionDep,
    role_id: uuid.UUID,
    permission_id: uuid.UUID,
) -> dict[str, str]:
    """Remove permission from role (Admin only)."""
    if not remove_permission_from_role(
        session=session, role_id=role_id, permission_id=permission_id
    ):
        raise HTTPException(status_code=404, detail="Mapping not found")
    return {"message": "Permission removed from role"}


# --- User-Role Mapping ---


@router.post(
    "/users/{user_id}/roles/{role_id}",
    dependencies=[Depends(require_role("Admin"))],
)
def assign_role_to_user_endpoint(
    *,
    session: SessionDep,
    user_id: uuid.UUID,
    role_id: uuid.UUID,
) -> dict[str, str]:
    """Assign role to user (Admin only)."""
    if not assign_role_to_user(session=session, user_id=user_id, role_id=role_id):
        raise HTTPException(status_code=404, detail="User or role not found")
    return {"message": "Role assigned to user"}


@router.delete(
    "/users/{user_id}/roles/{role_id}",
    dependencies=[Depends(require_role("Admin"))],
)
def remove_role_from_user_endpoint(
    *,
    session: SessionDep,
    user_id: uuid.UUID,
    role_id: uuid.UUID,
) -> dict[str, str]:
    """Remove role from user (Admin only)."""
    if not remove_role_from_user(session=session, user_id=user_id, role_id=role_id):
        raise HTTPException(status_code=404, detail="Assignment not found")
    return {"message": "Role removed from user"}


@router.get("/users/{user_id}/roles", response_model=RolesPublic)
def get_user_roles_endpoint(*, session: SessionDep, user_id: uuid.UUID) -> RolesPublic:
    """Get all roles for a user."""
    roles = get_user_roles(session=session, user_id=user_id)
    return RolesPublic(
        data=[RolePublic.model_validate(r, from_attributes=True) for r in roles],
        count=len(roles),
    )


@router.get("/users/{user_id}/permissions", response_model=PermissionsPublic)
def get_user_permissions_endpoint(
    *, session: SessionDep, user_id: uuid.UUID
) -> PermissionsPublic:
    """Get all permissions for a user (via their roles)."""
    permissions = get_user_permissions(session=session, user_id=user_id)
    return PermissionsPublic(
        data=[PermissionPublic.model_validate(p) for p in permissions],
        count=len(permissions),
    )


# --- Permissions Catalog ---


@router.get("/permissions-catalog")
def get_permissions_catalog() -> dict[str, list[PermissionDefinition]]:
    """
    Get the catalog of available permissions in the application.

    This endpoint returns the predefined permissions that can be assigned to roles.
    Useful for UI to display what permissions are available.
    """
    return DEFAULT_PERMISSIONS
