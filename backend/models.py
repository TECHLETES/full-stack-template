import uuid
from datetime import datetime, timezone

from pydantic import EmailStr
from sqlalchemy import Column, DateTime
from sqlalchemy.types import JSON
from sqlmodel import Field, Relationship, SQLModel


def get_datetime_utc() -> datetime:
    return datetime.now(timezone.utc)


# Shared properties
class UserBase(SQLModel):
    email: EmailStr = Field(unique=True, index=True, max_length=255)
    is_active: bool = True
    is_superuser: bool = False
    full_name: str | None = Field(default=None, max_length=255)


# Properties to receive via API on creation
class UserCreate(UserBase):
    password: str = Field(min_length=8, max_length=128)


class UserRegister(SQLModel):
    email: EmailStr = Field(max_length=255)
    password: str = Field(min_length=8, max_length=128)
    full_name: str | None = Field(default=None, max_length=255)


# Properties to receive via API on update, all are optional
class UserUpdate(UserBase):
    email: EmailStr | None = Field(default=None, max_length=255)  # type: ignore
    password: str | None = Field(default=None, min_length=8, max_length=128)


class UserUpdateMe(SQLModel):
    full_name: str | None = Field(default=None, max_length=255)
    email: EmailStr | None = Field(default=None, max_length=255)


class UpdatePassword(SQLModel):
    current_password: str = Field(min_length=8, max_length=128)
    new_password: str = Field(min_length=8, max_length=128)


# Database model, database table inferred from class name
class User(UserBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    hashed_password: str = Field(default="")
    created_at: datetime | None = Field(
        default_factory=get_datetime_utc,
        sa_type=DateTime(timezone=True),  # type: ignore
    )
    # Microsoft Entra fields
    azure_user_id: str | None = Field(default=None, index=True)
    azure_tenant_id: str | None = Field(default=None)
    azure_roles: list[str] = Field(default_factory=list, sa_column=Column(JSON))

    items: list["Item"] = Relationship(back_populates="owner", cascade_delete=True)
    tenant_roles: list["UserTenantRole"] = Relationship(
        back_populates="user", cascade_delete=True
    )
    roles: list["Role"] = Relationship(
        back_populates="users",
        link_model="UserRole",
        cascade_delete=True,
    )


# Properties to return via API, id is always required
class UserPublic(UserBase):
    id: uuid.UUID
    created_at: datetime | None = None
    azure_user_id: str | None = None
    azure_tenant_id: str | None = None
    azure_roles: list[str] = []


class UsersPublic(SQLModel):
    data: list[UserPublic]
    count: int


# --- Microsoft Tenant Models ---


class MicrosoftTenantBase(SQLModel):
    tenant_id: str = Field(unique=True, index=True, max_length=255)
    tenant_name: str = Field(max_length=255)
    is_enabled: bool = True
    auto_create_users: bool = True


class MicrosoftTenantCreate(MicrosoftTenantBase):
    pass


class MicrosoftTenantUpdate(SQLModel):
    tenant_name: str | None = Field(default=None, max_length=255)
    is_enabled: bool | None = None
    auto_create_users: bool | None = None


class MicrosoftTenant(MicrosoftTenantBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    created_at: datetime | None = Field(
        default_factory=get_datetime_utc,
        sa_type=DateTime(timezone=True),  # type: ignore
    )
    created_by: uuid.UUID | None = Field(
        default=None, foreign_key="user.id", ondelete="SET NULL"
    )
    tenant_roles: list["UserTenantRole"] = Relationship(
        back_populates="tenant", cascade_delete=True
    )


class MicrosoftTenantPublic(MicrosoftTenantBase):
    id: uuid.UUID
    created_at: datetime | None = None
    created_by: uuid.UUID | None = None


class MicrosoftTenantsPublic(SQLModel):
    data: list[MicrosoftTenantPublic]
    count: int


# --- RBAC Models (Roles and Permissions) ---


class PermissionBase(SQLModel):
    name: str = Field(unique=True, index=True, max_length=255)
    description: str | None = Field(default=None, max_length=500)
    resource: str = Field(max_length=255)  # e.g., "items", "users", "reports"


class PermissionCreate(PermissionBase):
    pass


class PermissionUpdate(SQLModel):
    name: str | None = Field(default=None, max_length=255)  # type: ignore
    description: str | None = Field(default=None, max_length=500)
    resource: str | None = Field(default=None, max_length=255)  # type: ignore


class Permission(PermissionBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    created_at: datetime | None = Field(
        default_factory=get_datetime_utc,
        sa_type=DateTime(timezone=True),  # type: ignore
    )
    roles: list["Role"] = Relationship(
        back_populates="permissions",
        link_model="RolePermission",
    )


class PermissionPublic(PermissionBase):
    id: uuid.UUID
    created_at: datetime | None = None


class PermissionsPublic(SQLModel):
    data: list[PermissionPublic]
    count: int


class RoleBase(SQLModel):
    name: str = Field(unique=True, index=True, max_length=255)
    description: str | None = Field(default=None, max_length=500)
    is_system: bool = False  # True for default roles synced from config


class RoleCreate(RoleBase):
    permission_ids: list[uuid.UUID] = Field(default_factory=list)


class RoleUpdate(SQLModel):
    name: str | None = Field(default=None, max_length=255)  # type: ignore
    description: str | None = Field(default=None, max_length=500)
    permission_ids: list[uuid.UUID] | None = None


class Role(RoleBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    created_at: datetime | None = Field(
        default_factory=get_datetime_utc,
        sa_type=DateTime(timezone=True),  # type: ignore
    )
    permissions: list["Permission"] = Relationship(
        back_populates="roles",
        link_model="RolePermission",
    )
    users: list["User"] = Relationship(
        back_populates="roles",
        link_model="UserRole",
    )


class RolePublic(RoleBase):
    id: uuid.UUID
    created_at: datetime | None = None
    permissions: list[PermissionPublic] = Field(default_factory=list)


class RolesPublic(SQLModel):
    data: list[RolePublic]
    count: int


# Many-to-many: Role ↔ Permission
class RolePermission(SQLModel, table=True):
    role_id: uuid.UUID = Field(
        foreign_key="role.id", primary_key=True, ondelete="CASCADE"
    )
    permission_id: uuid.UUID = Field(
        foreign_key="permission.id", primary_key=True, ondelete="CASCADE"
    )


# Many-to-many: User ↔ Role
class UserRole(SQLModel, table=True):
    user_id: uuid.UUID = Field(
        foreign_key="user.id", primary_key=True, ondelete="CASCADE"
    )
    role_id: uuid.UUID = Field(
        foreign_key="role.id", primary_key=True, ondelete="CASCADE"
    )


# --- User-Tenant Role Mapping ---


class UserTenantRoleBase(SQLModel):
    roles: list[str] = Field(default_factory=list, sa_column=Column(JSON))


class UserTenantRole(UserTenantRoleBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    user_id: uuid.UUID = Field(foreign_key="user.id", ondelete="CASCADE")
    tenant_id: uuid.UUID = Field(
        foreign_key="microsofttenant.id", ondelete="CASCADE"
    )
    created_at: datetime | None = Field(
        default_factory=get_datetime_utc,
        sa_type=DateTime(timezone=True),  # type: ignore
    )
    user: User | None = Relationship(back_populates="tenant_roles")
    tenant: MicrosoftTenant | None = Relationship(back_populates="tenant_roles")


class UserTenantRolePublic(SQLModel):
    id: uuid.UUID
    user_id: uuid.UUID
    tenant_id: uuid.UUID
    roles: list[str] = []
    created_at: datetime | None = None


# Shared properties
class ItemBase(SQLModel):
    title: str = Field(min_length=1, max_length=255)
    description: str | None = Field(default=None, max_length=255)


# Properties to receive on item creation
class ItemCreate(ItemBase):
    pass


# Properties to receive on item update
class ItemUpdate(ItemBase):
    title: str | None = Field(default=None, min_length=1, max_length=255)  # type: ignore


# Database model, database table inferred from class name
class Item(ItemBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    created_at: datetime | None = Field(
        default_factory=get_datetime_utc,
        sa_type=DateTime(timezone=True),  # type: ignore
    )
    owner_id: uuid.UUID = Field(
        foreign_key="user.id", nullable=False, ondelete="CASCADE"
    )
    owner: User | None = Relationship(back_populates="items")


# Properties to return via API, id is always required
class ItemPublic(ItemBase):
    id: uuid.UUID
    owner_id: uuid.UUID
    created_at: datetime | None = None


class ItemsPublic(SQLModel):
    data: list[ItemPublic]
    count: int


# Generic message
class Message(SQLModel):
    message: str


# JSON payload containing access token
class Token(SQLModel):
    access_token: str
    token_type: str = "bearer"


# Contents of JWT token
class TokenPayload(SQLModel):
    sub: str | None = None


class NewPassword(SQLModel):
    token: str
    new_password: str = Field(min_length=8, max_length=128)
