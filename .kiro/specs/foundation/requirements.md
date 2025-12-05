# Requirements Document: Foundation

## Introduction

The Foundation feature establishes the core data structures and baseline user profile for the Fitness Copilot application. It provides the "source of truth" for meal plans, training routines, and daily activity logs, serving as the structured backbone that all AI-driven features will interact with. The system supports multi-tenant architecture where each user has isolated data.

## UI Reference

Frontend implementation should follow the design sketches in `__ignore/sketch_nano_banana.jpg` for the Monitor and Oracle views.

## Glossary

- **System**: The Fitness Copilot backend application
- **User**: An individual using the fitness tracking application
- **Tenant**: An isolated user account with separate data
- **Meal Plan**: A structured schedule of meals with nutritional information
- **Training Program**: A predefined workout routine that users can select from a menu
- **Training Routine**: The specific exercises within a selected training program
- **Daily Log**: A record of actual meals consumed and exercises performed on a given day
- **Baseline Profile**: User's physical measurements (weight, height) and fitness goal
- **Goal Method**: The user's fitness objective (cut, bulk, or maintain)

## Requirements

### Requirement 1: Tenant Management

**User Story:** As a user, I want my own isolated account, so that my fitness data remains private and separate from other users.

#### Acceptance Criteria

1. WHEN a new user registers THEN the System SHALL create a unique tenant identifier for that user
2. WHEN a user accesses their data THEN the System SHALL filter all queries by the user's tenant identifier
3. WHEN a user requests meal plans THEN the System SHALL return only meal plans associated with their tenant
4. WHEN a user requests training routines THEN the System SHALL return only routines associated with their tenant
5. WHEN a user creates logs THEN the System SHALL associate those logs with their tenant identifier

### Requirement 2: User Baseline Profile

**User Story:** As a user, I want to set my baseline physical measurements and fitness goal, so that the system can provide personalized tracking and recommendations.

#### Acceptance Criteria

1. WHEN a user creates their profile THEN the System SHALL store weight in kilograms, height in centimeters, and goal method
2. WHEN a user updates their profile THEN the System SHALL validate that weight is between 30 and 300 kilograms
3. WHEN a user updates their profile THEN the System SHALL validate that height is between 100 and 250 centimeters
4. WHERE a user has set their goal method THEN the System SHALL accept only the values cut, bulk, or maintain
5. WHEN a user retrieves their profile THEN the System SHALL return their current weight, height, goal method, and profile creation date

### Requirement 3: Meal Plan Structure

**User Story:** As a user, I want my meal plans loaded from structured data, so that I have a clear nutritional roadmap for each day.

#### Acceptance Criteria

1. WHEN the System starts THEN the System SHALL load meal plan data from CSV files into the database
2. WHEN a meal plan entry is stored THEN the System SHALL include user identifier, day of week, meal type, item name, calories, protein, carbohydrates, and fat
3. WHEN a user requests today's meal plan THEN the System SHALL return all meal entries matching the current day of week for that user
4. WHEN meal plan data is loaded THEN the System SHALL validate that calorie values are non-negative integers
5. WHEN meal plan data is loaded THEN the System SHALL validate that macronutrient values (protein, carbs, fat) are non-negative numbers

### Requirement 4: Training Program Selection

**User Story:** As a user, I want to choose from predefined training programs, so that I can quickly start following a structured workout plan without manual configuration.

#### Acceptance Criteria

1. WHEN the System starts THEN the System SHALL provide between 3 and 6 predefined training programs
2. WHEN a user views available programs THEN the System SHALL display program name, description, training days per week, and difficulty level
3. WHEN a user selects a training program THEN the System SHALL associate that program with the user's profile
4. WHERE a user has selected a training program THEN the System SHALL load the corresponding exercise routines for each training day
5. WHEN a user requests today's training routine THEN the System SHALL return exercises from their selected program matching the current day of week

### Requirement 5: Training Routine Structure

**User Story:** As a user, I want my training routines defined by my selected program, so that I have a clear exercise plan for each day.

#### Acceptance Criteria

1. WHEN a training routine entry is stored THEN the System SHALL include program identifier, day of week, exercise name, machine hint, sets, reps, and target load
2. WHEN training routine data is loaded THEN the System SHALL validate that sets and reps are positive integers
3. WHEN training routine data is loaded THEN the System SHALL validate that target load is a non-negative number
4. WHEN a user switches programs THEN the System SHALL update their active routine to reflect the new program's exercises
5. WHEN a user has no selected program THEN the System SHALL return an empty routine for today

### Requirement 6: Daily Activity Logging

**User Story:** As a user, I want to manually log meals and exercises, so that I can track my actual adherence to my plans.

#### Acceptance Criteria

1. WHEN a user logs a meal THEN the System SHALL store the meal name, calories, protein, carbohydrates, fat, meal type, and timestamp
2. WHEN a user logs an exercise THEN the System SHALL store the exercise name, sets performed, reps performed, weight used, and timestamp
3. WHEN a user requests today's logs THEN the System SHALL return all meal logs and exercise logs created on the current date for that user
4. WHEN a meal log is created THEN the System SHALL validate that calorie and macronutrient values are non-negative
5. WHEN an exercise log is created THEN the System SHALL validate that sets, reps, and weight are non-negative

### Requirement 7: Daily Summary Calculations

**User Story:** As a user, I want to see my daily progress metrics, so that I can understand how I'm tracking against my goals.

#### Acceptance Criteria

1. WHEN a user requests today's summary THEN the System SHALL calculate total calories consumed from all meal logs
2. WHEN a user requests today's summary THEN the System SHALL calculate total protein consumed from all meal logs
3. WHEN a user requests today's summary THEN the System SHALL calculate the number of exercises completed from all exercise logs
4. WHEN a user requests today's summary THEN the System SHALL calculate calories remaining by subtracting consumed from planned
5. WHEN a user requests today's summary THEN the System SHALL return all calculated metrics in a single response
