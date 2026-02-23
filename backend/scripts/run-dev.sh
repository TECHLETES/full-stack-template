#!/bin/bash
set -e

echo "🚀 Starting development environment..."

# Sync Python dependencies
echo "📦 Installing Python dependencies..."
uv sync

# Load environment variables if using direnv
if command -v direnv &> /dev/null; then
    echo "🔧 Loading direnv configuration..."
    direnv allow
fi

# Start Docker Compose services (PostgreSQL, etc.)
echo "🐳 Starting Docker Compose services..."
docker compose -f ../docker-compose.dev.yml up -d

# Wait for PostgreSQL to be ready with health check
echo "⏳ Waiting for database to be ready..."
MAX_ATTEMPTS=30
ATTEMPT=1

while [ $ATTEMPT -le $MAX_ATTEMPTS ]; do
    if docker compose exec -T db pg_isready -U postgres > /dev/null 2>&1; then
        echo "✅ Database is ready!"
        break
    fi
    echo "   Attempt $ATTEMPT/$MAX_ATTEMPTS: Database not ready yet, waiting..."
    sleep 1
    ATTEMPT=$((ATTEMPT + 1))
done

if [ $ATTEMPT -gt $MAX_ATTEMPTS ]; then
    echo "❌ Database failed to start after $MAX_ATTEMPTS attempts"
    docker compose logs db
    exit 1
fi

# Set PYTHONPATH to enable app module imports
export PYTHONPATH="${PWD}:$PYTHONPATH"

uv run python app/backend_pre_start.py

# Run migrations and setup
echo "🔄 Running database migrations..."
uv run alembic upgrade head

# Initialize database with sample data
echo "🌱 Initializing database with sample data..."
uv run python app/initial_data.py

# Start FastAPI dev server with auto-reload in current terminal
echo "✨ Starting FastAPI development server..."
uv run fastapi dev app/main.py


