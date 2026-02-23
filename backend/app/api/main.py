from fastapi import APIRouter

from app.api.routes import auth_entra, items, login, private, users, utils
from app.core.config import settings

api_router = APIRouter()
api_router.include_router(login.router)
api_router.include_router(users.router)
api_router.include_router(utils.router)
api_router.include_router(items.router)
api_router.include_router(auth_entra.router)
api_router.include_router(auth_entra.tenant_router)


if settings.ENVIRONMENT == "local":
    api_router.include_router(private.router)
