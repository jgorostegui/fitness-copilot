# Commands Reference

All commands run from project root using `just`.

## Quick Start
```bash
just dev               # Start dev with hot-reload (backend only)
just dev-frontend      # Start frontend dev server (hot-reload)
just dev-backend       # Start backend dev server locally (hot-reload)
just up                # Start in detached mode
just down              # Stop all services
just status            # Check service status
```

## Development Workflow

### Option 1: Docker with Backend Hot-Reload
```bash
just dev               # Backend hot-reload, frontend serves static files
```

### Option 2: Full Hot-Reload (Recommended)
```bash
# Terminal 1: Start backend + database
just dev

# Terminal 2: Start frontend with hot-reload
just dev-frontend
```

### Option 3: Everything Local (No Docker)
```bash
# Terminal 1: Start database
docker compose up -d db mailcatcher

# Terminal 2: Backend
just dev-backend

# Terminal 3: Frontend
just dev-frontend
```

## Shell Access
```bash
just sh           # Backend shell (quick alias)
just shell-db     # PostgreSQL shell
```

## Testing
```bash
just tb           # Backend tests (Docker)
just tf           # Frontend unit tests (Vitest)
just test         # Run all tests
```

## Database
```bash
just migrate                    # Run migrations
just migration "description"    # Create new migration
```

## Code Quality
```bash
just lint         # Run all linters
just format       # Format all code
just pre-commit   # Run pre-commit hooks
```

## Build
```bash
just generate-client   # Regenerate OpenAPI client
just build             # Build Docker images
```

## Secrets Management
```bash
just sync-secrets      # Sync local .env secrets to GitHub Actions
```

## GitHub Actions Runner
```bash
just runner-start      # Start self-hosted runner
just runner-stop       # Stop runner
just runner-logs       # View runner logs
just runner-status     # Check runner status
```

Setup: Add `GITHUB_RUNNER_TOKEN` to `.env` (get from repo settings → Actions → Runners)
