#!/usr/bin/env bash
set -e

# =============================================================================
# Docker Entrypoint for FastAPI Backend
# Handles prestart tasks and server initialization with production-ready config
# =============================================================================

# Get environment variables with sensible defaults
ENVIRONMENT="${ENVIRONMENT:-local}"
BACKEND_PORT="${BACKEND_PORT:-8000}"
WORKERS="${WORKERS:-4}"

echo "[Entrypoint] Starting FastAPI Backend Initialization"
echo "[Entrypoint] Environment: $ENVIRONMENT"
echo "[Entrypoint] Workers: $WORKERS"

# Step 1: Wait for database to be ready
echo "[Entrypoint] Step 1/3: Waiting for database..."
python utils/backend_pre_start.py
if [ $? -ne 0 ]; then
    echo "[Entrypoint] ERROR: Database pre-start checks failed"
    exit 1
fi

# Step 2: Run database migrations (BEFORE RBAC initialization)
echo "[Entrypoint] Step 2/3: Running database migrations..."
alembic upgrade head
if [ $? -ne 0 ]; then
    echo "[Entrypoint] ERROR: Database migrations failed"
    exit 1
fi

# Step 3: Create initial data
echo "[Entrypoint] Step 3/3: Initializing database with seed data..."
python utils/initial_data.py
if [ $? -ne 0 ]; then
    echo "[Entrypoint] ERROR: Initial data creation failed"
    exit 1
fi

echo "[Entrypoint] Initialization complete. Starting FastAPI server..."
echo "[Entrypoint] Listening on port $BACKEND_PORT"

# Build fastapi command based on configuration
FASTAPI_CMD="fastapi run --port $BACKEND_PORT --workers $WORKERS"

# Use exec to replace shell process with FastAPI, preserving PID signals
exec $FASTAPI_CMD main.py
