# Requirements Document: Conversational Core

## Introduction

This specification covers the implementation of a demo-friendly fitness copilot application that combines the foundation (Slice 1), chat system (Slice 2), text-to-logging (Slice 3), and a new demo mode that allows showcasing the app without authentication complexity. The demo mode enables instant access to pre-configured demo users, making it easy to demonstrate multi-user chat and logging functionality.

## Glossary

- **Demo Mode**: A special operational mode enabled in local/development environments that bypasses JWT authentication for demo users
- **Demo User**: Pre-seeded user accounts (demo1, demo2, demo3) with pre-configured profiles for demonstration purposes
- **Brain Service**: The backend service that processes chat messages and routes them to appropriate handlers (food logging, exercise logging, general response)
- **Chat Message**: A single message in the Oracle chat, either from user or assistant
- **Action Type**: The type of action triggered by a chat message (log_food, log_exercise, none)
- **Tenant Isolation**: Security mechanism ensuring users can only access their own data

## Requirements

### Requirement 1: Demo Mode Infrastructure

**User Story:** As a developer/presenter, I want to quickly demonstrate the app with pre-filled demo users, so that I can showcase the onboarding flow without typing.

#### Acceptance Criteria

1. WHEN the environment is "local" THEN the System SHALL expose `POST /api/v1/demo/login/{persona}` endpoint where persona is "cut", "bulk", or "maintain"
2. WHEN a demo login is requested AND the user does not exist THEN the System SHALL create them with the persona's physical attributes AND set `onboarding_complete = False`
3. WHEN a demo login is requested AND the user exists THEN the System SHALL return the auth token immediately
4. WHEN the environment is NOT "local" THEN the System SHALL return 404 for demo endpoints
5. WHEN the environment is "local" THEN the System SHALL expose `GET /api/v1/demo/users` endpoint listing available personas

### Requirement 2: Demo User Profiles (Pre-filled but Not Complete)

**User Story:** As a presenter, I want demo users to have pre-filled profiles but require onboarding confirmation, so that I can demonstrate the onboarding flow.

#### Acceptance Criteria

1. WHEN "cut" persona is created THEN the System SHALL configure them with (male, 85kg, 180cm, standard_cut goal, moderately_active) AND onboarding_complete=False
2. WHEN "bulk" persona is created THEN the System SHALL configure them with (male, 90kg, 185cm, moderate_gain goal, very_active) AND onboarding_complete=False
3. WHEN "maintain" persona is created THEN the System SHALL configure them with (female, 60kg, 165cm, maintenance goal, lightly_active) AND onboarding_complete=False
4. WHEN a demo user is created THEN the System SHALL assign them a training program
5. WHEN onboarding is completed THEN the System SHALL set onboarding_complete=True via `PUT /profile/me`

### Requirement 3: Chat Message Storage

**User Story:** As a user, I want my chat messages to be saved, so that I can see my conversation history when I return.

#### Acceptance Criteria

1. WHEN a chat message is created THEN the System SHALL store id, user_id, role, content, action_type, action_data, and created_at
2. WHEN storing a chat message THEN the System SHALL associate it with the authenticated user's tenant
3. WHEN a user requests chat history THEN the System SHALL return only messages belonging to that user
4. WHEN returning chat messages THEN the System SHALL order them by created_at ascending
5. WHEN a user is deleted THEN the System SHALL cascade delete all their chat messages

### Requirement 4: Chat API Endpoints

**User Story:** As a frontend developer, I want chat API endpoints with multimodal support, so that I can build the Oracle chat interface with image/audio attachments.

#### Acceptance Criteria

1. WHEN a client calls `GET /api/v1/chat/messages` THEN the System SHALL return the user's chat history with optional limit parameter
2. WHEN a client calls `POST /api/v1/chat/messages` with content THEN the System SHALL process the message and return an assistant response
3. WHEN processing a chat message THEN the System SHALL store both the user message and assistant response
4. WHEN returning chat messages THEN the System SHALL serialize using camelCase for frontend compatibility
5. WHEN a client calls `POST /api/v1/chat/messages` THEN the System SHALL accept optional `attachment_type` (image, audio, none) and `attachment_url` fields

### Requirement 5: Brain Service - Food Parsing

**User Story:** As a user, I want to log food by typing naturally, so that I can track meals without filling forms.

#### Acceptance Criteria

1. WHEN a message contains food keywords (ate, eaten, had, breakfast, lunch, dinner, snack) THEN the Brain Service SHALL attempt food parsing
2. WHEN a known food is detected (banana, chicken, rice, eggs, oats, salmon, broccoli, apple, bread, milk) THEN the Brain Service SHALL return action_type=log_food with macro data
3. WHEN food is successfully parsed THEN the System SHALL create a MealLog record for the user
4. WHEN food is logged via chat THEN the assistant response SHALL confirm what was logged with calories and protein
5. WHEN an unknown food is mentioned THEN the Brain Service SHALL fall back to general response
6. WHEN a message has attachment_type=image THEN the Brain Service SHALL return a hardcoded "Vision Analysis" response (e.g., "I see what looks like a healthy meal! For now, tell me what you ate and I'll log it.")

### Requirement 6: Brain Service - Exercise Parsing

**User Story:** As a user, I want to log exercises by typing naturally, so that I can track workouts conversationally.

#### Acceptance Criteria

1. WHEN a message contains exercise keywords (bench, squat, deadlift, press, row, curl, sets, reps, kg, lbs) THEN the Brain Service SHALL attempt exercise parsing
2. WHEN exercise is detected THEN the Brain Service SHALL extract sets, reps, and weight using pattern matching
3. WHEN sets/reps/weight are not specified THEN the System SHALL use defaults (3 sets, 10 reps, 0 kg)
4. WHEN exercise is successfully parsed THEN the System SHALL create an ExerciseLog record for the user
5. WHEN exercise is logged via chat THEN the assistant response SHALL confirm the logged exercise details
6. WHEN a message has attachment_type=audio THEN the Brain Service SHALL return a hardcoded "Voice Analysis" response (e.g., "I heard your voice note! For now, type what you said and I'll log it.")

### Requirement 7: Brain Service - General Response and Reset

**User Story:** As a user, I want helpful responses when my message isn't a logging command, so that I understand what the system can do.

#### Acceptance Criteria

1. WHEN a message does not match food or exercise patterns THEN the Brain Service SHALL return a general helpful response
2. WHEN returning a general response THEN the System SHALL set action_type=none
3. WHEN returning a general response THEN the assistant SHALL suggest example commands the user can try
4. WHEN a message contains "reset" THEN the System SHALL delete all of today's logs for the user and return action_type=reset

### Requirement 8: Frontend Auth Flow

**User Story:** As a presenter, I want a simple demo login that shows the onboarding flow with pre-filled data, so that I can demonstrate the full user journey.

#### Acceptance Criteria

1. WHEN the frontend detects demo mode is available THEN the System SHALL show a "Demo Login" option with persona cards (Cut, Bulk, Maintain)
2. WHEN a persona card is clicked THEN the System SHALL call `POST /demo/login/{persona}` and store the returned token
3. WHEN login succeeds THEN the System SHALL fetch profile via `GET /profile/me` and check onboarding_complete
4. WHEN onboarding_complete is False THEN the System SHALL redirect to the Onboarding screen
5. WHEN onboarding_complete is True THEN the System SHALL redirect to the Dashboard

### Requirement 9: Frontend Onboarding Pre-fill

**User Story:** As a presenter, I want the onboarding form to be pre-filled with demo data, so that I can just click "Start Journey" without typing.

#### Acceptance Criteria

1. WHEN the Onboarding screen loads THEN the System SHALL call `GET /profile/me` to fetch current profile data
2. WHEN profile data is received THEN the System SHALL pre-fill all form inputs with the existing values
3. WHEN the user clicks "Start Journey" THEN the System SHALL call `PUT /profile/me` with onboarding_complete=True
4. WHEN onboarding is completed THEN the System SHALL redirect to the Dashboard

### Requirement 10: Frontend Chat Integration

**User Story:** As a user, I want to chat with the fitness brain, so that I can log food and exercises conversationally.

#### Acceptance Criteria

1. WHEN the Oracle tab is opened THEN the System SHALL fetch and display chat history
2. WHEN a message is sent THEN the System SHALL display it immediately and show a typing indicator
3. WHEN an assistant response is received THEN the System SHALL display it with appropriate styling
4. WHEN a response has action_type=log_food or log_exercise THEN the System SHALL show an action confirmation card
5. WHEN food or exercise is logged via chat THEN the Monitor tab SHALL update automatically (optimistic or invalidation-based)

### Requirement 11: Data Consistency (The Frankenstein Loop)

**User Story:** As a user, I want my logged data to be consistent across views, so that Monitor and Oracle show the same information.

#### Acceptance Criteria

1. WHEN food is logged via chat THEN the Monitor dashboard calories SHALL update automatically
2. WHEN exercise is logged via chat THEN the Monitor dashboard workouts_completed SHALL update automatically
3. WHEN "reset" is sent via chat THEN the Monitor dashboard SHALL reset to zero for today
4. WHEN the same data is viewed in Monitor and Oracle THEN the values SHALL match
