from fastapi import APIRouter

from backend.api.routes import (
    auth_entra,
    items,
    login,
    notifications,
    private,
    rbac,
    users,
    utils,
)
from backend.core.config import settings

api_router = APIRouter()
api_router.include_router(login.router)
api_router.include_router(users.router)
api_router.include_router(utils.router)
api_router.include_router(items.router)
api_router.include_router(rbac.router)
api_router.include_router(auth_entra.router)
api_router.include_router(auth_entra.tenant_router)
api_router.include_router(notifications.router)


if settings.ENVIRONMENT == "local":
    api_router.include_router(private.router)
