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

# Backend shell
sh:
    docker compose exec backend bash

# Database shell
db-sh:
    docker compose exec db psql -U postgres -d app

# ============== Docker Run (execute command inside container) ==============

# Run any command inside backend container
docker-run cmd:
    docker compose exec backend bash -c "{{cmd}}"

# Run backend tests inside Docker
docker-test:
    docker compose exec backend bash scripts/tests-start.sh

# Run backend tests with args
docker-test-args args:
    docker compose exec backend bash scripts/tests-start.sh {{args}}

# Run E2E tests inside Docker (playwright container)
docker-e2e:
    docker compose run --rm playwright npx playwright test

# ============== Testing (Host) ==============

test: test-backend test-frontend

test-backend:
    cd backend && uv run pytest

test-frontend:
    cd frontend && npm run test

test-e2e:
    cd frontend && npx playwright test

test-e2e-ui:
    cd frontend && npx playwright test --ui

# ============== E2E Stack ==============

e2e-up:
    docker network create traefik-public || true
    docker compose up -d --wait backend frontend db mailcatcher proxy adminer

e2e-down:
    docker compose down -v --remove-orphans

# Full E2E cycle
e2e: e2e-up test-e2e e2e-down

# Full E2E cycle inside Docker
docker-e2e-full: e2e-up docker-e2e e2e-down

# ============== Code Quality (Host) ==============

lint: lint-backend lint-frontend

lint-backend:
    cd backend && uv run ruff check .

lint-frontend:
    cd frontend && npm run lint

format: format-backend format-frontend

format-backend:
    cd backend && uv run ruff format .

format-frontend:
    cd frontend && npx biome format --write ./

pre-commit:
    uv run pre-commit run --all-files

# ============== Database ==============

migrate:
    docker compose exec backend alembic upgrade head

migration name:
    docker compose exec backend alembic revision --autogenerate -m "{{name}}"

migrate-rollback:
    docker compose exec backend alembic downgrade -1

# ============== Utilities ==============

generate-client:
    docker compose exec backend python -c "import app.main; import json; print(json.dumps(app.main.app.openapi()))" > frontend/openapi.json
    cd frontend && npm run generate-client
    cd frontend && npx biome format --write ./src/client

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
tf: test-frontend
te: test-e2e
