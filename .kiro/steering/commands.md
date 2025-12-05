# Commands Reference

All commands run from project root using `just`.

## Quick Start
```bash
just dev           # Backend + db (hot-reload)
just frontend      # Frontend (hot-reload)
just backend       # Backend locally (no Docker)
```

## Development Workflows

### Standard
```bash
just dev
```
Backend + database with hot-reload. Frontend serves static.

### Full Hot-Reload
```bash
# Terminal 1
just dev

# Terminal 2
just frontend
```
Both backend and frontend with hot-reload.

### Local Backend
```bash
# Terminal 1
just db

# Terminal 2
just backend
```
Fastest reload, requires Python setup.

## Docker Management
```bash
just up            # Start all services
just down          # Stop all services
just clean         # Stop and remove volumes
just status        # Check service status
just logs          # View all logs
just build         # Rebuild images
```

## Shell Access (Inside Docker)
```bash
just docker-shell  # Backend shell (run --rm, works even if not running)
just sh            # Backend shell (exec into running container)
just db-sh         # PostgreSQL shell
```

## Testing Philosophy

This project uses Google's **Small/Medium/Large** test sizing.
See: [Test Sizes - Google Testing Blog](https://testing.googleblog.com/2010/12/test-sizes.html)

| Size       | Marker       | Network        | Database | External Services | CI Behavior      |
|------------|--------------|----------------|----------|-------------------|------------------|
| **Small**  | `unit`       | No             | No       | No                | Must pass        |
| **Medium** | `acceptance` | localhost only | Yes      | Mocked            | Must pass        |
| **Large**  | `integration`| Yes            | Yes      | Live (Gemini)     | Skipped by default |

## Testing (Host Machine)

```bash
just test              # All tests (backend + frontend)
just test-backend      # Backend tests only
just test-unit         # Unit tests only (Small - no DB required)
just test-acceptance   # Acceptance tests only (Medium - DB required)
just test-integration  # Integration tests (Large - live external services)
just test-frontend     # Frontend tests only
just test-e2e          # E2E tests (Playwright)
just test-e2e-ui       # E2E with UI

# Aliases
just tb                # Backend tests (alias)
just tu                # Unit tests (alias)
just ta                # Acceptance tests (alias)
just ti                # Integration tests (alias)
just tf                # Frontend tests (alias)
just te                # E2E tests (alias)

# Direct uv commands (from backend directory)
cd backend
uv run pytest                    # Run all tests
uv run pytest -x                 # Stop on first failure
uv run pytest -k "test_name"     # Run specific test
uv run pytest -m unit            # Run only unit tests (no DB)
uv run pytest -m acceptance      # Run only acceptance tests (DB required)
uv run pytest -m integration     # Run only integration tests (live external)
uv run pytest --cov=app          # Run with coverage
```

## Docker Commands (Atomic)
```bash
just docker-run "cmd"       # Run any command (run --rm: creates new container, always works)
just docker-exec "cmd"      # Run any command (exec: faster, requires running container)
```

## Testing (Inside Docker) - requires: just dev or just up

```bash
just docker-test                    # All backend tests
just docker-test-args "-x -v"       # Backend tests with args
just docker-test-unit               # Unit tests only
just docker-test-acceptance         # Acceptance tests only
just docker-test-integration        # Integration tests (live external)
just docker-test-coverage           # Tests with coverage report
just docker-e2e                     # E2E tests (playwright container)
```

## E2E Testing
```bash
just e2e-up           # Start full stack for E2E
just test-e2e         # Run E2E tests (from host)
just docker-e2e       # Run E2E tests (inside Docker)
just e2e-down         # Stop stack
just e2e              # Full cycle: up, test, down
just docker-e2e-full  # Full cycle in Docker: up, docker-e2e, down
```

## Database (Inside Docker)
```bash
just migrate                    # Run migrations
just migration "description"    # Create migration
just migrate-rollback           # Rollback last
```

## Database (Local - from backend directory)
```bash
cd backend
uv run alembic upgrade head                           # Run migrations
uv run alembic revision --autogenerate -m "desc"      # Create migration
uv run alembic downgrade -1                           # Rollback last
uv run alembic history                                # Show history
```

## Code Quality (Host Machine)
```bash
just lint              # All linters (backend + frontend)
just lint-backend      # Backend linting only
just lint-frontend     # Frontend linting only
just format            # Format all code
just format-backend    # Format backend only
just format-frontend   # Format frontend only
just format-check      # Check formatting without fixing
just check             # All quality checks (lint + format check)
just pre-commit        # Run pre-commit hooks
```

## Security Scanning
```bash
just security          # Run all security scans
just security-bandit   # Bandit code security scan
just security-safety   # Safety dependency vulnerability scan
```

## Build & Utilities
```bash
just generate-client   # Regenerate OpenAPI client
just secret            # Generate secret key
just sync-secrets      # Sync .env to GitHub
```

## GitHub Actions Runner
```bash
just runner-start      # Start self-hosted runner
just runner-stop       # Stop runner
just runner-logs       # View runner logs
just runner-status     # Check runner status
```

Setup: Add `GITHUB_RUNNER_TOKEN` to `.env` (get from repo settings → Actions → Runners)
