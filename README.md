# 🚀 Techletes Full Stack FastAPI Template

**A modern, production-ready full-stack template for building custom data and AI applications at Techletes.**

<a href="https://github.com/TECHLETES/full-stack-template/actions?query=workflow%3A%22Test+Docker+Compose%22" target="_blank"><img src="https://github.com/TECHLETES/full-stack-template/workflows/Test%20Docker%20Compose/badge.svg" alt="Test Docker Compose"></a>
<a href="https://github.com/TECHLETES/full-stack-template/actions?query=workflow%3A%22Test+Backend%22" target="_blank"><img src="https://github.com/TECHLETES/full-stack-template/workflows/Test%20Backend/badge.svg" alt="Test Backend"></a>
![Test Coverage](./coverage.svg)

---

## About This Template

This is **Techletes' internal company template** for building full-stack applications. It's designed to be:
- **Cloned and customized** for each new project
- **Extensible** with company-specific integrations (Microsoft Entra, Mistral AI, custom data connectors, etc.)
- **Production-ready** with security, testing, and deployment best practices built-in
- **Maintainable** by providing consistent patterns and architectural guidance for all company projects

Perfect for rapid development of custom solutions in data, AI, and business applications.

## Technology Stack and Features

- ⚡ [**FastAPI**](https://fastapi.tiangolo.com) for the Python backend API.
  - 🧰 [SQLModel](https://sqlmodel.tiangolo.com) for the Python SQL database interactions (ORM).
  - 🔍 [Pydantic](https://docs.pydantic.dev), used by FastAPI, for the data validation and settings management.
  - 💾 [PostgreSQL](https://www.postgresql.org) as the SQL database.
- 🚀 [React](https://react.dev) for the frontend.
  - 💃 Using TypeScript, hooks, [Vite](https://vitejs.dev), and other parts of a modern frontend stack.
  - 🎨 [Tailwind CSS](https://tailwindcss.com) and [shadcn/ui](https://ui.shadcn.com) for the frontend components.
  - 🤖 An automatically generated frontend client.
  - 🧪 [Playwright](https://playwright.dev) for End-to-End testing.
  - 🦇 Dark mode support.
- 🐋 [Docker Compose](https://www.docker.com) for development and production.
- 🔒 Secure password hashing by default.
- 🔑 JWT (JSON Web Token) authentication.
- 📫 Email based password recovery.
- 📬 [Mailcatcher](https://mailcatcher.me) for local email testing during development.
- ⏳ [RQ (Redis Queue)](https://python-rq.org/) for background job processing and file uploads.
- 💾 File storage with support for local filesystem or S3-compatible object storage.
- ✅ Tests with [Pytest](https://pytest.org).
- 📞 [Caddy](https://caddyserver.com/) as a reverse proxy / load balancer.
- 🚢 Deployment instructions using Docker Compose, including how to set up a frontend Caddy proxy to handle automatic HTTPS certificates.
- 🏭 CI (continuous integration) and CD (continuous deployment) based on GitHub Actions.

### Planned Company Integrations & Extensions

Future versions will include built-in support for:
- 🔐 **Microsoft Entra ID** — Single sign-on (SSO) for enterprise authentication
- 🤖 **Mistral AI** — Ready-to-integrate LLM models for AI-powered features
- 📊 **Data Connectors** — Common data source integrations (SQL, APIs, files)
- 🔍 **Search** — Full-text search, semantic search, and filtering patterns
- 📈 **Analytics** — Built-in metrics and monitoring patterns

### Dashboard Login

[![API docs](img/login.png)](https://github.com/TECHLETES/full-stack-template)

### Dashboard - Admin

[![API docs](img/dashboard.png)](https://github.com/TECHLETES/full-stack-template)

### Dashboard - Items

[![API docs](img/dashboard-items.png)](https://github.com/TECHLETES/full-stack-template)

### Dashboard - Dark Mode

[![API docs](img/dashboard-dark.png)](https://github.com/TECHLETES/full-stack-template)

### Interactive API Documentation

[![API docs](img/docs.png)](https://github.com/TECHLETES/full-stack-template)

## Quick Start – Clone for Your Project

This template is designed to be **cloned and customized** for each new Techletes project.

### Clone & Setup

For a quick start, simply clone this repository:

```bash
git clone https://github.com/Techletes/full-stack-template.git my-project
cd my-project
# Update .env files and customize as needed
docker compose up --build
```

### Customization Workflow

1. **Clone the template** to your project directory
2. **Update `.env` files** with your project credentials and settings
3. **Customize models** in `backend/models.py` for your domain
4. **Add API routes** in `backend/api/routes/`
5. **Build frontend pages** in `frontend/src/routes/` and `frontend/src/components/`
6. **Create background tasks** in `backend/tasks/` for long-running operations (emails, exports, file processing)
7. **Integrate company services** (Microsoft Entra, Mistral AI, data connectors, etc.)
8. **Deploy** using Docker Compose or your preferred platform

See [development.md](./development.md) for detailed guidance on file uploads, background tasks, and local development.

### Set Up Your Project Repository

Each Techletes project should have its own repository. If you want a private repository hosting your project:

- Create a new private GitHub repository under the Techletes organization
- Clone this template repository:

```bash
git clone https://github.com/Techletes/full-stack-template.git my-project
cd my-project
```

- Point the repository to your new project repository:

```bash
git remote set-url origin git@github.com:Techletes/my-project.git
```

- Keep this template as an upstream remote to receive updates:

```bash
git remote add upstream https://github.com/Techletes/full-stack-template.git
```

- Push your initial code:

```bash
git push -u origin main
```

### Keep Your Project Updated

As the template evolves with new integrations and improvements, you can pull updates:

```bash
# Pull latest changes from template (without auto-merging)
git pull --no-commit upstream main

# Review changes, resolve conflicts if needed
# Then commit when ready:
git merge --continue
```

### Configure

You can then update configs in the `.env` files to customize your configurations.

Before deploying it, make sure you change at least the values for:

- `SECRET_KEY`
- `FIRST_SUPERUSER_PASSWORD`
- `POSTGRES_PASSWORD`

You can (and should) pass these as environment variables from secrets.

Read the [deployment.md](./deployment.md) docs for more details.

### Generate Secret Keys

Some environment variables in the `.env` file have a default value of `changethis`.

You have to change them with a secret key, to generate secret keys you can run the following command:

```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

Copy the content and use that as password / secret key. And run that again to generate another secure key.

## Dependency Management

This project uses [**uv**](https://docs.astral.sh/uv/) — a fast, modern Python package manager — for managing dependencies.

### Install uv

If you're on **Linux** and don't have uv installed yet:

```bash
# Using curl (recommended)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Or using apt (if available in your distro)
sudo apt install uv

# Or using pip
pip install uv
```

After installation, verify it works:

```bash
uv --version
```

### Managing Dependencies

Dependencies for the backend are defined in [backend/pyproject.toml](./backend/pyproject.toml). Frontend dependencies are in [frontend/package.json](./frontend/package.json).

#### Common uv Commands

Run these commands from the project root or respective `backend/` and `frontend/` directories:

**Sync all dependencies** to your virtual environment:
```bash
cd backend
uv sync              # Install/update all dependencies from lock file
```

**Update lock file** after modifying `pyproject.toml`:
```bash
cd backend
uv lock              # Generate/update uv.lock based on pyproject.toml
```

**Upgrade all dependencies** to their latest versions:
```bash
cd backend
uv lock --upgrade    # Update uv.lock to latest compatible versions
```

**Add a new dependency**:
```bash
cd backend
uv add package-name  # Add and sync automatically
```

**Remove a dependency**:
```bash
cd backend
uv remove package-name  # Remove and sync automatically
```

**Run a script** with dependencies installed:
```bash
cd backend
uv run fastapi dev main.py  # Run command in the managed environment
```

### Workflow

1. **Initial setup**: `uv sync` installs all dependencies from the lock file
2. **Edit requirements**: Modify `backend/pyproject.toml` to add/remove/change versions
3. **Update lock file**: Run `uv lock` to resolve and lock the new versions
4. **Sync locally**: Run `uv sync` to install the updated dependencies
5. **Commit changes**: Commit both `pyproject.toml` and `uv.lock` to version control

For more details, see the [uv documentation](https://docs.astral.sh/uv/).

## Backend Development

Backend docs: [backend/README.md](./backend/README.md).

## Frontend Development

Frontend docs: [frontend/README.md](./frontend/README.md).

## Deployment

Deployment docs: [deployment.md](./deployment.md).

## Development

General development docs: [development.md](./development.md).

This includes using Docker Compose, custom local domains, `.env` configurations, etc.

## Release Notes

Check the file [release-notes.md](./release-notes.md).

## License

The Full Stack FastAPI Template is licensed under the terms of the MIT license.
