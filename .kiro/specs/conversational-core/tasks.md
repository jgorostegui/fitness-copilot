# Implementation Plan: Conversational Core

## Task List

- [x] 1. Create ChatMessage model and enums
  - Add `ChatMessageRole` enum (user, assistant) to `models.py`
  - Add `ChatActionType` enum (log_food, log_exercise, reset, none) to `models.py`
  - Add `ChatAttachmentType` enum (image, audio, none) to `models.py`
  - Add `ChatMessage` SQLModel table with: id, user_id, role, content, action_type, action_data (JSON), attachment_type, attachment_url, created_at
  - Add `ChatMessageCreate` schema with optional attachment_type and attachment_url fields
  - Add `ChatMessagePublic`, `ChatMessagesPublic` schemas
  - Ensure `ChatMessagePublic` extends `CamelModel` for camelCase serialization
  - _Requirements: 3.1, 3.2, 4.5_

- [x] 2. Create Alembic migration for chat_message table
  - Create migration file for chat_message table
  - Add all columns: id, user_id, role, content, action_type, action_data, created_at
  - Add index on user_id for tenant filtering
  - Add index on created_at for ordering
  - Add foreign key to user.id with CASCADE delete
  - Run migration and verify
  - _Requirements: 3.1, 3.5_

- [x] 3. Implement chat CRUD operations
  - Create `backend/app/crud_chat.py`
  - Implement `create_chat_message(session, user_id, content, role, action_type, action_data)`
  - Implement `get_chat_messages(session, user_id, limit)` with ordering by created_at ASC
  - Ensure all queries filter by user_id (tenant isolation)
  - _Requirements: 3.2, 3.3, 3.4_

- [x] 3.1 Write property test for tenant isolation
  - **Property 2: Tenant isolation for chat messages**
  - **Validates: Requirements 3.3**

- [x] 3.2 Write property test for message ordering
  - **Property 3: Chat message ordering**
  - **Validates: Requirements 3.4**

- [x] 4. Implement BrainService with food parsing
  - Create `backend/app/services/brain.py`
  - Define `BrainResponse` dataclass with content, action_type, action_data
  - Define `FOOD_DB` dict with 10 common foods and their macros
  - Define `FOOD_KEYWORDS` set (ate, eaten, had, breakfast, lunch, dinner, snack)
  - Implement `_has_food_keywords(content)` using simple `if keyword in content.lower()` checks (no regex)
  - Implement `_parse_food(content)` using simple `if "banana" in content.lower()` checks for known foods
  - Integrate `app.llm.google.GoogleLLMProvider` for unknown foods (call `extract_json()` with food extraction prompt)
  - If LLM disabled or fails, fall back to general response
  - Return `BrainResponse` with action_type=LOG_FOOD when food found
  - _Requirements: 5.1, 5.2, 5.5_

- [x] 4.1 Write property test for food keyword detection
  - **Property 4: Food keyword detection triggers parsing**
  - **Validates: Requirements 5.1**

- [x] 4.2 Write property test for known food parsing
  - **Property 5: Known food parsing produces correct action**
  - **Validates: Requirements 5.2**

- [x] 4.3 Write property test for unknown food fallback
  - **Property 7: Unknown food falls back gracefully**
  - **Validates: Requirements 5.5**

- [x] 5. Implement BrainService with exercise parsing
  - Define `EXERCISE_MAP` dict mapping keywords to exercise names (bench, squat, deadlift, press, row, curl, pullup, dip)
  - Define `EXERCISE_KEYWORDS` set for detection
  - Implement `_has_exercise_keywords(content)` using simple `if keyword in content.lower()` checks (no regex)
  - Implement `_parse_exercise(content)` using simple keyword matching for exercise names
  - Integrate `app.llm.google.GoogleLLMProvider` for extracting sets/reps/weight (call `extract_json()` with exercise extraction prompt)
  - If LLM disabled or fails, use defaults: 3 sets, 10 reps, 0 kg
  - Return `BrainResponse` with action_type=LOG_EXERCISE when exercise found
  - _Requirements: 6.1, 6.2, 6.3_

- [x] 5.1 Write property test for exercise keyword detection
  - **Property 8: Exercise keyword detection triggers parsing**
  - **Validates: Requirements 6.1**

- [x] 5.2 Write property test for exercise value extraction
  - **Property 9: Exercise parsing extracts or defaults values**
  - **Validates: Requirements 6.2, 6.3**

- [x] 6. Implement BrainService general response, attachments, and main router
  - Implement `_general_response()` method returning helpful suggestions
  - Implement `_handle_image_attachment()` returning hardcoded vision response: "I see what looks like a healthy meal! For now, tell me what you ate and I'll log it."
  - Implement `_handle_audio_attachment()` returning hardcoded voice response: "I heard your voice note! For now, type what you said and I'll log it."
  - Implement `process_message(content, attachment_type)` as main entry point
  - If attachment_type=image, return vision mock response
  - If attachment_type=audio, return voice mock response
  - Try food parsing first if food keywords present
  - Try exercise parsing if exercise keywords present
  - Fall back to general response
  - _Requirements: 5.6, 6.6, 7.1, 7.2, 7.3_

- [x] 6.1 Write property test for non-matching messages
  - **Property 11: Non-matching messages get helpful response**
  - **Validates: Requirements 7.1, 7.2, 7.3**

- [x] 7. Create chat API routes
  - Create `backend/app/api/routes/chat.py`
  - Implement `GET /api/v1/chat/messages` endpoint with limit param (default 50)
  - Implement `POST /api/v1/chat/messages` endpoint
  - Register router in `backend/app/api/main.py`
  - _Requirements: 4.1, 4.2, 4.3, 4.4_

- [x] 8. Wire POST /chat/messages to create logs
  - In POST handler, after Brain processes message:
  - If action_type=LOG_FOOD, call `create_meal_log()` with action_data
  - If action_type=LOG_EXERCISE, call `create_exercise_log()` with action_data
  - Store both user message and assistant response in chat_message table
  - Return response with action_type and action_data
  - _Requirements: 5.3, 5.4, 6.4, 6.5_

- [x] 8.1 Write property test for food logging creates record
  - **Property 6: Food logging creates record and confirms**
  - **Validates: Requirements 5.3, 5.4**

- [x] 8.2 Write property test for exercise logging creates record
  - **Property 10: Exercise logging creates record and confirms**
  - **Validates: Requirements 6.4, 6.5**

- [x] 9. Checkpoint - Ensure chat tests pass
  - Ensure all tests pass, ask the user if questions arise.

- [x] 10. Create DemoService with persona configurations
  - Create `backend/app/services/demo.py`
  - Define `DemoPersona` dataclass with all profile fields
  - Define `PERSONAS` dict with 3 configurations:
    - "cut": Cutting (male, 85kg, 180cm, standard_cut, moderately_active, onboarding_complete=False)
    - "bulk": Bulking (male, 90kg, 185cm, moderate_gain, very_active, onboarding_complete=False)
    - "maintain": Maintenance (female, 60kg, 165cm, maintenance, lightly_active, onboarding_complete=False)
  - Implement `get_or_create_demo_user(session, persona)` - creates user if not exists, returns user
  - Implement `list_personas()` - returns available personas for UI
  - _Requirements: 1.1, 1.2, 2.1, 2.2, 2.3, 2.4_

- [x] 11. Create demo API routes
  - Create `backend/app/api/routes/demo.py`
  - Implement `GET /api/v1/demo/users` - list available personas (cut, bulk, maintain)
  - Implement `POST /api/v1/demo/login/{persona}` - creates user if needed, returns JWT token
  - Register router only when `ENVIRONMENT == "local"`
  - _Requirements: 1.1, 1.2, 1.3, 1.4, 1.5_

- [x] 12. Add "reset" command to BrainService
  - Add "reset" to keywords detection
  - Implement `_handle_reset(user_id)` that deletes all of today's MealLog and ExerciseLog for user
  - Return `BrainResponse` with action_type=reset and confirmation message
  - _Requirements: 7.4_

- [x] 13. Write acceptance tests for demo mode
  - Test GET /demo/users returns 3 personas (cut, bulk, maintain)
  - Test POST /demo/login/cut creates user with onboarding_complete=False and returns token
  - Test POST /demo/login/cut on existing user returns token without recreating
  - Test demo endpoints return 404 in non-local environment
  - Test "reset" command clears today's logs
  - _Requirements: 1.1, 1.2, 1.3, 1.4, 1.5, 7.4_

- [x] 14. Checkpoint - Ensure all backend tests pass
  - Ensure all tests pass, ask the user if questions arise.

- [x] 15. Regenerate OpenAPI client
  - Run `./scripts/generate-client.sh`
  - Verify ChatService is generated with getMessages, sendMessage
  - Verify DemoService is generated with getUsers, loginPersona
  - Verify types include ChatMessagePublic, DemoPersonaPublic
  - _Enables frontend integration_

- [x] 16. Create useAuth hook with demo support
  - Create `frontend/src/hooks/useAuth.ts`
  - Store token in localStorage
  - Implement `loginDemo(persona)` - calls POST /demo/login/{persona}, stores token
  - Implement `logout()` - clears token
  - Implement `isAuthenticated` check
  - Configure OpenAPI client to use stored token
  - _Requirements: 8.1, 8.2_

- [x] 17. Create DemoLogin component
  - Create `frontend/src/components/Fitness/DemoLogin.tsx`
  - Display 3 clickable cards (Cut, Bulk, Maintain) with descriptions
  - On click: call `loginDemo(persona)` then redirect to FitnessApp
  - Style with Chakra UI
  - _Requirements: 8.1, 8.2_

- [x] 18. Update FitnessApp with auth guard
  - Check `isAuthenticated` - if false, show DemoLogin
  - Fetch profile via `GET /profile/me`
  - If `onboarding_complete === false` → render Onboarding
  - If `onboarding_complete === true` → render Dashboard
  - _Requirements: 8.3, 8.4, 8.5_

- [x] 19. Update Onboarding to pre-fill from API
  - On mount: call `GET /profile/me` to fetch current profile
  - Pre-fill all form inputs with fetched data (weight, height, goal, etc.)
  - On "Start Journey" click: call `PUT /profile/me` with `onboarding_complete: true`
  - On success: trigger re-render to show Dashboard
  - _Requirements: 9.1, 9.2, 9.3, 9.4_

- [x] 20. Create useChat hook
  - Create `frontend/src/hooks/useChat.ts`
  - Use TanStack Query for GET /chat/messages
  - Use TanStack Mutation for POST /chat/messages
  - On mutation success with action_type=log_*, invalidate logs and summary queries
  - On mutation success with action_type=reset, invalidate logs and summary queries
  - _Requirements: 10.1, 10.2, 10.3_

- [x] 21. Update ChatInterface component
  - Import useChat hook
  - Replace mock/local state with hook data
  - Display messages from API
  - Show typing indicator when isSending
  - Handle action_type for ActionCard rendering
  - Add image attachment button (sends attachment_type=image with placeholder URL)
  - Add voice attachment button (sends attachment_type=audio with placeholder URL)
  - _Requirements: 10.3, 10.4, 4.5_
  - **Note**: Created useLogs.ts and useSummary.ts hooks for data fetching

- [x] 22. Wire Monitor to auto-update on chat logs
  - Created useLogs and useSummary hooks
  - useChat hook invalidates logs and summary queries on log_food, log_exercise, reset actions
  - _Requirements: 11.1, 11.2, 11.3_

- [x] 22.1 Write property test for chat logging updates summary
  - **Property 12: Chat logging updates summary consistently**
  - **Validates: Requirements 11.1, 11.2, 11.3, 11.4**

- [x] 23. Final Checkpoint - Test all flows
  - Ensure all tests pass, ask the user if questions arise.
  - Manual test: Demo login (cut) → Onboarding pre-filled → click Start → Dashboard
  - Manual test: Chat "banana" → Monitor updates calories
  - Manual test: Chat "bench" → Monitor updates workouts
  - Manual test: Chat "reset" → Monitor resets to zero
  - Manual test: Send image attachment → get mock vision response
  - Manual test: Send audio attachment → get mock voice response
  - Manual test: Switch personas → verify separate data
