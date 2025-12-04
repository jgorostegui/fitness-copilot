# Project Overview

This is a Full Stack FastAPI Template for building modern web applications.

## Tech Stack

### Backend
- **FastAPI** - Python web framework for building APIs
- **SQLModel** - SQL database ORM with Pydantic integration
- **PostgreSQL** - SQL database
- **Alembic** - Database migrations
- **Pydantic** - Data validation and settings
- **JWT** - Authentication with JSON Web Tokens
- **uv** - Python package manager

### Frontend
- **React 18** - UI library with TypeScript
- **Vite** - Build tool and dev server
- **TanStack Query** - Data fetching and caching
- **TanStack Router** - Type-safe routing
- **Chakra UI** - Component library
- **Playwright** - End-to-end testing

### Infrastructure
- **Docker Compose** - Container orchestration
- **Traefik** - Reverse proxy and load balancer
- **GitHub Actions** - CI/CD pipelines

## Project Structure

```
├── backend/          # FastAPI backend application
│   ├── app/         # Main application code
│   ├── scripts/     # Utility scripts
│   └── alembic/     # Database migrations
├── frontend/        # React frontend application
│   ├── src/         # Source code
│   └── tests/       # Playwright tests
├── scripts/         # Project-level scripts
└── docker-compose.yml
```

## Key Features

- Secure password hashing and JWT authentication
- Email-based password recovery
- Automatic OpenAPI client generation
- Docker-based development and deployment
- Pre-configured CI/CD with GitHub Actions
- Dark mode support
- Admin dashboard with user management
