"""Dependencies for RBAC authorization."""

from typing import Annotated

from fastapi import Depends, HTTPException
from sqlmodel import Session

from backend.api.deps import SessionDep
from backend.crud_rbac import user_has_permission, user_has_role
from backend.models import User


async def get_current_user_with_rbac(
    current_user: Annotated[User, Depends(lambda: None)],
) -> User:
    """
    Get current user (assumes get_current_user dependency already exists).
    This is a placeholder that should be integrated with existing auth.
    """
    return current_user


def require_role(role_name: str):
    """
    Dependency to require a specific role.

    Usage:
        @router.get("/admin")
        async def admin_only(
            current_user: Annotated[User, Depends(require_role("Admin"))],
            session: SessionDep,
        ):
            return {"message": "Admin access granted"}
    """

    async def check_role(
        current_user: User, session: SessionDep
    ) -> User:
        if not current_user:
            raise HTTPException(status_code=401, detail="Not authenticated")

        if not user_has_role(
            session=session, user_id=current_user.id, role_name=role_name
        ):
            raise HTTPException(
                status_code=403,
                detail=f"User does not have required role: {role_name}",
            )
        return current_user

    return Depends(check_role)


def require_permission(permission_name: str):
    """
    Dependency to require a specific permission.

    Usage:
        @router.delete("/items/{item_id}")
        async def delete_item(
            current_user: Annotated[User, Depends(require_permission("items:delete"))],
            session: SessionDep,
        ):
            return {"message": "Item deleted"}
    """

    async def check_permission(
        current_user: User, session: SessionDep
    ) -> User:
        if not current_user:
            raise HTTPException(status_code=401, detail="Not authenticated")

        if not user_has_permission(
            session=session,
            user_id=current_user.id,
            permission_name=permission_name,
        ):
            raise HTTPException(
                status_code=403,
                detail=f"User does not have required permission: {permission_name}",
            )
        return current_user

    return Depends(check_permission)


def require_any_role(*role_names: str):
    """
    Dependency to require any of the specified roles.

    Usage:
        @router.get("/reports")
        async def get_reports(
            current_user: Annotated[User, Depends(require_any_role("Admin", "Editor"))],
            session: SessionDep,
        ):
            return {"message": "Reports access"}
    """

    async def check_any_role(
        current_user: User, session: SessionDep
    ) -> User:
        if not current_user:
            raise HTTPException(status_code=401, detail="Not authenticated")

        has_any_role = any(
            user_has_role(session=session, user_id=current_user.id, role_name=role)
            for role in role_names
        )

        if not has_any_role:
            roles_str = ", ".join(role_names)
            raise HTTPException(
                status_code=403,
                detail=f"User does not have any of required roles: {roles_str}",
            )
        return current_user

    return Depends(check_any_role)


def require_all_permissions(*permission_names: str):
    """
    Dependency to require all of the specified permissions.

    Usage:
        @router.post("/projects/{project_id}/users")
        async def add_user_to_project(
            current_user: Annotated[User, Depends(
                require_all_permissions("users:create", "users:manage_roles")
            )],
            session: SessionDep,
        ):
            return {"message": "User added"}
    """

    async def check_all_permissions(
        current_user: User, session: SessionDep
    ) -> User:
        if not current_user:
            raise HTTPException(status_code=401, detail="Not authenticated")

        missing_perms = [
            perm
            for perm in permission_names
            if not user_has_permission(
                session=session, user_id=current_user.id, permission_name=perm
            )
        ]

        if missing_perms:
            perms_str = ", ".join(missing_perms)
            raise HTTPException(
                status_code=403,
                detail=f"User is missing required permissions: {perms_str}",
            )
        return current_user

    return Depends(check_all_permissions)
