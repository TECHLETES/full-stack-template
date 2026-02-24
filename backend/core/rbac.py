"""RBAC configuration - Default roles and permissions."""

from typing import TypedDict


class RoleDefinition(TypedDict):
    """Type definition for a system role."""

    display_name: str
    description: str
    permissions: list[str]


class PermissionDefinition(TypedDict):
    """Type definition for a permission."""

    name: str
    display: str
    resource: str


# Default permissions catalog for the application
DEFAULT_PERMISSIONS: dict[str, list[PermissionDefinition]] = {
    "items": [
        {"name": "items:create", "display": "Create Items", "resource": "items"},
        {"name": "items:read", "display": "Read Items", "resource": "items"},
        {"name": "items:update", "display": "Update Items", "resource": "items"},
        {"name": "items:delete", "display": "Delete Items", "resource": "items"},
        {"name": "items:export", "display": "Export Items", "resource": "items"},
    ],
    "users": [
        {"name": "users:create", "display": "Create Users", "resource": "users"},
        {"name": "users:read", "display": "Read Users", "resource": "users"},
        {"name": "users:update", "display": "Update Users", "resource": "users"},
        {"name": "users:delete", "display": "Delete Users", "resource": "users"},
        {
            "name": "users:manage_roles",
            "display": "Manage User Roles",
            "resource": "users",
        },
    ],
    "reports": [
        {"name": "reports:view", "display": "View Reports", "resource": "reports"},
        {
            "name": "reports:download",
            "display": "Download Reports",
            "resource": "reports",
        },
        {"name": "reports:share", "display": "Share Reports", "resource": "reports"},
    ],
}

# Default system roles - these are synced to Entra
DEFAULT_SYSTEM_ROLES: dict[str, RoleDefinition] = {
    "Admin": {
        "display_name": "Admin",
        "description": "Full access to all features",
        "permissions": [
            "items:create",
            "items:read",
            "items:update",
            "items:delete",
            "items:export",
            "users:create",
            "users:read",
            "users:update",
            "users:delete",
            "users:manage_roles",
            "reports:view",
            "reports:download",
            "reports:share",
        ],
    },
    "Editor": {
        "display_name": "Editor",
        "description": "Can create and edit content",
        "permissions": [
            "items:create",
            "items:read",
            "items:update",
            "users:read",
            "reports:view",
            "reports:download",
        ],
    },
    "Viewer": {
        "display_name": "Viewer",
        "description": "Read-only access",
        "permissions": [
            "items:read",
            "users:read",
            "reports:view",
        ],
    },
}
