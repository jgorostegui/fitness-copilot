# Fitness Copilot - Task Runner

# Default task: show available commands
default:
    @just --list

# ============== Development ==============

# Start development environment with hot-reload
dev:
    docker compose watch

# Start development environment in detached mode
up:
    docker compose up -d

# Stop all services
down:
    docker compose down

# Stop and remove volumes (clean slate)
clean:
    docker compose down -v

# View logs for all services
logs:
    docker compose logs -f

# View logs for a specific service (e.g., just logs-service backend)
logs-service service:
    docker compose logs -f {{service}}

# Restart a specific service
restart service:
    docker compose restart {{service}}

# Check service status
status:
    docker compose ps

# ============== Docker Shell ==============

# Open a shell in the backend container
shell-backend:
    docker compose exec backend bash

# Open a shell in the frontend container
shell-frontend:
    docker compose exec frontend sh

# Open a shell in the database container
shell-db:
    docker compose exec db psql -U postgres -d app

# Alias for backend shell
sh: shell-backend

# ============== Backend ==============

# Run backend tests (inside Docker)
test-backend:
    docker compose exec backend bash scripts/tests-start.sh

# Run backend tests with specific args (e.g., just test-backend-args "-x -v")
test-backend-args args:
    docker compose exec backend bash scripts/tests-start.sh {{args}}

# Run backend tests locally (requires venv)
test-backend-local:
    cd backend && uv run pytest

# Run backend linting
lint-backend:
    cd backend && uv run ruff check .

# Format backend code
format-backend:
    cd backend && uv run ruff format .

# ============== Frontend ==============

# Run frontend unit tests
test-frontend:
    cd frontend && npm run test

# Run frontend unit tests in watch mode
test-frontend-watch:
    cd frontend && npm run test:watch

# Run frontend E2E tests (requires stack running)
test-frontend-e2e:
    cd frontend && npm run test:e2e

# Run frontend E2E tests with UI
test-frontend-e2e-ui:
    cd frontend && npx playwright test --ui

# Run frontend linting
lint-frontend:
    cd frontend && npm run lint

# Generate OpenAPI client (via Docker)
generate-client:
    docker compose exec backend python -c "import app.main; import json; print(json.dumps(app.main.app.openapi()))" > frontend/openapi.json
    cd frontend && npm run generate-client
    cd frontend && npx biome format --write ./src/client

# ============== Quick Aliases ==============

# Run all tests
test: test-backend test-frontend

# Backend tests (alias)
tb: test-backend

# Frontend tests (alias)
tf: test-frontend

# ============== Database ==============

# Create a new migration (e.g., just migration "add user table")
migration name:
    docker compose exec backend alembic revision --autogenerate -m "{{name}}"

# Run migrations
migrate:
    docker compose exec backend alembic upgrade head

# Rollback last migration
migrate-rollback:
    docker compose exec backend alembic downgrade -1

# Show migration history
migrate-history:
    docker compose exec backend alembic history

# ============== Code Quality ==============

# Install pre-commit hooks
pre-commit-install:
    uv run pre-commit install

# Run pre-commit on all files
pre-commit:
    uv run pre-commit run --all-files

# Run all linters
lint: lint-backend lint-frontend

# Format all code
format: format-backend lint-frontend

# ============== Build & Deploy ==============

# Build all images
build:
    docker compose build

# Pull latest images
pull:
    docker compose pull

# Generate a secret key
secret:
    python -c "import secrets; print(secrets.token_urlsafe(32))"

# ============== GitHub Actions Runner ==============

# Start self-hosted GitHub Actions runner
runner-start:
    docker compose -f docker-compose.runner.yml -p github-runner up -d

# Stop GitHub Actions runner
runner-stop:
    docker compose -f docker-compose.runner.yml -p github-runner down

# View runner logs
runner-logs:
    docker compose -f docker-compose.runner.yml -p github-runner logs -f

# Check runner status
runner-status:
    docker compose -f docker-compose.runner.yml -p github-runner ps
