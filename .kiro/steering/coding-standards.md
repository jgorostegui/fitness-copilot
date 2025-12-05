# Coding Standards

## Backend (Python/FastAPI)

### Style Guide
- Follow PEP 8 conventions
- Use type hints for all function parameters and return values
- Use Ruff for linting and formatting
- Maximum line length: handled by Ruff

### Code Organization
- **Models**: SQLModel classes in `backend/app/models.py`
- **Schemas**: Pydantic models for request/response validation
- **API Routes**: Organized by resource in `backend/app/api/routes/`
- **CRUD**: Database operations split by concern:
  - `crud.py` - User/auth operations
  - `crud_fitness.py` - Training programs, exercise logs
  - `crud_nutrition.py` - Meal plans, meal logs
- **Dependencies**: Reusable dependencies in `backend/app/api/deps.py`

### Best Practices
- Use dependency injection for database sessions and authentication
- Validate all inputs with Pydantic models
- Handle errors with appropriate HTTP exceptions
- Write tests for all endpoints
- Use async/await for database operations
- Keep business logic separate from route handlers

### Database
- Always create Alembic migrations for schema changes
- Never modify the database schema directly
- Use SQLModel for ORM operations
- Include proper indexes for query performance

## Frontend (React/TypeScript)

### Style Guide
- Use TypeScript for all files
- Use Biome for linting and formatting
- Prefer functional components with hooks
- Use meaningful component and variable names

### Code Organization
- **Routes**: Page components in `frontend/src/routes/`
- **Components**: Reusable UI in `frontend/src/components/`
- **Hooks**: Custom hooks in `frontend/src/hooks/`
- **Client**: Generated API client in `frontend/src/client/`

### Best Practices
- Use TanStack Query for data fetching and caching
- Use TanStack Router for type-safe routing
- Leverage Chakra UI components for consistency
- Handle loading and error states properly
- Use React Hook Form for form management
- Keep components small and focused
- Extract reusable logic into custom hooks

### API Integration
- Always use the generated OpenAPI client
- Regenerate client after backend API changes
- Handle API errors gracefully with error boundaries

## Testing

This project uses Google's **Small/Medium/Large** test sizing philosophy.

Reference: [Test Sizes - Google Testing Blog](https://testing.googleblog.com/2010/12/test-sizes.html)

### Test Sizes (Google's Definition)

| Feature              | Small (Unit)     | Medium (Integration) | Large (E2E)      |
|----------------------|------------------|----------------------|------------------|
| Network access       | No               | localhost only       | Yes              |
| Database             | No               | Yes                  | Yes              |
| File system access   | No               | Yes                  | Yes              |
| External systems     | No               | Discouraged          | Yes              |
| Multiple threads     | No               | Yes                  | Yes              |
| Sleep statements     | No               | Yes                  | Yes              |
| Time limit (seconds) | 60               | 300                  | 900+             |

### Our Test Tiers

- **Unit** (`@pytest.mark.unit`): Pure logic in isolation; heavy mocking; deterministic; fastest feedback. No DB, no network.
- **Acceptance** (`@pytest.mark.acceptance`): API + DB communication via TestClient. Mocks external HTTP. Localhost only.
- **Integration** (`@pytest.mark.integration`): Live external services (Gemini API). Skipped by default, run with `RUN_INTEGRATION_TESTS=1`.

Key principle: Tests must be **isolated** and runnable in **any order** (enables parallel execution).

### Backend Tests

- Use pytest for all tests
- Test files in `backend/app/tests/`
- Organize by tier: `tests/unit/`, `tests/acceptance/`, `tests/integration/`
- Use pytest markers: `@pytest.mark.unit`, `@pytest.mark.acceptance`, `@pytest.mark.integration`
- Include unit tests for pure logic and business rules
- Include acceptance tests for API endpoints with DB
- Include integration tests for live external services (Gemini)
- Aim for high test coverage (≥ 50% gate in CI)

### Frontend Tests
- Use Playwright for E2E tests
- Test critical user flows
- Test files in `frontend/tests/`
- Run tests against Docker stack

### What Runs in CI

1. **Unit tests** → must pass (blocks merge)
2. **Acceptance tests** → must pass (blocks merge)
3. **Integration tests** → skipped by default (live external services)
4. **E2E tests** → runs with `continue-on-error: true` (non-blocking due to flakiness)

## Git Workflow
- Use descriptive commit messages
- Run pre-commit hooks before committing
- Keep commits focused and atomic
- Reference issues in commit messages when applicable
