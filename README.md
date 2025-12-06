# Fitness Copilot 🧟‍♂️

**🎃 Kiroween 2025**

> What if you could snap a photo of your meal or workout and get instant, context-aware feedback? Not just "that's 500 calories" but "you've got 600 left for today, and your leg workout is still pending."

## What It Does

Fitness Copilot is an AI-powered fitness tracking app that combines:

- **Vision-based logging**: Snap a photo of your meal or exercise, and Google Gemini Vision analyzes it
- **Voice input**: Speak your food or exercise logs instead of typing (browser-native Web Speech API)
- **Context-aware coaching**: The AI knows your training plan, today's progress, and recent conversation before responding
- **Validated tracking**: All data is validated before being stored—the AI proposes, the system validates
- **Dual interface**:
  - **Monitor**: A _typical_ dashboard for tracking metrics.
  - **Chat**: An interactive chat interface for text, voice, and image input.

The system doesn't just track—it understands your full situation and provides personalized guidance.

## How It Works

The key innovation is **context injection**: before every AI request, we inject the user's training plan, today's progress, and recent conversation. The AI doesn't just see a photo—it understands the full situation.

- **AI Vision** (understands images) → **Validation Layer** (enforces rules) → **Database** (stores facts)
- **Chat** (adaptive, conversational) ↔️ **Monitor** (structured metrics)

→ See [ARCHITECTURE.md](./ARCHITECTURE.md) for detailed flow diagrams.

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

## Architecture

See [ARCHITECTURE.md](./ARCHITECTURE.md) for detailed documentation including:

- System overview and component diagrams
- Chat message flow (text → LLM → validation → database)
- Voice input flow (speech → Web Speech API → same text flow)
- Vision flow (image → classification → analysis → validation)
- Context building and prompt architecture

## Documentation

- [Architecture Guide](./ARCHITECTURE.md) - System design and data flows
