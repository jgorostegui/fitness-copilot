# Commands Reference

All commands run from project root using `just`.

## Quick Start
```bash
just dev          # Start dev environment with hot-reload
just up           # Start in detached mode
just down         # Stop all services
just status       # Check service status
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
