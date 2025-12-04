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
just sh            # Backend shell
just db-shell      # PostgreSQL shell
just frontend-shell # Frontend shell
```

## Testing (Host Machine)
```bash
just test          # All tests
just tb            # Backend tests (alias)
just tf            # Frontend tests (alias)
just te            # E2E tests (alias)
just test-e2e-ui   # E2E with UI
```

## Testing (Inside Docker)
```bash
just docker-test                    # All tests in Docker
just docker-test-backend            # Backend tests in Docker
just docker-test-backend-args "-x"  # Backend tests with args
```

## E2E Testing
```bash
just e2e-up           # Start full stack
just e2e-run          # Run E2E tests (from host)
just e2e-run-docker   # Run E2E tests (inside Docker)
just e2e-run-headed   # Run E2E with visible browser
just e2e-down         # Stop stack
just e2e              # Full cycle: up, test, down
```

## Database (Inside Docker)
```bash
just migrate                    # Run migrations
just migration "description"    # Create migration
just migrate-rollback           # Rollback last
just migrate-history            # Show history
```

## Code Quality (Host Machine)
```bash
just lint          # All linters
just format        # Format all code
just pre-commit    # Run pre-commit hooks
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
