# Fitness Copilot - Task Runner

default:
    @just --list

# ============== Development ==============

# Start backend + database with hot-reload
dev:
    docker compose watch

# Start frontend dev server with hot-reload
frontend:
    cd frontend && npm run dev

# Start backend locally (requires: just db)
backend:
    cd backend && uv run fastapi dev app/main.py

# Start only database and mailcatcher
db:
    docker compose up -d db mailcatcher

# ============== Docker Management ==============

up:
    docker compose up -d

# Start production stack (ignores override, uses production builds)
up-prod:
    docker compose -f docker-compose.yml up -d

down:
    docker compose down

clean:
    docker compose down -v

logs:
    docker compose logs -f

status:
    docker compose ps

build:
    docker compose build

# ============== Shell Access ==============

# Backend shell (run --rm: works even if container not running)
docker-shell:
    @echo "Opening shell in backend container..."
    docker compose run --rm backend bash

# Backend shell (exec: faster, requires running container)
sh:
    docker compose exec backend bash

# Database shell
db-sh:
    docker compose exec db psql -U postgres -d app

# ============== Docker Commands ==============

# Run any command (run --rm: creates new container, always works)
docker-run cmd:
    docker compose run --rm backend bash -c "{{cmd}}"

# Run any command (exec: faster, requires running container)
docker-exec cmd:
    docker compose exec backend bash -c "{{cmd}}"

# ============== Docker Testing (requires: just dev or just up) ==============

# Run all backend tests in Docker
docker-test:
    @echo "Running backend tests in Docker..."
    docker compose exec backend bash scripts/tests-start.sh

# Run backend tests with args (e.g., just docker-test-args "-x -v")
docker-test-args args:
    docker compose exec backend bash scripts/tests-start.sh {{args}}

# Run unit tests only in Docker
docker-test-unit:
    @echo "Running unit tests in Docker..."
    docker compose exec backend uv run pytest -m unit -v

# Run acceptance tests only in Docker
docker-test-acceptance:
    @echo "Running acceptance tests in Docker..."
    docker compose exec backend uv run pytest -m acceptance -v

# Run integration tests in Docker (live external services, skipped by default)
# Uses -s to show LLM output for debugging
docker-test-integration:
    @echo "Running integration tests in Docker (live external services)..."
    docker compose exec backend bash -c "RUN_INTEGRATION_TESTS=1 uv run pytest -m integration -v -s --tb=short"

# Run tests with coverage in Docker
docker-test-coverage:
    @echo "Running tests with coverage in Docker..."
    docker compose exec backend uv run pytest --cov=app --cov-report=html --cov-report=term-missing

# Run E2E tests inside Docker (playwright container)
docker-e2e:
    docker compose run --rm playwright npx playwright test

# ============== Testing (Host) ==============

test: test-backend test-frontend

test-backend:
    cd backend && uv run pytest

# Run unit tests only (Small - no DB required)
test-unit:
    @echo "Running unit tests (Small - no DB)..."
    cd backend && uv run pytest -m unit -v

# Run acceptance tests only (Medium - DB required, mocks external)
test-acceptance:
    @echo "Running acceptance tests (Medium - DB required)..."
    cd backend && uv run pytest -m acceptance -v

# Run integration tests (Large - live external services, skipped by default)
# Uses -s to show LLM output for debugging
test-integration:
    @echo "Running integration tests (Large - live external services)..."
    cd backend && RUN_INTEGRATION_TESTS=1 uv run pytest -m integration -v -s --tb=short

test-frontend:
    cd frontend && npm run test

test-e2e:
    cd frontend && npx playwright test

test-e2e-ui:
    cd frontend && npx playwright test --ui

# ============== E2E Testing ==============
# Development: run "just dev" + "just frontend" in separate terminals, then "just test-e2e"
# CI-like: run "just e2e" for full Docker-based cycle

# Start Docker stack for E2E (CI-like, uses production builds)
e2e-up:
    docker network create traefik-public || true
    docker compose up -d --wait backend frontend db mailcatcher proxy adminer

e2e-down:
    docker compose down -v --remove-orphans

# Full E2E cycle with Docker (CI-like)
e2e: e2e-up test-e2e e2e-down

# ============== Code Quality (Host) ==============

# Lint all with auto-fix
lint: lint-backend lint-frontend

# Lint backend with auto-fix (ruff check --fix + format)
lint-backend:
    cd backend && uv run ruff check app --fix
    cd backend && uv run ruff format app

# Lint frontend with auto-fix
lint-frontend:
    cd frontend && npx biome check --fix ./

# Format all
format: format-backend format-frontend

# Format backend (ruff check --fix + ruff format)
format-backend:
    cd backend && uv run ruff check app --fix
    cd backend && uv run ruff format app

# Format frontend
format-frontend:
    cd frontend && npx biome format --write ./

# Auto-fix lint issues (ruff check --fix only, no formatting)
lint-fix: lint-fix-backend lint-fix-frontend

# Auto-fix backend lint issues
lint-fix-backend:
    cd backend && uv run ruff check app --fix

# Auto-fix frontend lint issues
lint-fix-frontend:
    cd frontend && npx biome check --fix ./

pre-commit:
    uv run pre-commit run --all-files

# Run all quality checks (lint + format check)
check: lint

# ============== Security Scanning ==============

# Run Bandit security scan
security-bandit:
    @echo "Running Bandit security scan..."
    cd backend && uv run bandit -r app/ -f screen

# Run Safety dependency scan
security-safety:
    @echo "Running Safety dependency scan..."
    cd backend && uv run safety check

# Run all security scans
security: security-bandit security-safety

# ============== Database ==============

migrate:
    docker compose exec backend alembic upgrade head

migration name:
    docker compose exec backend alembic revision --autogenerate -m "{{name}}"

migrate-rollback:
    docker compose exec backend alembic downgrade -1

# ============== Build ==============

# Build all images via docker compose (mimics staging deploy exactly)
build-staging:
    @echo "Building images via docker compose (same as staging deploy)..."
    docker compose -f docker-compose.yml build

# ============== Utilities ==============

# Generate OpenAPI client (requires: just dev or just up)
generate-client:
    ./scripts/generate-client.sh

# Generate OpenAPI client locally (no Docker, requires backend venv)
generate-client-local:
    ./scripts/generate-client.sh --local

secret:
    python -c "import secrets; print(secrets.token_urlsafe(32))"

# ============== GitHub Actions Runner ==============

runner-start:
    docker compose -f docker-compose.runner.yml -p github-runner up -d

runner-stop:
    docker compose -f docker-compose.runner.yml -p github-runner stop -t 60
    docker compose -f docker-compose.runner.yml -p github-runner down

runner-logs:
    docker compose -f docker-compose.runner.yml -p github-runner logs -f

runner-status:
    docker compose -f docker-compose.runner.yml -p github-runner ps

sync-secrets:
    ./scripts/sync-secrets.sh

# ============== Aliases ==============

tb: test-backend
tu: test-unit
ta: test-acceptance
ti: test-integration
tf: test-frontend
te: test-e2e
