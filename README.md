# Fitness Copilot 🧟‍♂️

**An AI-Powered Fitness App Built with Kiro SDD**

> *An AI-powered fitness copilot where computer vision and natural language are integrated with a strict database schema. Context-aware coaching meets validated data tracking.*

**🎃 Kiroween 2025**

## What Makes This Unique

We stitched together **incompatible systems** that shouldn't cooperate:

- 👁️ **Google Gemini Vision** (can say anything) → 🛡️ **Pydantic Validation** (enforces truth) → 🦴 **PostgreSQL** (stores facts)
- 🎨 **Chat** (adaptive, conversational) ↔️ 📈 **Monitor Dashboard** (rigid, mathematical) = **Split-Brain Interface**

**The system works** because of context: Before every AI request, we inject your training plan, today's progress, and recent conversation. The AI doesn't just see a leg press photo—it knows this exercise is in your plan today, you've done 3 workouts this week, and you have 600 calories left.

## Tech Stack

| Layer | Technology |
|-------|------------|
| **Backend** | FastAPI, SQLModel, PostgreSQL, Alembic |
| **Frontend** | React 18, TypeScript, Chakra UI, TanStack Router/Query |
| **AI** | Google Gemini (Vision + Chat) |
| **Development** | Kiro SDD, `.kiro/specs`, steering docs, agent hooks |
| **Infrastructure** | Docker Compose, Traefik |

## Prerequisites

- Docker and Docker Compose
- Python with [uv](https://docs.astral.sh/uv/) (for local backend workflows)
- Node.js 20+ with `fnm` or `nvm` (for local frontend workflows)

## Quick Start

1. Copy the example environment file and adjust as needed:

```bash
cp .env.example .env
```

At minimum, set:

- `PROJECT_NAME`
- `SECRET_KEY`, `FIRST_SUPERUSER`, `FIRST_SUPERUSER_PASSWORD`

LLM is disabled by default (`LLM_ENABLED=false`). To use Gemini, set `LLM_ENABLED=true` and configure `GOOGLE_API_KEY`.

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

## AI / LLM Configuration

LLM features are optional and controlled via `.env`:

- `LLM_ENABLED` – `false` to run without external AI calls (default for local work).
- `GOOGLE_API_KEY` – required when `LLM_ENABLED=true` to enable Gemini.
- `LLM_MODEL` – model name, defaults to `gemini-2.5-flash`.

When LLM is disabled, the app still runs with deterministic fallback behavior suitable for development and tests.

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

## Kiro / SDD Assets

This repo is set up for AI-assisted, spec-driven development with Kiro:

- `.kiro/specs/**` – per-feature requirements, design, and tasks documents.
- `.kiro/steering/**` – coding standards, project overview, and workflow guidance for agents.
- `.kiro/hooks/**` – optional agent hooks for linting, drift checks, and docs sync.

These files are not required to run the app, but they are useful when pairing with Kiro or other coding agents.

## Documentation

- [Development Guide](./development.md)
- [Deployment Guide](./deployment.md)
- [Backend README](./backend/README.md)
- [Frontend README](./frontend/README.md)
