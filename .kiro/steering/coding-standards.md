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
- **CRUD**: Database operations in `backend/app/crud.py`
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

This project uses a **three-tier testing philosophy** based on Google's Small/Medium/Large sizing:
[https://testing.googleblog.com/2010/12/test-sizes.html](https://testing.googleblog.com/2010/12/test-sizes.html)

### Test Tiers

| Type            | Size   | Network   | Database | External APIs | Typical Time |
|-----------------|--------|-----------|----------|---------------|--------------|
| **Unit**        | Small  | No        | No       | No            | ≤ 30s suite  |
| **Integration** | Medium | Localhost | Yes      | Mocked        | ≤ 150s suite |
| **E2E**         | Large  | Yes       | Yes      | Yes           | 300+ s       |

- **Unit**: Pure logic in isolation; heavy mocking; deterministic; fastest feedback
- **Integration**: End-to-end through our stack (API/DB) but mocks external HTTP
- **E2E**: Full browser-based tests with Playwright; exercises real user flows

### Backend Tests
- Use pytest for all tests
- Test files in `backend/app/tests/`
- Organize by tier: `tests/unit/`, `tests/integration/`
- Use pytest markers: `@pytest.mark.unit`, `@pytest.mark.integration`
- Include unit tests for CRUD operations and business logic
- Include integration tests for API endpoints
- Aim for high test coverage (≥ 50% gate in CI)

### Frontend Tests
- Use Playwright for E2E tests
- Test critical user flows
- Test files in `frontend/tests/`
- Run tests against Docker stack

### What Runs in CI
1. **Unit tests** → must pass (blocks merge)
2. **Integration tests** → must pass (blocks merge)
3. **E2E tests** → runs with `continue-on-error: true` (non-blocking due to flakiness)

## Git Workflow
- Use descriptive commit messages
- Run pre-commit hooks before committing
- Keep commits focused and atomic
- Reference issues in commit messages when applicable
