# Requirements Document

## Introduction

The Smart Assistant feature transforms the Fitness Copilot from a simple logging tool into a context-aware personal fitness assistant. The assistant maintains rich context about the user's profile, preferences, current day status, and conversation history to provide personalized, relevant responses. This feature also introduces realistic demo data with weekly meal plans, improved vision UX with explicit tracking confirmation, and enhanced chat interactions.

## Glossary

- **Context**: The combined state of user profile, preferences, daily progress, meal/exercise plans, and recent chat history used to personalize assistant responses
- **Smart_Assistant**: The AI-powered chat interface that processes user messages with full context awareness
- **Tracking**: The act of logging a meal or exercise to the user's daily records
- **Quick_Add**: Pre-configured meal buttons for fast logging of common dishes
- **Form_Tips**: Exercise technique guidance provided on-demand for gym equipment
- **Weekly_Plan**: A 7-day meal plan template assigned to each user
- **Current_Day**: The simulated day of the week for demo purposes (can be changed by user)
- **Demo_Persona**: Pre-configured user profiles with distinct characteristics and meal plans

## Requirements

### Requirement 1: Context Management

**User Story:** As a user, I want the assistant to remember my profile, preferences, and current progress, so that responses are personalized and relevant to my situation.

#### Acceptance Criteria

1. WHEN the assistant processes a message THEN the Smart_Assistant SHALL include user profile data (weight, height, goal phase, activity level) in the context
2. WHEN the assistant processes a message THEN the Smart_Assistant SHALL include the current day's meal and exercise logs in the context
3. WHEN the assistant processes a message THEN the Smart_Assistant SHALL include the user's weekly meal plan for the simulated day in the context
4. WHEN the assistant processes a message THEN the Smart_Assistant SHALL include the last 10 chat messages (text content only, excluding attachment payloads) in the context
5. WHEN building context for one user THEN the Smart_Assistant SHALL exclude all data belonging to other users (tenant isolation)
6. WHEN the assistant generates a response THEN the Smart_Assistant SHALL reference the user's current progress (e.g., "You've had 1200 of your 2000 kcal target")
7. WHEN including chat history in context THEN the Smart_Assistant SHALL exclude base64 image data and attachment URLs to prevent token bloat

### Requirement 2: Vision UX Enhancement

**User Story:** As a user, I want to preview food/exercise analysis before tracking, so that I can review and confirm what gets logged.

#### Acceptance Criteria

1. WHEN a user uploads an image THEN the Smart_Assistant SHALL analyze and display results without automatically adding to tracking
2. WHEN displaying food analysis THEN the Smart_Assistant SHALL show an "Add to Track" button
3. WHEN displaying exercise analysis THEN the Smart_Assistant SHALL show an "Add to Track" button
4. WHEN the user clicks "Add to Track" THEN the Smart_Assistant SHALL create the corresponding log entry using the message_id reference
5. WHEN displaying gym equipment analysis THEN the Smart_Assistant SHALL hide form tips in the initial response but store them in action_data
6. WHEN the user requests "form tips" THEN the Smart_Assistant SHALL retrieve tips from the stored action_data and inject a local message without LLM call
7. WHEN storing vision analysis THEN the Smart_Assistant SHALL use the ChatMessage.action_data JSON column (no separate table)

### Requirement 3: Realistic Quick Add Options

**User Story:** As a user, I want quick add buttons with realistic meal options, so that I can log common dishes efficiently.

#### Acceptance Criteria

1. WHEN displaying the Kitchen mode widget THEN the Smart_Assistant SHALL show quick add buttons with complete dish names (not single ingredients)
2. WHEN a quick add button is pressed THEN the Smart_Assistant SHALL log the meal with realistic macro values
3. WHEN displaying quick add options THEN the Smart_Assistant SHALL include at least 4 realistic meal options (e.g., "Grilled Chicken Salad", "Oatmeal with Berries")

### Requirement 4: Weekly Meal Plans

**User Story:** As a user, I want to see my meal plan for the entire week, so that I can plan ahead and track adherence.

#### Acceptance Criteria

1. WHEN a demo user is created THEN the Smart_Assistant SHALL assign a complete weekly meal plan (7 days)
2. WHEN displaying the meal plan THEN the Smart_Assistant SHALL show meals for the current day by default
3. WHEN the user changes the current day THEN the Smart_Assistant SHALL update the displayed meal plan accordingly
4. WHEN querying meal plans THEN the Smart_Assistant SHALL filter by user_id and day_of_week

### Requirement 5: Demo Persona Differentiation

**User Story:** As a demo user, I want each persona to have distinct characteristics and plans, so that I can experience different fitness scenarios.

#### Acceptance Criteria

1. WHEN creating the "cut" demo persona THEN the Smart_Assistant SHALL assign a 6-day training program with a calorie-deficit meal plan
2. WHEN creating the "bulk" demo persona THEN the Smart_Assistant SHALL assign a 4-day training program with a calorie-surplus meal plan
3. WHEN creating the "maintain" demo persona THEN the Smart_Assistant SHALL assign a 3-day training program with a maintenance meal plan
4. WHEN creating demo personas THEN the Smart_Assistant SHALL pre-populate weekly meal plans without requiring user input
5. WHEN displaying demo persona options THEN the Smart_Assistant SHALL show distinct descriptions highlighting the differences

### Requirement 6: Current Day Simulation

**User Story:** As a demo user, I want to change the simulated current day, so that I can test different scenarios in the weekly plan.

#### Acceptance Criteria

1. WHEN the user views the dashboard THEN the Smart_Assistant SHALL display the current simulated day
2. WHEN the user selects a different day THEN the Smart_Assistant SHALL update the displayed meal plan and training routine targets
3. WHEN logging meals or exercises THEN the Smart_Assistant SHALL use the real UTC timestamp for logged_at (not the simulated day)
4. WHEN displaying daily progress THEN the Smart_Assistant SHALL show real logs but compare against simulated day's targets
5. WHEN building LLM context THEN the Smart_Assistant SHALL use the simulated day for meal plan and training routine context

### Requirement 7: Chat-Driven Assistant Behavior

**User Story:** As a user, I want the assistant to behave like a knowledgeable fitness coach, so that I get helpful guidance beyond simple logging.

#### Acceptance Criteria

1. WHEN the user asks a fitness-related question THEN the Smart_Assistant SHALL provide a contextual answer using the user's profile and progress
2. WHEN the user logs a meal THEN the Smart_Assistant SHALL provide feedback relative to daily targets (e.g., "Great choice! You're at 60% of your protein goal")
3. WHEN the user logs an exercise THEN the Smart_Assistant SHALL acknowledge progress toward the training plan
4. WHEN the user's message does not match food or exercise patterns THEN the Smart_Assistant SHALL attempt to provide helpful fitness guidance using LLM

### Requirement 8: Context Privacy (Tenant Isolation)

**User Story:** As a user, I want my data to remain private, so that other users cannot see my information.

#### Acceptance Criteria

1. WHEN building context for user A THEN the Smart_Assistant SHALL exclude all chat messages from user B
2. WHEN building context for user A THEN the Smart_Assistant SHALL exclude all meal logs from user B
3. WHEN building context for user A THEN the Smart_Assistant SHALL exclude all exercise logs from user B
4. WHEN building context for user A THEN the Smart_Assistant SHALL exclude profile data from user B
5. WHEN a context query is executed THEN the Smart_Assistant SHALL include user_id filter in all database queries
