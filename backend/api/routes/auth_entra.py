from datetime import timedelta
from typing import Any

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from sqlmodel import func, select

from backend.api.deps import CurrentUser, SessionDep
from backend.core import security
from backend.core.auth_entra import EntraAuthClient
from backend.core.config import settings
from backend.models import (
    Message,
    MicrosoftTenant,
    MicrosoftTenantCreate,
    MicrosoftTenantPublic,
    MicrosoftTenantsPublic,
    MicrosoftTenantUpdate,
    Token,
    User,
    UserTenantRole,
)

router = APIRouter(prefix="/auth/entra", tags=["auth-entra"])


class EntraLoginRequest(BaseModel):
    access_token: str
    tenant_id: str | None = None
    roles: list[str] = []  # Roles from ID token claims (configured in Azure app)


class EntraLoginUrlResponse(BaseModel):
    login_url: str


@router.post("/login", response_model=Token)
def entra_login(
    request: EntraLoginRequest,
    session: SessionDep,
) -> Any:
    """
    Authenticate via Microsoft Entra.

    Accepts a Microsoft access token (obtained via MSAL on the frontend),
    fetches user info from Microsoft Graph, and returns an application JWT.
    """
    if not settings.azure_enabled:
        raise HTTPException(
            status_code=400, detail="Microsoft Entra authentication is not configured"
        )

    entra_client = EntraAuthClient()

    try:
        # Get user info from Microsoft Graph using the access token
        user_info = entra_client.get_user_info(request.access_token)
        # Use roles from ID token claims (sent by frontend)
        user_roles = request.roles or []
    except Exception:
        raise HTTPException(
            status_code=400, detail="Failed to validate Microsoft token"
        )

    email: str | None = user_info.get("userPrincipalName") or user_info.get("mail")
    if not email:
        raise HTTPException(
            status_code=400, detail="Could not retrieve email from Microsoft account"
        )

    azure_user_id: str = user_info.get("id", "")
    azure_tenant_id: str = user_info.get(
        "tid", request.tenant_id or settings.AZURE_TENANT_ID
    )

    # For multi-tenant: verify the tenant is allowed
    if settings.AZURE_IS_MULTI_TENANT and azure_tenant_id:
        allowed_tenant = session.exec(
            select(MicrosoftTenant).where(
                MicrosoftTenant.tenant_id == azure_tenant_id,
                MicrosoftTenant.is_enabled == True,  # noqa: E712
            )
        ).first()
        if not allowed_tenant:
            raise HTTPException(
                status_code=403, detail="Your organization is not authorized"
            )

    # Find or create user
    db_user = session.exec(select(User).where(User.email == email)).first()

    # Check if user has superuser role (configurable via AZURE_SUPERUSER_ROLE)
    is_admin = settings.AZURE_SUPERUSER_ROLE in user_roles

    if not db_user:
        db_user = User(
            email=email,
            full_name=user_info.get("displayName"),
            azure_user_id=azure_user_id,
            azure_tenant_id=azure_tenant_id,
            azure_roles=user_roles,
            is_active=True,
            is_superuser=is_admin,
        )
        session.add(db_user)
    else:
        # Sync user info from Microsoft on each login
        db_user.full_name = user_info.get("displayName") or db_user.full_name
        db_user.azure_user_id = azure_user_id
        db_user.azure_tenant_id = azure_tenant_id
        db_user.azure_roles = user_roles
        db_user.is_superuser = is_admin
        session.add(db_user)

    session.commit()
    session.refresh(db_user)

    # Sync tenant roles if multi-tenant
    if settings.AZURE_IS_MULTI_TENANT and azure_tenant_id:
        ms_tenant = session.exec(
            select(MicrosoftTenant).where(
                MicrosoftTenant.tenant_id == azure_tenant_id,
            )
        ).first()
        if ms_tenant:
            tenant_role = session.exec(
                select(UserTenantRole).where(
                    UserTenantRole.user_id == db_user.id,
                    UserTenantRole.tenant_id == ms_tenant.id,
                )
            ).first()
            if tenant_role:
                tenant_role.roles = user_roles
                session.add(tenant_role)
            else:
                tenant_role = UserTenantRole(
                    user_id=db_user.id,
                    tenant_id=ms_tenant.id,
                    roles=user_roles,
                )
                session.add(tenant_role)
            session.commit()

    if not db_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")

    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    return Token(
        access_token=security.create_access_token(
            db_user.id, expires_delta=access_token_expires
        )
    )


@router.get("/login-url", response_model=EntraLoginUrlResponse)
def get_entra_login_url(
    redirect_uri: str,
    tenant_id: str | None = None,
) -> Any:
    """Get Microsoft login URL for frontend redirect."""
    if not settings.azure_enabled:
        raise HTTPException(
            status_code=400, detail="Microsoft Entra authentication is not configured"
        )

    entra_client = EntraAuthClient()
    login_url = entra_client.get_login_url(redirect_uri, tenant_id)
    return EntraLoginUrlResponse(login_url=login_url)


@router.get("/config")
def get_entra_config() -> dict[str, Any]:
    """Return Entra configuration for the frontend (public info only)."""
    return {
        "enabled": settings.azure_enabled,
        "client_id": settings.AZURE_CLIENT_ID if settings.azure_enabled else None,
        "tenant_id": settings.AZURE_TENANT_ID if settings.azure_enabled else None,
        "is_multi_tenant": settings.AZURE_IS_MULTI_TENANT,
        "authority": (
            f"{settings.AZURE_AUTHORITY}/organizations"
            if settings.AZURE_IS_MULTI_TENANT
            else f"{settings.AZURE_AUTHORITY}/{settings.AZURE_TENANT_ID}"
        )
        if settings.azure_enabled
        else None,
    }


# --- Tenant Management (admin only, for multi-tenant) ---

tenant_router = APIRouter(prefix="/tenants", tags=["tenants"])


@tenant_router.get("/", response_model=MicrosoftTenantsPublic)
def list_tenants(
    session: SessionDep,
    current_user: CurrentUser,
    skip: int = 0,
    limit: int = 100,
) -> Any:
    """List all configured Microsoft tenants. Requires superuser."""
    if not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Not enough privileges")
    count_stmt = select(MicrosoftTenant)
    tenants = session.exec(count_stmt.offset(skip).limit(limit)).all()
    count = session.exec(select(func.count()).select_from(MicrosoftTenant)).one()
    return MicrosoftTenantsPublic(data=[MicrosoftTenantPublic.model_validate(t) for t in tenants], count=count)


@tenant_router.post("/", response_model=MicrosoftTenantPublic)
def create_tenant(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    tenant_in: MicrosoftTenantCreate,
) -> Any:
    """Add a new Microsoft tenant. Requires superuser."""
    if not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Not enough privileges")

    existing = session.exec(
        select(MicrosoftTenant).where(
            MicrosoftTenant.tenant_id == tenant_in.tenant_id
        )
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="Tenant already exists")

    db_tenant = MicrosoftTenant.model_validate(
        tenant_in, update={"created_by": current_user.id}
    )
    session.add(db_tenant)
    session.commit()
    session.refresh(db_tenant)
    return db_tenant


@tenant_router.patch("/{tenant_id}", response_model=MicrosoftTenantPublic)
def update_tenant(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    tenant_id: str,
    tenant_in: MicrosoftTenantUpdate,
) -> Any:
    """Update a Microsoft tenant. Requires superuser."""
    if not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Not enough privileges")

    db_tenant = session.exec(
        select(MicrosoftTenant).where(MicrosoftTenant.tenant_id == tenant_id)
    ).first()
    if not db_tenant:
        raise HTTPException(status_code=404, detail="Tenant not found")

    tenant_data = tenant_in.model_dump(exclude_unset=True)
    db_tenant.sqlmodel_update(tenant_data)
    session.add(db_tenant)
    session.commit()
    session.refresh(db_tenant)
    return db_tenant


@tenant_router.delete("/{tenant_id}", response_model=Message)
def delete_tenant(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    tenant_id: str,
) -> Any:
    """Delete a Microsoft tenant. Requires superuser."""
    if not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Not enough privileges")

    db_tenant = session.exec(
        select(MicrosoftTenant).where(MicrosoftTenant.tenant_id == tenant_id)
    ).first()
    if not db_tenant:
        raise HTTPException(status_code=404, detail="Tenant not found")

    session.delete(db_tenant)
    session.commit()
    return Message(message="Tenant deleted successfully")
