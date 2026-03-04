"""Dependencies for RBAC authorization."""

from collections.abc import Callable

from fastapi import HTTPException

from backend.api.deps import CurrentUser, SessionDep
from backend.crud_rbac import user_has_permission, user_has_role
from backend.models import User


def require_role(role_name: str) -> Callable[..., User]:
    """
    Dependency factory to require a specific RBAC role.

    Usage:
        @router.get("/admin", dependencies=[Depends(require_role("Admin"))])
        async def admin_only(): ...

        # Or as a typed parameter:
        async def admin_only(current_user: Annotated[User, Depends(require_role("Admin"))]):
    """

    def check_role(current_user: CurrentUser, session: SessionDep) -> User:
        if not user_has_role(
            session=session, user_id=current_user.id, role_name=role_name
        ):
            raise HTTPException(
                status_code=403,
                detail=f"User does not have required role: {role_name}",
            )
        return current_user

    return check_role


def require_permission(
    permission_name: str,
) -> Callable[[CurrentUser, SessionDep], User]:
    """
    Dependency factory to require a specific permission.

    Usage:
        @router.delete("/items/{item_id}", dependencies=[Depends(require_permission("items:delete"))])
        async def delete_item(): ...
    """

    def check_permission(current_user: CurrentUser, session: SessionDep) -> User:
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

    return check_permission


def require_any_role(*role_names: str) -> Callable[[CurrentUser, SessionDep], User]:
    """
    Dependency factory to require any of the specified roles.

    Usage:
        @router.get("/reports", dependencies=[Depends(require_any_role("Admin", "Editor"))])
        async def get_reports(): ...
    """

    def check_any_role(current_user: CurrentUser, session: SessionDep) -> User:
        has_any = any(
            user_has_role(session=session, user_id=current_user.id, role_name=role)
            for role in role_names
        )
        if not has_any:
            raise HTTPException(
                status_code=403,
                detail=f"User does not have any of required roles: {', '.join(role_names)}",
            )
        return current_user

    return check_any_role


def require_all_permissions(
    *permission_names: str,
) -> Callable[[CurrentUser, SessionDep], User]:
    """
    Dependency factory to require all of the specified permissions.

    Usage:
        @router.post("/endpoint", dependencies=[Depends(require_all_permissions("users:create", "users:manage_roles"))])
        async def endpoint(): ...
    """

    def check_all_permissions(current_user: CurrentUser, session: SessionDep) -> User:
        missing = [
            perm
            for perm in permission_names
            if not user_has_permission(
                session=session, user_id=current_user.id, permission_name=perm
            )
        ]
        if missing:
            raise HTTPException(
                status_code=403,
                detail=f"User is missing required permissions: {', '.join(missing)}",
            )
        return current_user

    return check_all_permissions
