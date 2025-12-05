# Development Workflow

## Getting Started

### Start Development Environment
```bash
docker compose watch
```

This starts all services with hot-reload enabled:
- Frontend: http://localhost:5173
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs
- Adminer (DB): http://localhost:8080

### Local Development (without Docker)

**Backend:**
```bash
cd backend
uv sync                          # Install dependencies
uv run fastapi dev app/main.py   # Start dev server
```

**Frontend:**
```bash
cd frontend
npm install                      # Install dependencies
npm run dev                      # Start dev server
```

## Common Tasks

### Backend Development
- **Models**: Modify SQLModel models in `backend/app/models.py`
- **API Endpoints**: Add/modify endpoints in `backend/app/api/`
- **CRUD Operations**: Update utils in `backend/app/crud.py`
- **Tests**: Run with `uv run pytest` or `bash ./scripts/test.sh`

### Database Migrations
```bash
# Inside Docker
docker compose exec backend bash
alembic revision --autogenerate -m "Description"
alembic upgrade head

# Local (from backend directory)
cd backend
uv run alembic revision --autogenerate -m "Description"
uv run alembic upgrade head
```

### Frontend Development
- **Routes/Pages**: Add in `frontend/src/routes/`
- **Components**: Create in `frontend/src/components/`
- **API Client**: Regenerate with `./scripts/generate-client.sh`
- **Tests**: Run with `npx playwright test`

## Code Quality

### Pre-commit Hooks
```bash
uv run pre-commit install        # Install hooks
uv run pre-commit run --all-files  # Run manually
```

### Linting
- **Backend**: Uses Ruff (configured in pyproject.toml)
- **Frontend**: Uses Biome (configured in biome.json)

## Environment Variables

Configure in `.env` file:
- `SECRET_KEY` - Generate with: `python -c "import secrets; print(secrets.token_urlsafe(32))"`
- `FIRST_SUPERUSER` / `FIRST_SUPERUSER_PASSWORD` - Admin credentials
- `POSTGRES_PASSWORD` - Database password
- `DOMAIN` - Deployment domain (localhost for dev)
