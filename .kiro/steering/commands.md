# Commands Reference

All commands run from project root using `just`.

## Quick Start
```bash
just dev           # Full stack with hot-reload (backend + frontend + db)
just frontend      # Frontend locally (optional, slightly faster HMR)
just backend       # Backend locally (no Docker, requires: just db)
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
just up            # Start all services (dev mode with override)
just up-prod       # Start production stack (ignores override)
just down          # Stop all services
just clean         # Stop and remove volumes
just status        # Check service status
just logs          # View all logs
just build         # Rebuild images
```

**How docker-compose files work:**
- `docker-compose.yml` - Base production config
- `docker-compose.override.yml` - Dev overrides (auto-merged by default)
- `just up` / `just dev` - Uses both files (dev mode)
- `just up-prod` - Uses only base file (production mode)

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

**IMPORTANT: Always use `just` commands for testing. Never use raw `uv run pytest` or `cd backend` commands.**

```bash
just test              # All tests (backend + frontend)
just test-backend      # Backend tests only (alias: just tb)
just test-unit         # Unit tests only (alias: just tu)
just test-acceptance   # Acceptance tests only (alias: just ta)
just test-integration  # Integration tests (alias: just ti)
just test-frontend     # Frontend tests only (alias: just tf)
just test-e2e          # E2E tests (alias: just te)
just test-e2e-ui       # E2E with UI
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

### Development (hot-reload)
```bash
# Terminal 1: just dev
# Terminal 2: just frontend
# Terminal 3: just test-e2e
```
Tests run against dev servers with hot-reload.

### CI-like (Docker builds)
```bash
just e2e              # Full cycle: up, test, down
just e2e-up           # Start Docker stack
just test-e2e         # Run tests
just e2e-down         # Stop stack
```

## Database

**IMPORTANT: Always use `just` commands for database operations.**

```bash
just migrate                    # Run migrations
just migration "description"    # Create migration
just migrate-rollback           # Rollback last
```

## Code Quality (Host Machine)
```bash
just lint              # All linters (backend + frontend)
just lint-backend      # Backend: ruff check + format check
just lint-frontend     # Frontend: biome check
just format            # Format all code
just format-backend    # Backend: ruff check --fix + ruff format
just format-frontend   # Frontend: biome format --write
just check             # All quality checks (lint)
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
just build-staging         # Build all Docker images (mimics CI deploy)
just generate-client       # Regenerate OpenAPI client (Docker, requires: just dev)
just generate-client-local # Regenerate OpenAPI client (local, no Docker)
just secret                # Generate secret key
just sync-secrets          # Sync .env to GitHub
```

## GitHub Actions Runner
```bash
just runner-start      # Start self-hosted runner
just runner-stop       # Stop runner
just runner-logs       # View runner logs
just runner-status     # Check runner status
```

Setup: Add `GITHUB_RUNNER_TOKEN` to `.env` (get from repo settings → Actions → Runners)
