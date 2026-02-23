---
name: Microsoft Entra Multi-Tenant Integration
description: Implement Microsoft Entra (Azure AD) authentication with multi-tenant support, allowing applications to register with Entra and manage multiple tenant instances with synced users and roles.
argument-hint: 'Feature scope (e.g., "basic single tenant", "multi-tenant with role sync", "with tenant management UI")'
agent: agent
[vscode/memory, vscode/askQuestions, execute, read, agent, 'microsoft-docs/*', edit, search, web, 'pylance-mcp-server/*', todo, ms-ossdata.vscode-pgsql/pgsql_listServers, ms-ossdata.vscode-pgsql/pgsql_connect, ms-ossdata.vscode-pgsql/pgsql_disconnect, ms-ossdata.vscode-pgsql/pgsql_open_script, ms-ossdata.vscode-pgsql/pgsql_visualizeSchema, ms-ossdata.vscode-pgsql/pgsql_query, ms-ossdata.vscode-pgsql/pgsql_modifyDatabase, ms-ossdata.vscode-pgsql/database, ms-ossdata.vscode-pgsql/pgsql_listDatabases, ms-ossdata.vscode-pgsql/pgsql_describeCsv, ms-ossdata.vscode-pgsql/pgsql_bulkLoadCsv, ms-ossdata.vscode-pgsql/pgsql_getDashboardContext, ms-ossdata.vscode-pgsql/pgsql_getMetricData, ms-ossdata.vscode-pgsql/pgsql_migration_oracle_app, ms-ossdata.vscode-pgsql/pgsql_migration_show_report, ms-python.python/getPythonEnvironmentInfo, ms-python.python/getPythonExecutableCommand, ms-python.python/installPythonPackage, ms-python.python/configurePythonEnvironment]
---

# Microsoft Entra Multi-Tenant Integration

Implement Microsoft Entra (Azure AD) integration allowing Techletes applications to:
1. Register as a multi-tenant Entra application
2. Support single or multiple tenant configurations per project
3. Sync users and roles from Microsoft tenants
4. Allow admins to manage which Microsoft tenants are allowed
5. Authenticate users via their Microsoft Entra identity

---

## Background & Architecture

### Multi-Tenant Model

**Key Concepts:**
- **Entra Application (Registration)**: Single app registered in your Azure subscription
- **Tenants**: Customer Azure AD directories connecting to your app
- **Users**: Belong to tenant, authenticated against their tenant's identity provider
- **Roles**: Managed in tenant's Azure AD, synced to application

**Example Scenario:**
```
Your App (Techletes Template)
├── Tenant A (Customer 1's Azure AD)
│   ├── Users: alice@customerA.com, bob@customerA.com
│   └── Roles: Admin, Editor, Viewer
├── Tenant B (Customer 2's Azure AD)
│   ├── Users: charlie@customerB.com, diana@customerB.com
│   └── Roles: Admin, Analyst
└── Tenant C (Customer 3's Azure AD)
    ├── Users: eve@customerC.com
    └── Roles: Viewer
```

**For Single-Tenant Projects:**
- Only one tenant allowed (yours or customer's)
- Configuration via environment variable: `AZURE_TENANT_ID`
- Simpler setup, no tenant management UI needed

**For Multi-Tenant Projects:**
- Multiple tenants configured in database
- Admin UI to add/remove/manage tenants
- Users always log in with their tenant credential

---

## Planning Phase

### 1. Determine Tenant Strategy

**Decision:** Single-tenant or multi-tenant?

**Single-Tenant (Simpler)**
```
AZURE_TENANT_ID=your-tenant-id  # Fixed in .env
AZURE_CLIENT_ID=app-client-id
AZURE_CLIENT_SECRET=app-secret

# Users from only this tenant can log in
```

**Multi-Tenant (More Complex)**
```
# Database stores list of allowed tenants:
allowed_tenants:
  - tenant_id: "tenant-a-id"
    name: "Customer A"
    enabled: true
  - tenant_id: "tenant-b-id"
    name: "Customer B"
    enabled: true

# Users from any allowed tenant can log in
# Each tenant has independent user/role management
```

**Recommendation:** Start with **single-tenant** for MVP, add multi-tenant later if needed.

### 2. Azure Setup Requirements

**What you need before coding:**
1. Azure subscription with Entra ID (Premium P1+ recommended for app roles)
2. Entra Application registration (multi-tenant or single-tenant)
3. Client ID, Client Secret, Tenant ID
4. API permissions set up in Azure
5. Redirect URIs configured

**Azure Entra Scopes Needed:**
```
- openid                    # OpenID Connect
- profile                   # Basic user profile
- email                     # Email address
- https://graph.microsoft.com/.default  # Graph API access
```

**App Roles in Azure (Example):**
```
- Admin       (allows_all_tenant_org_members: true)
- Editor      (allows_all_tenant_org_members: true)
- Viewer      (allows_all_tenant_org_members: false)
```

### 3. User Flow

**Login Flow:**
```
1. User clicks "Login with Microsoft"
2. Redirected to Microsoft login (entra.microsoft.com)
3. User authenticates with their tenant credentials
4. Microsoft redirects back with authorization code
5. Backend exchanges code for access token
6. Backend calls Microsoft Graph API to get user info & roles
7. Backend creates/updates user in database (with tenant & roles)
8. Backend creates JWT token for frontend
9. User logged in with their roles & permissions
```

**Migration Scenarios:**
- **New tenant adding app**: Admin adds tenant ID → new users auto-created on first login
- **User already in system**: Re-login syncs latest roles from Microsoft
- **Role changed in Azure**: Auto-synced on next login
- **User disabled in Azure**: Login blocked/session invalidated next refresh

---

## Research Phase (DO THIS FIRST)

**Before writing any code, research current Microsoft documentation to ensure implementation accuracy:**

### Required Documentation Research

**Visit these verified Microsoft Learn pages to ensure current implementation details:**

1. **Microsoft Entra ID Multi-Tenant Setup** (PRIMARY)
   - URL: https://learn.microsoft.com/entra/identity-platform/howto-convert-app-to-be-multi-tenant
   - Read sections: "Update registration to be multitenant", "Update your code to send requests to /common", "Handle multiple issuer values"
   - Check: Supported account types, App ID URI format, multi-tenant endpoints

2. **Microsoft Entra Overview**
   - URL: https://learn.microsoft.com/entra/architecture/authenticate-applications-and-users
   - Read sections: "Authenticate users", "Request tokens", multi-tenant application models
   - Check: Current tenant-independent endpoints (/common, /organizations)

3. **MSAL React Getting Started** (REQUIRED FOR FRONTEND)
   - URL: https://learn.microsoft.com/entra/msal/javascript/react/getting-started
   - Read sections: "Initialization", "AuthenticatedTemplate", "MsalAuthenticationTemplate"
   - Verify: @azure/msal-react package version, hook patterns, authentication flow

4. **Microsoft Graph API User Endpoint**
   - URL: https://learn.microsoft.com/graph/api/user-get
   - URL: https://learn.microsoft.com/graph/api/user-list-memberof
   - Read: Response structure, required permissions (Directory.Read.All, User.Read)

5. **App Roles and Authorization in Applications**
   - URL: https://learn.microsoft.com/entra/identity-platform/howto-add-app-roles-in-applications
   - Read sections: "Define app roles", "Assign roles to users", "Claim app roles"
   - Check: Current role assignment methods, token claims

6. **Security Best Practices**
   - URL: https://learn.microsoft.com/entra/identity-platform/security-best-practices
   - Critical topics: PKCE for SPAs, secure token storage, token validation, CORS

### What to Check & Verify

- [ ] Current MSAL React package version and breaking changes
- [ ] Latest Microsoft Graph API version (currently v1.0)
- [ ] Current token expiry defaults and refresh mechanisms
- [ ] Latest security recommendations for single-page apps
- [ ] Any deprecations in OAuth 2.0 scope handling
- [ ] Current best practices for multi-tenant applications
- [ ] Latest error handling patterns

### Implementation Accuracy Checklist

Before moving to implementation:
1. ✓ Verified all Microsoft documentation links are current
2. ✓ Checked for any API deprecations between now and when this prompt was written
3. ✓ Confirmed MSAL React installation instructions are current
4. ✓ Verified Microsoft Graph endpoints are at latest version
5. ✓ Checked security recommendations align with current best practices
6. ✓ Confirmed token flow matches current OAuth 2.0/OIDC standards

**Note:** If you find documentation that differs from this prompt, follow the Microsoft official documentation. This prompt was created Feb 2026, and Microsoft may have updated practices since then.

---

## Implementation Strategy

### Phase 1: Backend Setup

#### Step 1.1: Database Models

**Add to `backend/app/models.py`:**

```python
from uuid import UUID
from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime
from typing import Optional

# For single-tenant (simple)
class User(SQLModel, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    email: str = Field(unique=True, index=True)
    
    # Entra fields
    azure_user_id: str | None = Field(index=True)  # Object ID from Azure AD
    tenant_id: str | None = None  # Tenant they belong to
    roles: list[str] = Field(default_factory=list)  # e.g., ["Admin", "Editor"]
    
    # Standard fields
    full_name: str | None = None
    is_active: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
```

**For multi-tenant (add these models):**

```python
class MicrosoftTenant(SQLModel, table=True):
    """Represents an allowed Microsoft tenant"""
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    tenant_id: str = Field(unique=True, index=True)  # Azure AD tenant ID
    tenant_name: str  # Display name (e.g., "Acme Corp")
    is_enabled: bool = True
    
    # Settings
    require_admin_approval_for_new_users: bool = False
    auto_create_users_on_first_login: bool = True
    
    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    created_by: UUID = Field(foreign_key="user.id")  # Admin who added it

class UserTenantRole(SQLModel, table=True):
    """User role mapping per tenant"""
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    user_id: UUID = Field(foreign_key="user.id")
    tenant_id: UUID = Field(foreign_key="microsofttenant.id")
    roles: list[str] = Field(default_factory=list)  # ["Admin", "Editor", "Viewer"]
    is_approved: bool = True  # For approval workflow
    created_at: datetime = Field(default_factory=datetime.utcnow)
```

#### Step 1.2: Entra Configuration

**Add to `backend/app/core/config.py`:**

```python
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Microsoft Entra Configuration
    azure_tenant_id: str = "YOUR_TENANT_ID"  # For single-tenant
    azure_client_id: str = Field(..., description="Azure AD App Client ID")
    azure_client_secret: str = Field(..., description="Azure AD App Client Secret")
    azure_authority: str = "https://login.microsoftonline.com"
    
    # For multi-tenant, leave tenant_id generic or use "common"
    azure_is_multi_tenant: bool = False
    
    # Graph API scope (usually same for all)
    azure_graph_scope: str = "https://graph.microsoft.com/.default"
    
    model_config = SettingsConfigDict(env_file=".env")
```

#### Step 1.3: Microsoft Graph Integration

**Create `backend/app/core/auth_entra.py`:**

```python
import aiohttp
import json
from typing import Optional
from app.core.config import settings

class EntraAuthClient:
    """Handle Microsoft Entra (Azure AD) authentication"""
    
    def __init__(self):
        self.authority = settings.azure_authority
        self.client_id = settings.azure_client_id
        self.client_secret = settings.azure_client_secret
        self.graph_api = "https://graph.microsoft.com/v1.0"
    
    async def get_token_by_auth_code(
        self,
        auth_code: str,
        redirect_uri: str,
        tenant_id: Optional[str] = None,
    ) -> dict:
        """Exchange authorization code for access token
        
        Args:
            auth_code: Authorization code from Microsoft
            redirect_uri: Must match registered redirect URI in Azure
            tenant_id: For multi-tenant, specify tenant. For single, use default.
        """
        if not tenant_id:
            tenant_id = settings.azure_tenant_id
        
        token_url = f"{self.authority}/{tenant_id}/oauth2/v2.0/token"
        
        payload = {
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "code": auth_code,
            "redirect_uri": redirect_uri,
            "grant_type": "authorization_code",
            "scope": settings.azure_graph_scope,
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(token_url, data=payload) as resp:
                if resp.status == 200:
                    return await resp.json()
                else:
                    error = await resp.text()
                    raise Exception(f"Token exchange failed: {error}")
    
    async def get_user_info(self, access_token: str) -> dict:
        """Get user info from Microsoft Graph"""
        headers = {"Authorization": f"Bearer {access_token}"}
        
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"{self.graph_api}/me",
                headers=headers
            ) as resp:
                if resp.status == 200:
                    return await resp.json()
                else:
                    raise Exception(f"Failed to get user info: {resp.status}")
    
    async def get_user_roles(self, access_token: str, user_id: str) -> list[str]:
        """Get app roles assigned to user"""
        headers = {"Authorization": f"Bearer {access_token}"}
        
        async with aiohttp.ClientSession() as session:
            # Get app role assignments
            async with session.get(
                f"{self.graph_api}/me/memberOf",
                headers=headers,
                params={"$select": "displayName"}
            ) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    # Extract role names from appRoleAssignments
                    roles = []
                    for item in data.get("value", []):
                        if "appRole" in item:
                            roles.append(item["appRole"]["displayName"])
                    return roles
                else:
                    return []
    
    def get_login_url(
        self,
        redirect_uri: str,
        tenant_id: Optional[str] = None,
    ) -> str:
        """Generate Microsoft login URL"""
        if not tenant_id:
            tenant_id = settings.azure_tenant_id
        
        params = {
            "client_id": self.client_id,
            "response_type": "code",
            "redirect_uri": redirect_uri,
            "response_mode": "query",
            "scope": "openid profile email " + settings.azure_graph_scope,
            "state": uuid4().hex,  # CSRF protection
        }
        
        query_string = "&".join(f"{k}={v}" for k, v in params.items())
        return f"{self.authority}/{tenant_id}/oauth2/v2.0/authorize?{query_string}"
```

#### Step 1.4: Login Routes

**Create `backend/app/api/routes/auth_entra.py`:**

```python
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from app.core.db import get_session
from app.core.auth_entra import EntraAuthClient
from app.models import User
from app.core.security import create_access_token
from pydantic import BaseModel

router = APIRouter(prefix="/api/v1/auth/entra", tags=["auth"])

class EntraLoginRequest(BaseModel):
    auth_code: str
    redirect_uri: str
    tenant_id: str | None = None  # For multi-tenant

class EntraLoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user_email: str

@router.post("/login")
async def entra_login(
    request: EntraLoginRequest,
    session: Session = Depends(get_session),
) -> EntraLoginResponse:
    """
    Exchange Microsoft auth code for access token
    
    Flow:
    1. Frontend redirects from Microsoft login with auth_code
    2. Backend exchanges code for Microsoft access token
    3. Backend fetches user info from Microsoft Graph
    4. Backend creates/updates user in database
    5. Backend returns JWT for frontend
    """
    entra_client = EntraAuthClient()
    
    try:
        # Step 1: Exchange auth code for Microsoft access token
        token_response = await entra_client.get_token_by_auth_code(
            auth_code=request.auth_code,
            redirect_uri=request.redirect_uri,
            tenant_id=request.tenant_id,
        )
        
        ml_access_token = token_response["access_token"]
        
        # Step 2: Get user info from Microsoft Graph
        user_info = await entra_client.get_user_info(ml_access_token)
        user_roles = await entra_client.get_user_roles(
            ml_access_token,
            user_info["id"]
        )
        
        email = user_info.get("userPrincipalName") or user_info.get("mail")
        
        # Step 3: Find or create user in database
        statement = select(User).where(User.email == email)
        db_user = session.exec(statement).first()
        
        if not db_user:
            # Create new user
            db_user = User(
                email=email,
                full_name=user_info.get("displayName"),
                azure_user_id=user_info.get("id"),
                tenant_id=request.tenant_id,
                roles=user_roles,
                is_active=True,
            )
            session.add(db_user)
        else:
            # Update existing user
            db_user.full_name = user_info.get("displayName")
            db_user.azure_user_id = user_info.get("id")
            db_user.roles = user_roles
            db_user.updated_at = datetime.utcnow()
        
        session.commit()
        session.refresh(db_user)
        
        # Step 4: Create JWT token for frontend
        access_token = create_access_token(subject=str(db_user.id))
        
        return EntraLoginResponse(
            access_token=access_token,
            user_email=email,
        )
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/login-url")
async def get_entra_login_url(
    redirect_uri: str,
    tenant_id: str | None = None,
) -> dict:
    """Get Microsoft login URL for frontend"""
    entra_client = EntraAuthClient()
    login_url = entra_client.get_login_url(redirect_uri, tenant_id)
    return {"login_url": login_url}
```

#### Step 1.5: Update Auth Dependencies

**Modify `backend/app/api/deps.py`:**

```python
# Update get_current_user to check Entra roles
async def get_current_user(
    token: str = Depends(oauth2_scheme),
    session: Session = Depends(get_session),
) -> User:
    """Get current user from JWT token"""
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[ALGORITHM],
        )
        user_id: str = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=403, detail="Invalid credentials")
    except JWTError:
        raise HTTPException(status_code=403, detail="Invalid credentials")
    
    user = session.get(User, UUID(user_id))
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    if not user.is_active:
        raise HTTPException(status_code=403, detail="User is inactive")
    
    return user

# Role-based access control
def require_role(*required_roles: str):
    """Dependency to check if user has required roles"""
    async def check_role(user: User = Depends(get_current_user)) -> User:
        if not any(role in user.roles for role in required_roles):
            raise HTTPException(
                status_code=403,
                detail=f"User does not have required roles: {required_roles}"
            )
        return user
    return check_role
```

---

### Phase 2: Frontend Setup

#### Step 2.1: MSAL React Integration

**Install package:**
```bash
cd frontend
npm install @azure/msal-browser @azure/msal-react
```

**Create `frontend/src/auth/entra.ts`:**

```typescript
import {
  PublicClientApplication,
  Configuration,
  LogLevel,
} from "@azure/msal-browser"

const msalConfig: Configuration = {
  auth: {
    clientId: import.meta.env.VITE_AZURE_CLIENT_ID,
    authority: `https://login.microsoftonline.com/${import.meta.env.VITE_AZURE_TENANT_ID}`,
    redirectUri: import.meta.env.VITE_AZURE_REDIRECT_URI,
    postLogoutRedirectUri: "/",
  },
  cache: {
    cacheLocation: "localStorage",
  },
  system: {
    loggerOptions: {
      loggerCallback: (level, message) => {
        if (level === LogLevel.Error) console.error(message)
      },
    },
  },
}

export const msalInstance = new PublicClientApplication(msalConfig)
```

#### Step 2.2: Login Component

**Create `frontend/src/components/Auth/EntraLogin.tsx`:**

```typescript
import React from "react"
import { useMsal } from "@azure/msal-react"

export function EntraLoginButton() {
  const { instance, inProgress } = useMsal()

  const handleLogin = async () => {
    try {
      const response = await instance.loginPopup({
        scopes: ["openid", "profile", "email"],
      })

      // Get authorization code
      const account = response.account
      if (account) {
        // Send auth code to backend
        const codeResponse = await instance.acquireTokenSilent({
          scopes: ["https://graph.microsoft.com/.default"],
          account: account,
        })

        // Call backend login endpoint
        const backendResponse = await fetch(
          `${import.meta.env.VITE_API_URL}/auth/entra/login`,
          {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
              auth_code: response.accessToken,
              redirect_uri: import.meta.env.VITE_AZURE_REDIRECT_URI,
            }),
          }
        )

        const data = await backendResponse.json()
        // Store JWT token
        localStorage.setItem("token", data.access_token)
        // Redirect to dashboard
        window.location.href = "/"
      }
    } catch (error) {
      console.error("Login failed:", error)
    }
  }

  return (
    <button
      onClick={handleLogin}
      disabled={inProgress !== undefined}
      className="btn btn-primary"
    >
      Login with Microsoft
    </button>
  )
}
```

#### Step 2.3: Add Environment Variables

**Update `frontend/.env.example`:**

```bash
VITE_AZURE_CLIENT_ID=your-client-id-here
VITE_AZURE_TENANT_ID=your-tenant-id-here
VITE_AZURE_REDIRECT_URI=http://localhost:3000/auth-callback
```

---

### Phase 3: Testing & Verification

#### Test Scenarios

```
1. Single-Tenant Login
   ✓ User logs in with Microsoft credentials
   ✓ User created in database with roles
   ✓ JWT token returned
   ✓ User can access protected endpoints

2. Multi-Tenant Scenario
   ✓ Add new tenant to database
   ✓ User from new tenant can login
   ✓ User gets roles from their tenant only
   ✓ Users from different tenants are isolated

3. Role Sync
   ✓ User login syncs latest roles from Microsoft
   ✓ Role added in Azure → visible in app on next login
   ✓ Role removed in Azure → loses access on next refresh

4. Edge Cases
   ✓ User disabled in Azure → login fails
   ✓ Invalid token → proper error handling
   ✓ Token timeout → refresh mechanism
   ✓ Multiple concurrent logins
```

#### Test Commands

```bash
# Backend
cd backend
pytest tests/api/routes/test_auth_entra.py -v

# Frontend
cd frontend
npm run test -- tests/auth/entra.spec.ts
```

---

## Configuration Checklist

Before deployment:

- [ ] Azure Entra App Registration created
- [ ] Client ID, Client Secret, Tenant ID obtained
- [ ] Multi-tenant setting configured in Azure
- [ ] Redirect URIs registered in Azure
- [ ] App roles created in Azure (Admin, Editor, Viewer, etc.)
- [ ] API permissions set (User.Read, Directory.Read.All)
- [ ] `.env` variables populated for backend
- [ ] `.env` variables populated for frontend
- [ ] Database migrations run (new User fields, Tenant models)
- [ ] Backend tests passing
- [ ] Frontend integration tested in dev
- [ ] Logged in user roles match Azure AD groups

---

## Troubleshooting

| Issue | Cause | Solution |
|-------|-------|----------|
| "AADSTS500011: The resource principal named ... was not found" | Tenant ID wrong | Verify `AZURE_TENANT_ID` matches actual tenant |
| "AADSTS65001: User or admin has not consented" | App not approved in tenant | Admin must consent in Azure |
| "AADSTS700016: Application with identifier 'xxx' was not found" | Wrong Client ID | Check `azure_client_id` setting |
| Token exchange fails with 400 | Redirect URI mismatch | Ensure redirect URI matches exactly in Azure |
| User roles not syncing | Graph API permission missing | Check "Directory.Read.All" permission in Azure |
| Roles appear to be admin but still have no access | Role claim missing | Check app roles assigned to user group in Azure |

---

## Security Considerations

✅ **Enable:**
- PKCE for auth code flow (public clients)
- Secure token storage (httpOnly cookies preferred over localStorage)
- CORS restrictions for API
- Rate limiting on login endpoint
- Audit logging of Entra sync events

⚠️ **Verify:**
- Token expiry and refresh mechanism
- CSRF tokens for state parameter
- Admin-only tenant management endpoints
- Audit trail of role changes
- Encryption of stored tenant configs

---

## References

**⚠️ BEFORE STARTING: Complete the Research Phase above first. These are verified current URLs (Feb 2026):**

### Official Microsoft Entra & Identity Docs (PRIMARY)
- **Convert to Multi-Tenant Apps**: https://learn.microsoft.com/entra/identity-platform/howto-convert-app-to-be-multi-tenant
- **Authenticate Apps & Users**: https://learn.microsoft.com/entra/architecture/authenticate-applications-and-users
- **MSAL React Getting Started**: https://learn.microsoft.com/entra/msal/javascript/react/getting-started
- **Microsoft Graph API Overview**: https://learn.microsoft.com/graph/api/overview
- **App Roles in Applications**: https://learn.microsoft.com/entra/identity-platform/howto-add-app-roles-in-applications
- **Security Best Practices**: https://learn.microsoft.com/entra/identity-platform/security-best-practices

### Graph API Endpoints
- **Get User Info**: https://learn.microsoft.com/graph/api/user-get
- **User Member Of (Groups/Roles)**: https://learn.microsoft.com/graph/api/user-list-memberof
- **Permissions Reference**: https://learn.microsoft.com/graph/permissions-reference

### Techletes Template Instructions
- **Backend Auth Patterns**: [Backend Instructions](../../../instructions/backend.instructions.md#auth)
- **Frontend Auth Patterns**: [Frontend Instructions](../../../instructions/frontend.instructions.md#authentication)

### Tools & Libraries
- **MSAL Browser (npm)**: https://www.npmjs.com/package/@azure/msal-browser
- **MSAL React (npm)**: https://www.npmjs.com/package/@azure/msal-react
- **Microsoft Graph SDK Python**: https://pypi.org/project/msgraph-core/

---

## Next Steps

1. **Plan**: Decide single-tenant vs multi-tenant
2. **Azure Setup**: Register app, configure permissions, create roles
3. **Backend**: Implement Entra client, auth routes, user sync
4. **Frontend**: Add MSAL, login component, token management
5. **Test**: Verify login flow, role sync, edge cases
6. **Document**: Add to project README, deployment guide
7. **Deploy**: Set env vars in production, test with real tenant
