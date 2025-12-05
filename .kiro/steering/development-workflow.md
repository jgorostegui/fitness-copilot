# Development Workflow

**IMPORTANT: Always use `just` commands. Never use raw `docker compose`, `uv run`, or `cd` commands.**

## Getting Started

### Start Development Environment
```bash
just dev       # Full stack with hot-reload (backend + frontend + db)
```

This single command starts everything with hot-reload:
- **Backend**: FastAPI with file sync hot-reload
- **Frontend**: Vite dev server with HMR
- **Database**: PostgreSQL

Services available:
- Frontend: http://localhost:5173
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs
- Adminer (DB): http://localhost:8080

### Alternative: Local Frontend (faster HMR)
```bash
just dev       # Backend + db in Docker
just frontend  # Frontend locally (separate terminal, slightly faster HMR)
```

### Local Backend (without Docker)
```bash
just db        # Start only database
just backend   # Start backend locally (separate terminal)
```

## Common Tasks

### Backend Development
- **Models**: Modify SQLModel models in `backend/app/models.py`
- **API Endpoints**: Add/modify endpoints in `backend/app/api/routes/`
- **CRUD Operations**: Update in `backend/app/crud*.py`
- **Tests**: Run with `just test-backend` or `just tb`

### Database Migrations
```bash
just migrate                    # Run migrations
just migration "Description"    # Create new migration
just migrate-rollback           # Rollback last migration
```

### Frontend Development
- **Routes/Pages**: Add in `frontend/src/routes/`
- **Components**: Create in `frontend/src/components/`
- **Hooks**: Create in `frontend/src/hooks/`
- **API Client**: Regenerate with `just generate-client` or `just generate-client-local`
- **Tests**: Run with `just test-frontend` or `just tf`

## Testing

```bash
just test              # All tests (backend + frontend)
just test-backend      # Backend tests (alias: just tb)
just test-unit         # Unit tests only (alias: just tu)
just test-acceptance   # Acceptance tests (alias: just ta)
just test-frontend     # Frontend tests (alias: just tf)
just test-e2e          # E2E tests (alias: just te)
```

## Code Quality

```bash
just lint              # Run all linters
just format            # Format all code
just pre-commit        # Run pre-commit hooks
```

## Environment Variables

Configure in `.env` file:
- `SECRET_KEY` - Generate with: `just secret`
- `FIRST_SUPERUSER` / `FIRST_SUPERUSER_PASSWORD` - Admin credentials
- `POSTGRES_PASSWORD` - Database password
- `DOMAIN` - Deployment domain (localhost for dev)
