# Fitness Copilot - Task Runner

# Default task: show available commands
default:
    @just --list

# ============== Development ==============

# Start development (backend + db with hot-reload)
dev:
    docker compose watch

# Start frontend dev server with hot-reload
frontend:
    cd frontend && npm run dev

# Start backend locally (no Docker, requires: docker compose up -d db mailcatcher)
backend:
    cd backend && uv run fastapi dev app/main.py

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

# ============== E2E Testing (CI-like) ==============

# Start stack for E2E tests (without playwright container)
e2e-up:
    docker network create traefik-public || true
    docker compose up -d --wait backend frontend db mailcatcher proxy adminer

# Run E2E tests against running stack (local playwright)
e2e-run:
    cd frontend && npx playwright test

# Run E2E tests with headed browser (visible)
e2e-run-headed:
    cd frontend && npx playwright test --headed

# Run E2E tests in Docker container
e2e-run-docker:
    docker compose run --rm playwright npx playwright test

# Stop E2E stack and cleanup
e2e-down:
    docker compose down -v --remove-orphans

# Full E2E test cycle (start, test, stop)
e2e: e2e-up e2e-run e2e-down

# E2E alias
te: e2e-run

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

# Stop GitHub Actions runner gracefully
runner-stop:
    docker compose -f docker-compose.runner.yml -p github-runner stop -t 60
    docker compose -f docker-compose.runner.yml -p github-runner down

# Force stop and clean runner (use when stuck)
runner-kill:
    docker compose -f docker-compose.runner.yml -p github-runner down -v --remove-orphans -t 5

# Restart runner (clean restart)
runner-restart: runner-stop runner-start

# View runner logs
runner-logs:
    docker compose -f docker-compose.runner.yml -p github-runner logs -f

# Check runner status
runner-status:
    docker compose -f docker-compose.runner.yml -p github-runner ps

# Sync secrets from .env to GitHub
sync-secrets:
    ./scripts/sync-secrets.sh
