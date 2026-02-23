# RecAIPe Development Setup

## Quick Start

### Prerequisites
- Docker & Docker Compose
- uv (Python package manager)
- Node.js/npm (for frontend)

### 1. Full Stack Development (Recommended)

```bash
# Clone and navigate to project
cd /home/development/recaipe

# Start all services (backend, frontend, database, adminer)
docker compose up --build
```

**Services:**
- 🖥️ **Frontend**: http://localhost:3000
- 🚀 **Backend API**: http://localhost:8000
- 📚 **API Docs**: http://localhost:8000/docs
- 🗄️ **Database Admin**: http://localhost:8080

### 2. Backend Only Development

```bash
# Install dependencies
uv sync

cd /home/development/recaipe/backend

# Start backend server
uv run fastapi dev app/main.py
```

**Backend available at:** http://localhost:8000

### 3. Frontend Only Development

```bash
cd /home/development/recaipe/frontend

# Install dependencies
npm install

# Start dev server
npm run dev
```

**Frontend available at:** http://localhost:5173

## Development Workflow

### Making Backend Changes
1. Edit files in `backend/app/`
2. Server auto-reloads on save
3. Run tests: `cd backend && ./scripts/test.sh`
4. Check API docs at http://localhost:8000/docs

### Making Frontend Changes
1. Edit files in `frontend/src/`
2. Hot reload enabled
3. Run tests: `cd frontend && npm run test`
4. Regenerate client after API changes: `npm run generate-client`

### Database Changes
1. Edit models in `backend/app/models.py`
2. Create migration: `cd backend && alembic revision --autogenerate -m "description"`
3. Apply migration: `alembic upgrade head`

## Environment Setup

### .env Configuration
Copy `.env.example` to `.env` and update:
- `SECRET_KEY` - Generate with: `python -c "import secrets; print(secrets.token_urlsafe(32))"`
- `POSTGRES_PASSWORD` - Set secure password
- `FIRST_SUPERUSER_PASSWORD` - Set admin password

### Database
- **Host**: localhost:5432
- **User**: postgres
- **Database**: app
- **Admin Interface**: http://localhost:8080

## Testing

```bash
# Backend tests
cd backend && ./scripts/test.sh

# Frontend tests
cd frontend && npm run test
```

## Troubleshooting

### Backend Issues
- Ensure `uv sync` completed successfully
- Check database is running: `docker compose ps`
- View logs: `docker compose logs backend`

### Frontend Issues
- Clear node_modules: `rm -rf node_modules && npm install`
- Check port conflicts (default: 5173)

### Database Issues
- Reset database: `docker compose down -v && docker compose up --build`
- Access adminer at http://localhost:8080

## Project Structure

```
recaipe/
├── backend/          # FastAPI backend
│   ├── app/         # Application code
│   ├── tests/       # Backend tests
│   └── scripts/     # Dev scripts
├── frontend/        # React frontend
│   ├── src/         # Source code
│   └── tests/       # Frontend tests
├── docs/            # Documentation
└── docker-compose.yml
```

## Need Help?

- 📖 **Architecture**: `docs/ARCHITECTURE.md`
- 🔧 **Backend Guide**: `backend/README.md`
- 🎨 **Frontend Guide**: `frontend/README.md`
- 📋 **Roadmap**: `docs/ROADMAP.md`</content>
<parameter name="filePath">/home/development/recaipe/DEV_SETUP.md