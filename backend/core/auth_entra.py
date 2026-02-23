from urllib.parse import urlencode
from uuid import uuid4

import httpx

from backend.core.config import settings


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

    def _get_service_principal_token(self) -> str:
        """Get service principal token for Graph API calls."""
        token_url = f"{self.authority}/{settings.AZURE_TENANT_ID}/oauth2/v2.0/token"

        payload = {
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "grant_type": "client_credentials",
            "scope": "https://graph.microsoft.com/.default",
        }

        with httpx.Client() as client:
            resp = client.post(token_url, data=payload)
            if resp.status_code == 200:
                token_response = resp.json()
                return token_response["access_token"]  # type: ignore[return-value]
            raise Exception(f"Failed to get service principal token: {resp.text}")

    def sync_app_roles_to_manifest(self, roles: list[dict[str, str]]) -> bool:
        """
        Sync application roles to Entra app manifest.

        Args:
            roles: List of role dicts with format:
                {"id": "uuid", "displayName": "Admin", "value": "Admin"}

        Returns:
            True if successful, False otherwise
        """
        if not self.client_id or not self.client_secret:
            return False

        try:
            token = self._get_service_principal_token()
            headers = {
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json",
            }

            # Get current app
            with httpx.Client() as client:
                app_resp = client.get(
                    f"{self.graph_api}/applications?$filter=appId eq '{self.client_id}'",
                    headers=headers,
                )
                if app_resp.status_code != 200:
                    return False

                apps = app_resp.json().get("value", [])
                if not apps:
                    return False

                app_id = apps[0]["id"]

                # Prepare app roles payload
                payload = {
                    "appRoles": [
                        {
                            "id": role["id"],
                            "allowedMemberTypes": ["User"],
                            "description": role.get("description", role["displayName"]),
                            "displayName": role["displayName"],
                            "isEnabled": True,
                            "value": role["value"],
                        }
                        for role in roles
                    ]
                }

                # Update app manifest
                update_resp = client.patch(
                    f"{self.graph_api}/applications/{app_id}",
                    json=payload,
                    headers=headers,
                )

                return update_resp.status_code == 200

        except Exception as e:
            print(f"Failed to sync roles to Entra: {e}")
            return False
