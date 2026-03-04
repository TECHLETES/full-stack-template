# FastAPI Project - Development

## Design System

All UI/UX development is guided by the **[design-brief.json](../frontend/design-brief.json)** specification. This document defines:

- **Layout System**: Navigation sidebar, top utility bar, content grid, responsive behavior
- **Design Tokens**: Spacing, radius values, borders, shadows, typography scales
- **Color System**: Brand orange accent, neutral grays for light/dark modes, accent colors (success, danger, warning, info)
- **Component Patterns**: Cards, metric tiles, tables, buttons, input fields, badges, charts
- **Interaction States**: Hover, active, disabled, focus states
- **Accessibility**: Contrast requirements, keyboard navigation, color independence
- **Dark Mode**: Adaptations for reduced shadow reliance and increased border visibility

When building new UI components or pages, refer to the design brief for consistent spacing, colors, typography, and behavior.

## Docker Compose

* Start the local stack with Docker Compose:

```bash
docker compose watch
```

* Now you can open your browser and interact with these URLs:

Frontend and Backend, both served from the same unified Docker image: <http://localhost:8000>

The frontend is automatically bundled with the backend and served as static files.

Automatic interactive documentation with Swagger UI (from the OpenAPI backend): <http://localhost:8000/docs>

Adminer, database web administration: <http://localhost:8080>

**Note**: The first time you start your stack, it might take a few minutes for it to be ready. While the backend waits for the database to be ready, configures everything, and the Docker image builds both the frontend and backend components. You can check the logs to monitor it.

To check the logs, run (in another terminal):

```bash
docker compose logs
```

To check the logs of a specific service, add the name of the service, e.g.:

```bash
docker compose logs backend
```

## Unified Docker Image

The application is now built as a **single Docker image** that includes:

- **Frontend**: Built with Bun and compiled with Vite
- **Backend**: FastAPI Python application
- **Static Files**: Frontend assets served by FastAPI

The unified `Dockerfile` at the root of the project:
1. Builds the frontend using Bun
2. Compiles the frontend with Vite
3. Builds the backend Python environment
4. Mounts the compiled frontend as static files in the backend
5. Serves both through a single FastAPI application

This means there's only one Docker image and container to manage, simplifying deployment and reducing resource usage.

## Mailcatcher

Mailcatcher is a simple SMTP server that catches all emails sent by the backend during local development. Instead of sending real emails, they are captured and displayed in a web interface.

This is useful for:

* Testing email functionality during development
* Verifying email content and formatting
* Debugging email-related functionality without sending real emails

The backend is automatically configured to use Mailcatcher when running with Docker Compose locally (SMTP on port 1025). All captured emails can be viewed at <http://localhost:1080>.

## Background Tasks with RQ

The template includes **RQ (Redis Queue)** for background task processing. This allows you to offload long-running operations from the HTTP request cycle.

### What You Can Do

- **Upload Files**: Process file uploads asynchronously (e.g., generate thumbnails, extract metadata)
- **Send Emails**: Queue transactional emails to send in the background
- **Export Data**: Generate and export large datasets without blocking the API
- **Run Scheduled Tasks**: Use RQ's job scheduler for recurring tasks

### Architecture

- **Redis**: Broker for job queue
- **RQ Worker**: Background process that picks up jobs and executes them
- **API Endpoints**: Queue jobs via `/api/v1/tasks/enqueue`, check status via `/api/v1/tasks/{job_id}`

### Starting the Worker in Development

When you run `./backend/scripts/run-dev.sh`, the RQ worker starts automatically in the background alongside FastAPI.

To start the worker manually:

```bash
cd backend
uv run bash scripts/start-worker.sh
```

Or directly:

```bash
cd backend
uv run python worker.py
```

The worker monitors three queues (in priority order): `high`, `default`, `low`.

**Note**: In Docker Compose, code changes to tasks will automatically restart the worker container. For local development without Docker, restart the worker manually to pick up task changes.

### Creating Background Tasks

Tasks are simple Python functions in `backend/tasks/example.py`. Example:

```python
def send_email_task(to: str, subject: str, body: str) -> dict[str, str]:
    """Send email in the background."""
    # Your email logic here
    return {"status": "sent"}
```

### Enqueueing Jobs

From your API endpoint or FastAPI route:

```python
from backend.core.queue import get_queue
from backend.tasks.example import send_email_task

queue = get_queue("default")
job = queue.enqueue(send_email_task, to="user@example.com", subject="Hello")
```

Or via the HTTP API:

```bash
curl -X POST http://localhost:8000/api/v1/tasks/enqueue \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "task": "send_email",
    "queue": "default",
    "kwargs": {"to": "user@example.com", "subject": "Hello", "body": "Hi!"}
  }'
```

### Checking Job Status

```bash
curl http://localhost:8000/api/v1/tasks/{job_id} \
  -H "Authorization: Bearer $TOKEN"
```

### Docker Compose

In Docker Compose, a separate `worker` service runs the RQ worker alongside the main `backend` service. Both share the same `uploads-data` volume for file storage.

## Local Development

The Docker Compose files are configured to have the services available on different ports in `localhost`.

The backend (which includes the frontend) is available at `http://localhost:8000`.

For frontend-only development, you can run the frontend locally in a separate terminal (outside of Docker) while keeping the backend running in Docker:

```bash
cd frontend
npm run dev
```

This will start the frontend development server at `http://localhost:5173` with hot reload enabled, connecting to the backend API running at `http://localhost:8000`.

For backend-only development, you can run the backend directly:

```bash
cd backend
uv run fastapi dev main.py
```

This will start the backend development server at `http://localhost:8000` with auto-reload enabled.
```

And then start the local frontend development server:

```bash
bun run dev
```

Or you could stop the `backend` Docker Compose service:

```bash
docker compose stop backend
```

And then you can run the local development server for the backend:

```bash
cd backend
fastapi dev main.py
```

## Docker Compose in `localhost.tiangolo.com`

When you start the Docker Compose stack, it uses `localhost` by default, with different ports for each service (backend, frontend, adminer, etc).

When you deploy it to production (or staging), it will deploy each service in a different subdomain, like `api.example.com` for the backend and `dashboard.example.com` for the frontend.

In the guide about [deployment](deployment.md) you can read about Caddy, the configured proxy. That's the component in charge of transmitting traffic to each service based on the subdomain.

If you want to test that it's all working locally, you can edit the local `.env` file, and change:

```dotenv
DOMAIN=localhost.tiangolo.com
```

That will be used by the Docker Compose files to configure the base domain for the services.

Caddy will use this to transmit traffic at `api.localhost.tiangolo.com` to the backend, and traffic at `dashboard.localhost.tiangolo.com` to the frontend.

The domain `localhost.tiangolo.com` is a special domain that is configured (with all its subdomains) to point to `127.0.0.1`. This way you can use that for your local development.

After you update it, run again:

```bash
docker compose watch
```

When deploying, for example in production, the main Caddy is configured outside of the Docker Compose files. For local development, there's an included Caddy in `compose.override.yml`, just to let you test that the domains work as expected, for example with `api.localhost.tiangolo.com` and `dashboard.localhost.tiangolo.com`.

## Docker Compose files and env vars

There is a main `compose.yml` file with all the configurations that apply to the whole stack, it is used automatically by `docker compose`.

And there's also a `compose.override.yml` with overrides for development, for example to mount the source code as a volume. It is used automatically by `docker compose` to apply overrides on top of `compose.yml`.

These Docker Compose files use the `.env` file containing configurations to be injected as environment variables in the containers.

They also use some additional configurations taken from environment variables set in the scripts before calling the `docker compose` command.

After changing variables, make sure you restart the stack:

```bash
docker compose watch
```

## The .env file

The `.env` file is the one that contains all your configurations, generated keys and passwords, etc.

Depending on your workflow, you could want to exclude it from Git, for example if your project is public. In that case, you would have to make sure to set up a way for your CI tools to obtain it while building or deploying your project.

One way to do it could be to add each environment variable to your CI/CD system, and updating the `compose.yml` file to read that specific env var instead of reading the `.env` file.

## Pre-commits and code linting

we are using a tool called [prek](https://prek.j178.dev/) (modern alternative to [Pre-commit](https://pre-commit.com/)) for code linting and formatting.

When you install it, it runs right before making a commit in git. This way it ensures that the code is consistent and formatted even before it is committed.

You can find a file `.pre-commit-config.yaml` with configurations at the root of the project.

#### Install prek to run automatically

`prek` is already part of the dependencies of the project.

After having the `prek` tool installed and available, you need to "install" it in the local repository, so that it runs automatically before each commit.

Using `uv`, you could do it with (make sure you are inside `backend` folder):

```bash
❯ uv run prek install -f
prek installed at `../.git/hooks/pre-commit`
```

The `-f` flag forces the installation, in case there was already a `pre-commit` hook previously installed.

Now whenever you try to commit, e.g. with:

```bash
git commit
```

...prek will run and check and format the code you are about to commit, and will ask you to add that code (stage it) with git again before committing.

Then you can `git add` the modified/fixed files again and now you can commit.

#### Running prek hooks manually

you can also run `prek` manually on all the files, you can do it using `uv` with:

```bash
❯ uv run prek run --all-files
check for added large files..............................................Passed
check toml...............................................................Passed
check yaml...............................................................Passed
fix end of files.........................................................Passed
trim trailing whitespace.................................................Passed
ruff.....................................................................Passed
ruff-format..............................................................Passed
biome check..............................................................Passed
```

## URLs

The production or staging URLs would use these same paths, but with your own domain.

### Development URLs

Development URLs, for local development.

Frontend: <http://localhost:5173>

Backend: <http://localhost:8000>

Automatic Interactive Docs (Swagger UI): <http://localhost:8000/docs>

Automatic Alternative Docs (ReDoc): <http://localhost:8000/redoc>

Adminer: <http://localhost:8080>

Caddy UI: <http://localhost:2019>

MailCatcher: <http://localhost:1080>

### Development URLs with `localhost.tiangolo.com` Configured

Development URLs, for local development.

Frontend: <http://dashboard.localhost.tiangolo.com>

Backend: <http://api.localhost.tiangolo.com>

Automatic Interactive Docs (Swagger UI): <http://api.localhost.tiangolo.com/docs>

Automatic Alternative Docs (ReDoc): <http://api.localhost.tiangolo.com/redoc>

Adminer: <http://localhost.tiangolo.com:8080>

Caddy UI: <http://localhost.tiangolo.com:2019>

MailCatcher: <http://localhost.tiangolo.com:1080>
