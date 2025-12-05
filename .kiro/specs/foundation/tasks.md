# Implementation Plan: Foundation

This implementation plan breaks down the Foundation feature into incremental, testable tasks. Each task builds on previous work and references specific requirements from the requirements document.

## Task List

- [x] 1. Set up enhanced data models and database schema
  - Create SQLModel classes for User, TrainingProgram, TrainingRoutine, MealPlan, MealLog, ExerciseLog
  - Include all enhanced fields: age, sex, body_fat_percentage, activity_level, goal_weight_kg, macro preferences
  - Add enums for GoalMethod (9 options) and ActivityLevel (5 levels)
  - Create Alembic migration for all tables with proper indexes and foreign keys
  - _Requirements: 1.1, 2.1, 3.1, 4.1, 5.1, 6.1_

- [x] 1.1 Write property test for user profile validation
  - **Property 2: Profile validation bounds**
  - **Validates: Requirements 2.2, 2.3**

- [x] 1.2 Write property test for goal method enumeration
  - **Property 3: Goal method enumeration**
  - **Validates: Requirements 2.4**

- [x] 2. Implement calculation services for body and energy metrics
  - Create `CalculationService` class with methods for BMI, FFM, fat mass, BMR (both equations), TDEE, NEAT, deficit, EA
  - Implement Mifflin-St Jeor BMR formula (without body fat)
  - Implement Katch-McArdle BMR formula (with body fat)
  - Calculate activity multipliers based on ActivityLevel enum
  - Calculate Energy Availability (EA) with status thresholds
  - Calculate weekly and monthly projections
  - _Requirements: 2.5, 7.1, 7.2, 7.3, 7.4, 7.5_

- [x] 2.1 Write property test for BMI calculation
  - **Property 2: Profile validation bounds** (BMI component)
  - **Validates: Requirements 2.2, 2.3**

- [x] 2.2 Write property test for summary calculation accuracy
  - **Property 9: Summary calculation accuracy**
  - **Validates: Requirements 7.1, 7.4**

- [x] 3. Create CSV import service for training programs and meal plans
  - Implement `CSVImportService` class
  - Create method to load 3-6 predefined training programs from CSV
  - Create method to load training routines (exercises) for each program
  - Create method to load default meal plan templates from CSV
  - Add validation for CSV data (positive integers for sets/reps, non-negative for calories/macros)
  - Wire CSV loading into FastAPI lifespan event
  - _Requirements: 3.1, 3.4, 3.5, 4.1, 4.2, 5.2, 5.3_

- [ ]* 3.1 Write property test for training program availability
  - **Property 4: Training program availability**
  - **Validates: Requirements 4.1**

- [ ]* 3.2 Write property test for non-negative validation
  - **Property 8: Non-negative validation for logs**
  - **Validates: Requirements 6.4, 6.5**

- [x] 4. Implement profile management endpoints
  - Create `GET /api/v1/profile/me` endpoint returning UserProfilePublic schema
  - Create `PUT /api/v1/profile/me` endpoint accepting UserProfileUpdate schema
  - Create `GET /api/v1/profile/me/metrics` endpoint returning calculated BodyMetrics, EnergyMetrics, EnergyAvailability, WeeklySummary
  - Use `get_current_user` dependency for authentication
  - Ensure tenant isolation (user can only access their own profile)
  - _Requirements: 1.2, 2.1, 2.2, 2.3, 2.4, 2.5_

- [ ]* 4.1 Write property test for tenant isolation
  - **Property 1: Tenant isolation**
  - **Validates: Requirements 1.2, 1.3, 1.4**

- [x] 5. Configure multi-tenant database filtering
  - Create `get_current_tenant` dependency that extracts user_id from JWT token
  - Implement `TenantFilterMixin` or base query helper that automatically filters by user_id
  - Add tenant_id (user_id) foreign key constraints to MealPlan, MealLog, ExerciseLog tables
  - Create reusable CRUD functions that enforce tenant isolation on all queries
  - Ensure all SELECT, UPDATE, DELETE operations include tenant filter
  - Add database-level row security policies if using PostgreSQL (optional enhancement)
  - _Requirements: 1.1, 1.2, 1.3, 1.4, 1.5_

- [x] 6. Implement training program endpoints
  - Create `GET /api/v1/programs` endpoint returning list of available TrainingProgram
  - Create `POST /api/v1/programs/{program_id}/select` endpoint to associate program with user
  - Create `GET /api/v1/plans/training/today` endpoint returning today's exercises from selected program
  - Filter routines by current day of week (0=Monday, 6=Sunday)
  - Return empty list if user has no selected program
  - _Requirements: 4.1, 4.2, 4.3, 4.4, 4.5, 5.4, 5.5_

- [ ]* 6.1 Write property test for program selection association
  - **Property 5: Program selection association**
  - **Validates: Requirements 4.3**

- [ ]* 6.2 Write property test for routine filtering by program
  - **Property 6: Routine filtering by program**
  - **Validates: Requirements 4.4, 4.5**

- [ ]* 6.3 Write property test for empty routine for unselected program
  - **Property 7: Empty routine for unselected program**
  - **Validates: Requirements 5.5**

- [x] 7. Implement meal plan endpoints
  - Create `GET /api/v1/plans/meal/today` endpoint returning today's meal plan
  - Filter meal plans by user_id and current day of week
  - Ensure tenant isolation (only return plans for authenticated user)
  - _Requirements: 1.3, 3.2, 3.3_

- [x] 8. Implement daily logging endpoints
  - Create `POST /api/v1/logs/meal` endpoint accepting MealLogCreate schema
  - Create `POST /api/v1/logs/exercise` endpoint accepting ExerciseLogCreate schema
  - Create `GET /api/v1/logs/today` endpoint returning DailyLogsResponse with both meal and exercise logs
  - Filter logs by user_id and current date
  - Validate non-negative values for all numeric fields
  - Associate logs with authenticated user's tenant
  - _Requirements: 1.5, 6.1, 6.2, 6.3, 6.4, 6.5_

- [ ]* 8.1 Write property test for log timestamp ordering
  - **Property 10: Log timestamp ordering**
  - **Validates: Requirements 6.3**

- [x] 9. Implement daily summary endpoint
  - Create `GET /api/v1/summary/today` endpoint returning DailySummary
  - Calculate total calories consumed from meal logs
  - Calculate total protein consumed from meal logs
  - Calculate number of exercises completed from exercise logs
  - Calculate calories remaining (target - consumed)
  - Calculate protein remaining (target - consumed)
  - Use CalculationService to get target values based on user profile
  - _Requirements: 7.1, 7.2, 7.3, 7.4, 7.5_

- [x] 10. Create sample CSV data files
  - Create `data/programs.csv` with 3-6 training programs (beginner, intermediate, advanced)
  - Create `data/routines.csv` with exercises for each program and day of week
  - Create `data/meal_plans.csv` with default meal plan templates
  - Include variety: full body, upper/lower split, push/pull/legs programs
  - _Requirements: 3.1, 4.1, 4.2_

- [x] 11. Configure Pydantic for frontend compatibility
  - Add alias generator to convert snake_case to camelCase in JSON responses
  - Configure datetime serialization to ISO 8601 format
  - Ensure numeric IDs are serialized as strings where frontend expects them
  - Test response format matches TypeScript interfaces in `.kiro/frontend-frankenstein-fitness-copilot/types.ts`
  - _Requirements: All (frontend integration)_

- [x] 12. Checkpoint - Ensure all tests pass
  - Ensure all tests pass, ask the user if questions arise.
