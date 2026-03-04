from sqlalchemy.engine import Engine
from sqlmodel import Session, create_engine, select

from backend import crud
from backend.core.config import settings
from backend.core.rbac import DEFAULT_PERMISSIONS, DEFAULT_SYSTEM_ROLES
from backend.models import User, UserCreate

engine = create_engine(str(settings.SQLALCHEMY_DATABASE_URI))


def get_engine() -> Engine:
    """Get the database engine. Can be overridden in tests."""
    return engine


# make sure all SQLModel models are imported (backend.models) before initializing DB
# otherwise, SQLModel might fail to initialize relationships properly
# for more details: https://github.com/fastapi/full-stack-fastapi-template/issues/28


def init_db(session: Session) -> None:
    # Tables should be created with Alembic migrations
    # But if you don't want to use migrations, create
    # the tables un-commenting the next lines
    # from sqlmodel import SQLModel

    # This works because the models are already imported and registered from backend.models
    # SQLModel.metadata.create_all(engine)

    user: User | None = session.exec(
        select(User).where(User.email == settings.FIRST_SUPERUSER)
    ).first()
    if user is None:
        user_in = UserCreate(
            email=settings.FIRST_SUPERUSER,
            password=settings.FIRST_SUPERUSER_PASSWORD,
            is_superuser=True,
        )
        user = crud.create_user(session=session, user_create=user_in)

    _seed_rbac(session)


def _seed_rbac(session: Session) -> None:
    """Seed default permissions and system roles if they don't exist."""
    from backend.crud_rbac import (
        add_permission_to_role,
        create_permission,
        create_role,
        get_permission_by_name,
        get_role_by_name,
    )
    from backend.models import PermissionCreate, RoleCreate

    # Create default permissions
    for _resource, perms in DEFAULT_PERMISSIONS.items():
        for perm_def in perms:
            existing = get_permission_by_name(session=session, name=perm_def["name"])
            if not existing:
                create_permission(
                    session=session,
                    permission_in=PermissionCreate(
                        name=perm_def["name"],
                        resource=perm_def["resource"],
                        description=perm_def.get("display", ""),
                    ),
                )

    # Create default system roles with their permissions
    for role_name, role_def in DEFAULT_SYSTEM_ROLES.items():
        existing_role = get_role_by_name(session=session, name=role_name)
        if not existing_role:
            role = create_role(
                session=session,
                role_in=RoleCreate(
                    name=role_name,
                    description=role_def["description"],
                    permission_ids=[],
                ),
                is_system=True,
            )
            for perm_name in role_def["permissions"]:
                perm = get_permission_by_name(session=session, name=perm_name)
                if perm:
                    add_permission_to_role(
                        session=session, role_id=role.id, permission_id=perm.id
                    )
