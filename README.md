# Fitness Copilot

AI-powered fitness and nutrition tracking application built with FastAPI and React.

## Tech Stack

| Layer | Technology |
|-------|------------|
| Backend | FastAPI, SQLModel, PostgreSQL, Alembic |
| Frontend | React 18, TypeScript, Chakra UI, TanStack Router/Query |
| AI | Google Gemini |
| Infrastructure | Docker Compose, Traefik |

## Quick Start

```bash
just dev        # Start backend + db (hot-reload)
just frontend   # Optional: Run in 2nd terminal for frontend hot-reload
```

## Local URLs

| Service | URL |
|---------|-----|
| Frontend | <http://localhost:5173> |
| Backend API | <http://localhost:8000> |
| API Docs (Swagger) | <http://localhost:8000/docs> |
| Adminer (DB) | <http://localhost:8080> |
| MailCatcher | <http://localhost:1080> |

## Development Workflows

### Standard (Recommended)

```bash
just dev
```

Backend + database with hot-reload. Frontend serves static files.

### Full Hot-Reload

```bash
# Terminal 1
just dev

# Terminal 2
just frontend
```

### Local Backend (Fastest)

```bash
# Terminal 1
just db

# Terminal 2
just backend
```

Requires Python + uv setup.

## Testing

This project uses Google's Small/Medium/Large test sizing philosophy.

| Size | Marker | Database | External Services | CI |
|------|--------|----------|-------------------|-----|
| Small | `unit` | No | No | Must pass |
| Medium | `acceptance` | Yes | Mocked | Must pass |
| Large | `integration` | Yes | Live (Gemini) | Skipped |

```bash
just test-unit         # Unit tests (no DB)
just test-acceptance   # Acceptance tests (DB required)
just test-integration  # Integration tests (live external)
just test-e2e          # E2E tests (Playwright)
```

Aliases: `just tu`, `just ta`, `just ti`, `just te`

## Common Commands

```bash
# Development
just dev              # Backend + db
just frontend         # Frontend with hot-reload
just backend          # Backend locally (no Docker)

# Testing
just test             # All tests
just tb               # Backend tests
just tf               # Frontend tests

# Code Quality
just lint             # All linters
just lint-fix         # Fix linting issues
just format           # Format code

# Database
just migrate          # Run migrations
just migration "msg"  # Create migration

# Docker
just up               # Start all services
just down             # Stop all services
just sh               # Shell into backend container
```

## Project Structure

```
├── backend/           # FastAPI backend
│   ├── app/
│   │   ├── api/       # API routes
│   │   ├── llm/       # LLM integration (Gemini)
│   │   ├── tests/     # pytest tests (unit/acceptance/integration)
│   │   ├── models.py  # SQLModel models
│   │   ├── crud*.py   # Database operations
│   │   └── main.py    # FastAPI app
│   └── alembic/       # Database migrations
├── frontend/          # React frontend
│   ├── src/
│   │   ├── components/  # UI components
│   │   ├── routes/      # Page routes
│   │   └── client/      # Generated API client
│   └── tests/           # Playwright E2E tests
└── docker-compose.yml
```

## Documentation

- [Development Guide](./development.md)
- [Deployment Guide](./deployment.md)
- [Backend README](./backend/README.md)
- [Frontend README](./frontend/README.md)
