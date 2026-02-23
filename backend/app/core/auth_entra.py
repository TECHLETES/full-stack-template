from urllib.parse import urlencode
from uuid import uuid4

import httpx

from app.core.config import settings


class EntraAuthClient:
    """Handle Microsoft Entra (Azure AD) authentication."""

    def __init__(self) -> None:
        self.authority = settings.AZURE_AUTHORITY
        self.client_id = settings.AZURE_CLIENT_ID
        self.client_secret = settings.AZURE_CLIENT_SECRET
        self.graph_api = "https://graph.microsoft.com/v1.0"

    def _get_tenant_id(self, tenant_id: str | None = None) -> str:
        if tenant_id:
            return tenant_id
        if settings.AZURE_IS_MULTI_TENANT:
            return "organizations"
        return settings.AZURE_TENANT_ID

    def get_token_by_auth_code(
        self,
        auth_code: str,
        redirect_uri: str,
        tenant_id: str | None = None,
    ) -> dict[str, str]:
        """Exchange authorization code for access token."""
        tid = self._get_tenant_id(tenant_id)
        token_url = f"{self.authority}/{tid}/oauth2/v2.0/token"

        payload = {
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "code": auth_code,
            "redirect_uri": redirect_uri,
            "grant_type": "authorization_code",
            "scope": "openid profile email " + settings.AZURE_GRAPH_SCOPE,
        }

        with httpx.Client() as client:
            resp = client.post(token_url, data=payload)
            if resp.status_code == 200:
                return resp.json()  # type: ignore[no-any-return]
            raise Exception(f"Token exchange failed: {resp.text}")

    def get_user_info(self, access_token: str) -> dict[str, str]:
        """Get user info from Microsoft Graph."""
        headers = {"Authorization": f"Bearer {access_token}"}

        with httpx.Client() as client:
            resp = client.get(f"{self.graph_api}/me", headers=headers)
            if resp.status_code == 200:
                return resp.json()  # type: ignore[no-any-return]
            raise Exception(f"Failed to get user info: {resp.status_code}")

    def get_user_roles(self, access_token: str) -> list[str]:
        """Get app roles assigned to user via /me/memberOf."""
        headers = {"Authorization": f"Bearer {access_token}"}

        with httpx.Client() as client:
            resp = client.get(
                f"{self.graph_api}/me/memberOf",
                headers=headers,
                params={"$select": "displayName"},
            )
            if resp.status_code == 200:
                data = resp.json()
                roles: list[str] = []
                for item in data.get("value", []):
                    display_name = item.get("displayName")
                    if display_name:
                        roles.append(display_name)
                return roles
            return []

    def get_login_url(
        self,
        redirect_uri: str,
        tenant_id: str | None = None,
        state: str | None = None,
    ) -> str:
        """Generate Microsoft login URL."""
        tid = self._get_tenant_id(tenant_id)

        params = {
            "client_id": self.client_id,
            "response_type": "code",
            "redirect_uri": redirect_uri,
            "response_mode": "query",
            "scope": "openid profile email " + settings.AZURE_GRAPH_SCOPE,
            "state": state or uuid4().hex,
        }

        query_string = urlencode(params)
        return f"{self.authority}/{tid}/oauth2/v2.0/authorize?{query_string}"
