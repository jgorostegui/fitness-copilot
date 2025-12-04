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

### Backend Tests
- Use pytest for all tests
- Test files in `backend/app/tests/`
- Include unit tests for CRUD operations
- Include integration tests for API endpoints
- Aim for high test coverage

### Frontend Tests
- Use Playwright for E2E tests
- Test critical user flows
- Test files in `frontend/tests/`
- Run tests against Docker stack

## Git Workflow
- Use descriptive commit messages
- Run pre-commit hooks before committing
- Keep commits focused and atomic
- Reference issues in commit messages when applicable
