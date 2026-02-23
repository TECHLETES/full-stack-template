import logging
import uuid

from sqlalchemy import Engine
from sqlmodel import Session, select
from tenacity import after_log, before_log, retry, stop_after_attempt, wait_fixed

from backend.core.auth_entra import EntraAuthClient
from backend.core.config import settings
from backend.core.db import engine
from backend.core.rbac import DEFAULT_PERMISSIONS, DEFAULT_SYSTEM_ROLES
from backend.crud_rbac import (
    create_permission,
    create_role,
    get_permission_by_name,
    get_role_by_name,
)
from backend.models import PermissionCreate, RoleCreate

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

max_tries = 60 * 5  # 5 minutes
wait_seconds = 1


@retry(
    stop=stop_after_attempt(max_tries),
    wait=wait_fixed(wait_seconds),
    before=before_log(logger, logging.INFO),
    after=after_log(logger, logging.WARN),
)
def init(db_engine: Engine) -> None:
    try:
        with Session(db_engine) as session:
            # Try to create session to check if DB is awake
            session.exec(select(1))
    except Exception as e:
        logger.error(e)
        raise e


def init_rbac(db_engine: Engine) -> None:
    """Initialize RBAC system with default permissions and roles."""
    try:
        with Session(db_engine) as session:
            # Create default permissions if they don't exist
            logger.info("Initializing RBAC permissions...")
            for permission_group in DEFAULT_PERMISSIONS.values():
                for perm_dict in permission_group:
                    existing = get_permission_by_name(
                        session=session, name=perm_dict["name"]
                    )
                    if not existing:
                        create_permission(
                            session=session,
                            permission_in=PermissionCreate(
                                name=perm_dict["name"],
                                description=perm_dict.get("display", perm_dict["name"]),
                                resource=perm_dict["resource"],
                            ),
                        )
                        logger.info(f"Created permission: {perm_dict['name']}")

            # Create default system roles if they don't exist
            logger.info("Initializing RBAC system roles...")
            entra_roles = []
            for role_name, role_config in DEFAULT_SYSTEM_ROLES.items():
                existing_role = get_role_by_name(session=session, name=role_name)
                if not existing_role:
                    # Get permission IDs
                    permission_ids = []
                    for perm_name in role_config["permissions"]:
                        perm = get_permission_by_name(session=session, name=perm_name)
                        if perm:
                            permission_ids.append(perm.id)

                    role = create_role(
                        session=session,
                        role_in=RoleCreate(
                            name=role_name,
                            description=role_config["description"],
                            permission_ids=permission_ids,
                        ),
                        is_system=True,
                    )
                    logger.info(f"Created system role: {role_name}")
                    entra_roles.append(role)
                else:
                    entra_roles.append(existing_role)

            # Sync roles to Entra if configured
            if settings.AZURE_CLIENT_ID and settings.AZURE_CLIENT_SECRET:
                logger.info("Syncing roles to Microsoft Entra...")
                entra_client = EntraAuthClient()
                roles_payload = [
                    {
                        "id": str(uuid.uuid4()),
                        "displayName": role.name,
                        "description": role.description or f"{role.name} role",
                        "value": role.name,
                    }
                    for role in entra_roles
                ]

                if entra_client.sync_app_roles_to_manifest(roles_payload):
                    logger.info("Successfully synced roles to Entra app manifest")
                else:
                    logger.warning("Failed to sync roles to Entra app manifest")
            else:
                logger.info(
                    "Entra not configured (AZURE_CLIENT_ID not set), skipping role sync"
                )

    except Exception as e:
        logger.error(f"Failed to initialize RBAC: {e}")
        raise e


def main() -> None:
    logger.info("Initializing service")
    init(engine)
    init_rbac(engine)
    logger.info("Service finished initializing")


if __name__ == "__main__":
    main()
