# 🚀 Techletes Full Stack FastAPI Template

**A modern, production-ready full-stack template for building custom data and AI applications at Techletes.**

<a href="https://github.com/fastapi/full-stack-fastapi-template/actions?query=workflow%3A%22Test+Docker+Compose%22" target="_blank"><img src="https://github.com/fastapi/full-stack-fastapi-template/workflows/Test%20Docker%20Compose/badge.svg" alt="Test Docker Compose"></a>
<a href="https://github.com/fastapi/full-stack-fastapi-template/actions?query=workflow%3A%22Test+Backend%22" target="_blank"><img src="https://github.com/fastapi/full-stack-fastapi-template/workflows/Test%20Backend/badge.svg" alt="Test Backend"></a>
<a href="https://coverage-badge.samuelcolvin.workers.dev/redirect/fastapi/full-stack-fastapi-template" target="_blank"><img src="https://coverage-badge.samuelcolvin.workers.dev/fastapi/full-stack-fastapi-template.svg" alt="Coverage"></a>

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

[![API docs](img/login.png)](https://github.com/fastapi/full-stack-fastapi-template)

### Dashboard - Admin

[![API docs](img/dashboard.png)](https://github.com/fastapi/full-stack-fastapi-template)

### Dashboard - Items

[![API docs](img/dashboard-items.png)](https://github.com/fastapi/full-stack-fastapi-template)

### Dashboard - Dark Mode

[![API docs](img/dashboard-dark.png)](https://github.com/fastapi/full-stack-fastapi-template)

### Interactive API Documentation

[![API docs](img/docs.png)](https://github.com/fastapi/full-stack-fastapi-template)

## Quick Start – Clone for Your Project

This template is designed to be **cloned and customized** for each new Techletes project.

### Option 1: Simple Clone (Recommended)

For a quick start, simply clone this repository:

```bash
git clone https://github.com/Techletes/full-stack-template.git my-project
cd my-project
# Update .env files and customize as needed
docker compose up --build
```

### Option 2: Clone with Copier (Automated Setup)

Use [Copier](https://copier.readthedocs.io) to automatically configure project details:

```bash
pipx install copier
copier copy https://github.com/Techletes/full-stack-template.git my-project
```

This will ask for project name, stack name, credentials, and other configuration.

### Customization Workflow

1. **Clone the template** to your project directory
2. **Update `.env` files** with your project credentials and settings
3. **Customize models** in `backend/models.py` for your domain
4. **Add API routes** in `backend/api/routes/`
5. **Build frontend pages** in `frontend/src/routes/` and `frontend/src/components/`
6. **Integrate company services** (Microsoft Entra, Mistral AI, data connectors, etc.)
7. **Deploy** using Docker Compose or your preferred platform

See [development.md](./development.md) for detailed guidance.

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
git push -u origin master
```

### Keep Your Project Updated

As the template evolves with new integrations and improvements, you can pull updates:

```bash
# Pull latest changes from template (without auto-merging)
git pull --no-commit upstream master

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

## How To Use It - Alternative With Copier

This repository also supports generating a new project using [Copier](https://copier.readthedocs.io).

It will copy all the files, ask you configuration questions, and update the `.env` files with your answers.

### Install Copier

You can install Copier with:

```bash
pip install copier
```

Or better, if you have [`pipx`](https://pipx.pypa.io/), you can run it with:

```bash
pipx install copier
```

**Note**: If you have `pipx`, installing copier is optional, you could run it directly.

### Generate a Project With Copier

Decide a name for your new project's directory, you will use it below. For example, `my-awesome-project`.

Go to the directory that will be the parent of your project, and run the command with your project's name:

```bash
copier copy https://github.com/fastapi/full-stack-fastapi-template my-awesome-project --trust
```

If you have `pipx` and you didn't install `copier`, you can run it directly:

```bash
pipx run copier copy https://github.com/fastapi/full-stack-fastapi-template my-awesome-project --trust
```

**Note** the `--trust` option is necessary to be able to execute a [post-creation script](https://github.com/fastapi/full-stack-fastapi-template/blob/master/.copier/update_dotenv.py) that updates your `.env` files.

### Input Variables

Copier will ask you for some data, you might want to have at hand before generating the project.

But don't worry, you can just update any of that in the `.env` files afterwards.

The input variables, with their default values (some auto generated) are:

- `project_name`: (default: `"FastAPI Project"`) The name of the project, shown to API users (in .env).
- `stack_name`: (default: `"fastapi-project"`) The name of the stack used for Docker Compose labels and project name (no spaces, no periods) (in .env).
- `secret_key`: (default: `"changethis"`) The secret key for the project, used for security, stored in .env, you can generate one with the method above.
- `first_superuser`: (default: `"admin@example.com"`) The email of the first superuser (in .env).
- `first_superuser_password`: (default: `"changethis"`) The password of the first superuser (in .env).
- `smtp_host`: (default: "") The SMTP server host to send emails, you can set it later in .env.
- `smtp_user`: (default: "") The SMTP server user to send emails, you can set it later in .env.
- `smtp_password`: (default: "") The SMTP server password to send emails, you can set it later in .env.
- `emails_from_email`: (default: `"info@example.com"`) The email account to send emails from, you can set it later in .env.
- `postgres_password`: (default: `"changethis"`) The password for the PostgreSQL database, stored in .env, you can generate one with the method above.
- `sentry_dsn`: (default: "") The DSN for Sentry, if you are using it, you can set it later in .env.

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
