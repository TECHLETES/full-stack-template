---
name: Techletes Full-Stack Template — Workspace Instructions
description: Internal company template for building full-stack applications with FastAPI, React, and PostgreSQL
---

# Techletes Full-Stack Template — Workspace Instructions

## About This Template

This is **Techletes' internal company template** for building modern full-stack applications focused on data and AI solutions. It's designed to:

- **Be cloned for each new project** — Rapidly spin up new applications with a solid foundation
- **Remain maintainable** — Consistent patterns across all company projects for easy onboarding
- **Be extensible** — Ready for integration with company-specific services (Microsoft Entra, Mistral AI, data connectors, etc.)
- **Support collaboration** — All developers follow the same patterns and best practices

### Core Stack
- **Backend**: FastAPI + SQLModel ORM + PostgreSQL
- **Frontend**: React + TypeScript + Vite + shadcn/ui
- **Infrastructure**: Single unified Docker image, Docker Compose, Caddy, CI/CD with GitHub Actions
- **Dependency Management**: `uv` for Python packages

**Deployment**: Single Docker image that includes both frontend and backend, served together as one application.

---

## Quick Development Commands

### ⚠️ Docker Policy
**DO NOT run `docker compose up` or `docker compose build` unless explicitly instructed.**
- Use `docker-compose.dev.yml` ONLY when base services (PostgreSQL, Redis, etc.) are needed for testing and are not already running.
- Default workflow: Run backend and frontend locally without Docker.

### Backend Only (Recommended for Development)
```bash
cd backend
uv sync                          # Install dependencies
uv run fastapi dev main.py       # Start API server (auto-reload)
./scripts/test.sh                # Run tests
./scripts/lint.sh                # Lint + format
```

### Frontend Only
```bash
cd frontend
npm install                      # Install dependencies
npm run dev                      # Start dev server (hot reload)
npm run test                     # Run Playwright tests
npm run generate-client          # Regenerate API client from OpenAPI spec
```

### Start Base Services Only (When Needed for Testing)
```bash
# Only use this if PostgreSQL and/or Redis are required and not running locally
docker compose -f docker-compose.dev.yml up
# This starts: PostgreSQL (5432), Redis, Adminer (8080)
# Backend and Frontend should still run locally (not in Docker)
```

---

## Architecture & Key Components

### Backend (`/backend`)
- **Entry**: `main.py` — FastAPI app setup, CORS, middleware
- **API Routes**: `api/routes/` — endpoints organized by domain (users, items, login, etc.)
- **Models**: `models.py` — SQLModel definitions (User, Item with relationships)
- **CRUD**: `crud.py` — database operations (create, read, update, delete)
- **Auth**: `core/security.py` — JWT tokens, password hashing (pwdlib with argon2/bcrypt)
- **Config**: `core/config.py` — Pydantic settings, env vars (SECRET_KEY, DATABASE_URL, etc.)
- **DB**: `core/db.py` — database session management
- **Migrations**: `alembic/` — SQLAlchemy auto-migration scripts
- **Tests**: `tests/` — pytest fixtures, unit/integration tests

**Database**: PostgreSQL via SQLModel (async-compatible), migrations via Alembic.

### Frontend (`/frontend`)
- **Entry**: `src/main.tsx` — React app root, routing, theme provider
- **Client**: `src/client/` — auto-generated API client from OpenAPI spec (OpenAPI Generator)
- **Schema**: `src/client/schemas.gen.ts` — generated TypeScript types from backend
- **Routes**: `src/routes/` — TanStack Router (file-based routing)
- **Components**: `src/components/` — reusable UI (Admin, Items, UserSettings, etc.)
- **Hooks**: `src/hooks/` — custom hooks (useAuth, useCustomToast, etc.)
- **Tests**: `tests/` — Playwright E2E tests (auth.setup.ts, *.spec.ts)

**Build**: Vite (fast HMR), TypeScript strict mode, Tailwind + shadcn/ui components, Dark mode support.

### Infrastructure
- **Dockerfile**: Single unified multi-stage build
  - Stage 1: Builds frontend with Bun
  - Stage 2: Builds backend with Python, mounts frontend static files
- **Docker Compose**: `docker-compose.yml` — PostgreSQL, unified app (backend+frontend), Adminer, Caddy (reverse proxy)
- **Static Files**: Frontend built files served from `/backend/static` by FastAPI
- **CI/CD**: GitHub Actions workflows for testing, coverage, Docker builds
- **Docs**: `docs/` — development.md, deployment.md, release-notes.md

---

## Development Workflow

### Docker Setup

The application uses a **single unified Docker image** where:
- Frontend is built with Bun and compiled with Vite
- Frontend build output is served as static files from FastAPI backend
- Both frontend and backend run in the same container on port 8000

### 1. Backend Changes
```bash
cd backend
# Edit models.py, crud.py, api/routes/*, core/config.py, etc.
# Server auto-reloads on save (when running: uv run fastapi dev main.py)

# After editing models.py:
alembic revision --autogenerate -m "description"
alembic upgrade head

# Lint & format:
./scripts/lint.sh  # Ruff (E, W, F, I, B, C4, UP, etc.), strict Mypy

# Test:
./scripts/test.sh  # Pytest with coverage
```

### 2. Frontend Changes
```bash
cd frontend
# Edit src/components/*, src/routes/*, src/hooks/*, etc.
# HMR (hot reload) enabled automatically

# After backend API changes:
npm run generate-client  # Regenerates src/client/schemas.gen.ts, sdk.gen.ts

# Lint & format:
npm run lint  # Biome (formatting, linting)

# Test E2E:
npm run test  # Playwright tests (integration with running backend)
```

### 3. Database
1. Edit `backend/models.py` (add fields, relationships)
2. Run: `cd backend && alembic revision --autogenerate -m "add new field"`
3. Run: `alembic upgrade head` to apply
4. Restart backend if using Docker Compose

---

## Code Patterns & Conventions

### Backend

**SQLModel + Relationships**:
- All models inherit from `SQLModel` and use `table=True` for DB models
- Primary keys: UUID (default_factory=uuid.uuid4)
- Timestamps: `created_at` with timezone-aware UTC
- Use `Relationship` for Foreign Keys with cascade delete

**Auth**:
- JWT tokens (configurable expiry)
- Passwords: hashed with pwdlib (Argon2/Bcrypt)
- Depends on `get_current_user` middleware
- Email-based password recovery

**API Routes** (`api/routes/`):
- Organized by domain (users.py, items.py, login.py, etc.)
- Use dependency injection for auth & DB sessions
- Return Pydantic models (not SQLModel table models)
- FastAPI auto-generates OpenAPI schema

**Validation**:
- Pydantic models for input/output validation
- EmailStr for emails, Field(min_length=..., max_length=...) for strings
- Custom validators with `@field_validator`

### Frontend

**React + TypeScript**:
- Strict TypeScript mode enabled
- Hooks-based components (no class components)
- File-based routing with TanStack Router (`src/routes/` subdirectories = URL structure)

**API Integration**:
- Use auto-generated client: `import { ... } from '@/client'`
- Types from `src/client/schemas.gen.ts`
- Error handling with custom toast hook: `useCustomToast()`

**UI Components**:
- All from shadcn/ui or custom in `src/components/ui/`
- Tailwind CSS for styling
- Dark mode provider: `<ThemeProvider>` in root layout

**Testing**:
- Playwright for E2E tests (`tests/*.spec.ts`)
- `tests/auth.setup.ts` handles login flow reuse
- `tests/utils/privateApi.ts` for API helpers, `mailcatcher.ts` for email testing

---

## Environment & Configuration

### Backend Config (`core/config.py`)
Load from `.env` via Pydantic Settings:
- `SECRET_KEY` — JWT signing key (generate: `python -c "import secrets; print(secrets.token_urlsafe(32))"`)
- `DATABASE_URL` — PostgreSQL connection
- `ENVIRONMENT` — "local", "staging", "production"
- `FIRST_SUPERUSER` / `FIRST_SUPERUSER_PASSWORD` — initial admin account
- `SMTP_HOST`, `SMTP_PORT` — email sending (Mailcatcher for dev)
- `BACKEND_CORS_ORIGINS` — allowed frontend origins
- `SENTRY_DSN` — error tracking (optional)

### Backend Server Configuration (Docker)
The `backend/scripts/entrypoint.sh` auto-configures the FastAPI server based on `ENVIRONMENT` variable, but can be overridden:
- `WORKERS` — Number of Gunicorn workers (default: 4)
- `BACKEND_HOST` — Server bind address (default: 0.0.0.0)
- `BACKEND_PORT` — Server port (default: 8000)
- `LOG_LEVEL` — Logging verbosity: debug, info, warning, error (default: debug/info/warning based on environment)
- `RELOAD` — Auto-reload on code changes (default: false, set true for local development)

**Example for production scaling:**
```bash
# In docker-compose.yml or .env for production deployment
ENVIRONMENT=production
WORKERS=8          # Scale workers for your CPU count
LOG_LEVEL=warning  # Reduce log verbosity
```

### Frontend Config
- `.env.local` for local overrides
- `vite.config.ts` — Vite settings (API proxy to `http://localhost:8000`)
- `playwright.config.ts` — E2E test settings (baseURL, workers, timeout)

---

## Testing Strategy

### Backend (`pytest`)
- `tests/api/routes/` — route/endpoint tests
- `tests/crud/` — database operation tests
- `tests/utils/` — helper functions (seed data, users, items)
- `conftest.py` — fixtures (client, async session, test user)
- **Run**: `cd backend && ./scripts/test.sh` or `pytest`
- **Coverage**: tracked in CI, see badge in README

### Frontend (`Playwright`)
- `tests/auth.setup.ts` — shared login flow (reuses tokens)
- `tests/login.spec.ts`, `tests/admin.spec.ts`, etc. — feature tests
- `tests/utils/mailcatcher.ts` — email verification helpers
- **Run**: `cd frontend && npm run test` or `npm run test:ui`
- **Note**: Requires running backend API

---

## Common Tasks

### Add a New API Endpoint
1. Add model to `backend/models.py` (if needed)
2. Add route in `backend/api/routes/newfeature.py` with proper dependencies
3. Register route in `backend/api/main.py` via `APIRouter`
4. Add tests in `backend/tests/api/routes/test_newfeature.py`
5. **⚠️ CRITICAL: Frontend MUST regenerate OpenAPI client** — Never add an endpoint directly without regenerating:
   ```bash
   ./scripts/generate-client.sh  # Regenerates src/client/schemas.gen.ts, sdk.gen.ts
   ```
   This ensures type safety and keeps frontend types in sync with backend API.
6. Use new client in `src/components/` or route with auto-generated types

### Add a New Frontend Page
1. Create route file in `src/routes/` (e.g., `src/routes/mypage.tsx`)
2. Add components in `src/components/MyPage/`
3. Use auto-generated client types: `import { ItemPublic } from '@/client'`
4. Add E2E test in `tests/mypage.spec.ts`
5. Link from sidebar in `src/components/Sidebar/`

### Update TypeScript Client
After backend changes:
```bash
cd frontend
npm run generate-client  # Updates src/client/schemas.gen.ts, sdk.gen.ts
```

### Database Migration
```bash
cd backend
# After editing models.py:
alembic revision --autogenerate -m "descriptive name"
alembic upgrade head
```

### Linting & Formatting
```bash
# Backend
cd backend && ./scripts/lint.sh  # Ruff + Mypy

# Frontend
cd frontend && npm run lint      # Biome
```

---

## Docker Usage Rules

**MUST READ: These rules are strictly enforced.**

1. **Never run `docker compose up` or `docker compose build` for development** unless explicitly instructed by the user.
2. **Do not use the unified Docker image locally** — It's designed for production deployment, not local development.
3. **Use `docker-compose.dev.yml` ONLY for base services** (PostgreSQL, Redis) when:
   - They are required for testing/development
   - They are not already running on your local machine
   - You explicitly need database persistence across restarts
4. **Default workflow**: Always run backend (`uv run fastapi dev main.py`) and frontend (`npm run dev`) locally on your machine.
5. **When to use `docker-compose.dev.yml`**:
   ```bash
   # Only if PostgreSQL/Redis are needed AND not running locally
   docker compose -f docker-compose.dev.yml up
   ```
6. **Backend and Frontend should always run locally**, even if base services are in Docker.

**Why?** Local development is faster (auto-reload, HMR), easier to debug, and doesn't require Docker context switching.

---

## Debugging & Troubleshooting

### Backend Issues
- **Server won't start**: Check `.env` DATABASE_URL, run `docker compose up db` first
- **Import errors**: Run `cd backend && uv sync`
- **Migration conflicts**: Check `alembic/versions/`, remove conflicting files if safe
- **Type errors**: Run `mypy app` locally for type checking before testing

### Frontend Issues
- **Client out of sync**: Run `npm run generate-client` after backend changes
- **Playwright timeouts**: Ensure backend is running on `http://localhost:8000`
- **Node modules broken**: Delete `node_modules/` and `.pnp.cjs`, run `npm install`

### Database Issues
- **Postgres won't connect**: Check compose.yml env vars, ensure `docker compose up db` runs
- **Migration issues**: Drop testdb, restart container, re-run migrations
- **Admin panel (Adminer)**: http://localhost:8080 for manual inspection

---

## Key Tools & Versions

| Tool | Purpose | Location |
|------|---------|----------|
| `uv` | Python package manager | root→backend dependency |
| `pytest` | Backend testing | backend/pyproject.toml |
| `ruff` | Python linter/formatter | backend/pyproject.toml |
| `mypy` | Type checking | backend/pyproject.toml |
| `alembic` | Database migrations | backend/alembic/ |
| `bun` / `npm` | Node package manager | frontend |
| `vite` | Frontend bundler | frontend/vite.config.ts |
| `playwright` | E2E testing | frontend/playwright.config.ts |
| `biome` | TypeScript linter | frontend/biome.json |
| `docker compose` | Local dev env | compose.yml (all-in-one command) |
| `openapi-ts` | Generate client from OpenAPI | frontend/openapi-ts.config.ts |

---

## Template Maintenance & Evolution

This template is continuously improved with new capabilities for Techletes projects. When making changes:

**For all projects using this template:**
- ✅ Keep core layer structure intact (backend/app, frontend/src, docker compose)
- ✅ Maintain backward compatibility where possible
- ✅ Update project docs when adding new features
- ✅ Add skills/instructions for new patterns (in `.github/` folder)

**Implemented integrations:**
- ✅ **Microsoft Entra ID** — Single sign-on and enterprise authentication (multi-tenant support)

**Planned integrations & enhancements:**
- 🤖 **Mistral AI** — Ready-to-use LLM integration patterns
- 📊 **Data Connectors** — Common data source patterns (SQL, APIs, files)
- 🔍 **Advanced Search** — Full-text and semantic search capabilities
- 📈 **Analytics** — Built-in metrics, logging, and monitoring

When these are added to the template, existing projects can pull updates via:
```bash
git pull --no-commit upstream master   # Pull from template
# Review, resolve conflicts, merge when ready
```

---

## Microsoft Entra ID (Azure AD) Integration

This template includes enterprise-ready Microsoft Entra ID authentication with multi-tenant support. The feature is **opt-in** — leave `AZURE_CLIENT_ID` empty to keep email/password-only authentication.

### Quickstart

1. **Register app in Azure Entra** — Follow [docs/ENTRA_SETUP.md](docs/ENTRA_SETUP.md)
2. **Set environment variables in `.env`:**
   ```bash
   AZURE_CLIENT_ID=<your-client-id>
   AZURE_CLIENT_SECRET=<your-client-secret>
   AZURE_TENANT_ID=<your-tenant-id>
   ```
3. **Run migrations:** `cd backend && alembic upgrade head`
4. **Restart:** `docker compose up --build`

### Architecture

- **Backend**: `core/auth_entra.py` — Microsoft Graph API client for token validation
- **Frontend**: `src/auth/entra.ts` — MSAL initialization; `src/components/Auth/EntraLogin.tsx` — login button
- **Routes**: `api/routes/auth_entra.py` — endpoints: `/auth/entra/login`, `/auth/entra/config`, `/tenants/` CRUD
- **Models**: Extended `User` with `azure_user_id`, `azure_tenant_id`, `azure_roles`; new `MicrosoftTenant` and `UserTenantRole` models

### How It Works

1. Frontend fetches public config from `/api/v1/auth/entra/config`
2. Initializes MSAL with CLIENT_ID and TENANT_ID
3. User clicks "Sign in with Microsoft" → redirects to Microsoft login
4. Returns with access token → sent to backend `/auth/entra/login`
5. Backend validates token via Microsoft Graph (using CLIENT_SECRET internally)
6. Backend returns JWT for all subsequent API calls

### Testing

```bash
# Check if Entra is enabled:
curl http://localhost:8000/api/v1/auth/entra/config

# Run backend tests (includes Entra mocks):
cd backend && ./scripts/test.sh

# Manual test: Click "Sign in with Microsoft" on login page
```

### Single-Tenant vs Multi-Tenant

The backend always uses the `organizations` endpoint (multi-tenant capable). Access control is managed in your **Azure app registration** — restrict to one tenant or allow any there. The database tenant management (`/api/v1/tenants/`) is for application-level organization (roles, data isolation), not access gating.

- **Single-tenant app**: Register app in Azure scoped to your tenant, don't add other tenants in the DB
- **Multi-tenant SaaS**: Allow any tenant in Azure, register customer tenants via `/api/v1/tenants/`

### Common Tasks

**Enable Entra in existing project:**
```bash
# 1. Update .env with Azure credentials
# 2. Run migrations: cd backend && alembic upgrade head
# 3. Restart: docker compose up --build
```

**Disable Entra (keep email/password):**
```bash
# 1. Remove AZURE_CLIENT_ID from .env (leave empty)
# 2. Restart — login page reverts to email/password form only
```

### Troubleshooting

**"Sign in with Microsoft" button doesn't appear:**
- Check: Is `AZURE_CLIENT_ID` set in `.env`?
- Check: Browser console for MSAL config errors
- Run: `curl http://localhost:8000/api/v1/auth/entra/config` to verify backend config

**Login redirects to Microsoft but returns with error:**
- Check: Is redirect URI `http://localhost:5173` registered in Azure app?
- Check: Are API permissions set (openid, profile, email, User.Read)?
- Check: Is `.env` correctly configured?

**See detailed troubleshooting:** [docs/ENTRA_SETUP.md](docs/ENTRA_SETUP.md#testing-the-integration)

---

TanStack Router uses file structure in `src/routes/`:
```
src/routes/
  __root.tsx          → Root layout <RootComponent>
  _layout.tsx         → Wrapper layout (e.g., with sidebar)
  _layout/
    index.tsx         → / (home/dashboard)
    admin.tsx         → /admin
    items.tsx         → /items
    user-settings.tsx → /user-settings
    login.tsx         → /login (outside _layout)
    signup.tsx        → /signup
    recover-password.tsx → /recover-password
    reset-password.tsx  → /reset-password
```

---

## Design System Reference

**All UI/UX development uses [frontend/design-brief.json](../../frontend/design-brief.json)** as the authoritative design reference.

This includes:
- Layout system, spacing tokens, and responsive breakpoints
- Component patterns (cards, buttons, forms, tables, badges, etc.)
- Color system with brand orange and neutral grays
- Typography scale and font weights
- Dark mode specifications
- Interaction states and accessibility requirements

When suggesting UI changes or reviewing component design, align recommendations with the design brief.

## When to Ask Me (Agent) Questions

- **Architecture decisions**: Suggest where to add new features (backend route + DB model vs frontend component)
- **File organization**: Clarify if code belongs in routes, components, utils, or hooks
- **API design**: Review endpoint design before implementation
- **Type safety**: Help with TypeScript schema validation
- **Performance**: Suggest optimizations for queries, caching, pagination
- **Testing**: Recommend test coverage, fixtures, mocking strategies
- **Design alignment**: Verify component designs match the design brief specifications

---

## Links & References

- [FastAPI Docs](https://fastapi.tiangolo.com)
- [SQLModel Docs](https://sqlmodel.tiangolo.com)
- [React Docs](https://react.dev)
- [Vite Docs](https://vitejs.dev)
- [TanStack Router](https://tanstack.com/router/latest)
- [Playwright Docs](https://playwright.dev)
- [Docker Compose Docs](https://docs.docker.com/compose)

---

**Auto-reload enabled** in dev mode. Edit code → save → see changes immediately.
Keep backend API running during frontend development. Keep frontend running during E2E tests.
