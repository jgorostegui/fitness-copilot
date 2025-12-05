# Implementation Plan: Smart Assistant

This implementation plan is structured in 3 phases with manual testing checkpoints between each phase. Each phase must be fully working before proceeding to the next.

## Phase 1: Data Realism (Foundation)

This phase updates the demo data to be realistic with weekly meal plans and differentiated personas. If this breaks, everything breaks.

- [x] 1. Update User model with simulated_day field
  - [x] 1.1 Add `simulated_day: int = Field(default=0, ge=0, le=6)` to User model
    - Add field to UserBase class
    - Add to UserProfilePublic response model
    - Add to UserProfileUpdate for setting the day
    - _Requirements: 6.1_
  - [x] 1.2 Create Alembic migration for simulated_day column
    - Generate migration with `just migration "add_simulated_day_to_user"`
    - Run migration and verify
    - _Requirements: 6.1_

- [x] 2. Create realistic weekly meal plan data
  - [x] 2.1 Create meal plan CSV files for each persona
    - Create `data/meal_plans_cut.csv` with 7 days, 4 meals/day, calorie deficit (~1800 kcal)
    - Create `data/meal_plans_bulk.csv` with 7 days, 5 meals/day, calorie surplus (~3200 kcal)
    - Create `data/meal_plans_maintain.csv` with 7 days, 4 meals/day, maintenance (~2200 kcal)
    - Include realistic dish names (not single ingredients)
    - _Requirements: 4.1, 5.1, 5.2, 5.3, 5.4_
  - [x] 2.2 Update CSVImportService to load persona-specific meal plans
    - Add method `load_meal_plans_for_persona(persona: str, user_id: UUID)`
    - Load from persona-specific CSV file
    - Create MealPlan entries for all 7 days
    - _Requirements: 4.1, 5.4_

- [x] 3. Update demo personas with distinct training programs
  - [x] 3.1 Create training program CSV files for each persona
    - Create `data/routines_cut.csv` with 6-day PPL split (Push/Pull/Legs x2)
    - Create `data/routines_bulk.csv` with 4-day Upper/Lower split
    - Create `data/routines_maintain.csv` with 3-day Full Body program
    - _Requirements: 5.1, 5.2, 5.3_
  - [x] 3.2 Update DemoService to assign persona-specific programs
    - Update `get_or_create_demo_user()` to create training program
    - Assign correct program based on persona
    - Load meal plans for the persona
    - _Requirements: 5.1, 5.2, 5.3, 5.4_

- [x] 3.3 Write property test for demo persona training days
  - **Property 9: Demo Persona Training Days**
  - **Validates: Requirements 5.1, 5.2, 5.3**

- [x] 3.4 Write property test for weekly meal plan completeness
  - **Property 7: Weekly Meal Plan Completeness**
  - **Validates: Requirements 4.1, 5.4**

- [x] 4. Update Quick Add with realistic meals
  - [x] 4.1 Replace quick add options in ContextWidget
    - Remove single ingredients (banana, shake, coffee, eggs)
    - Add complete dishes: "Grilled Chicken Salad", "Oatmeal with Berries", "Eggs & Avocado Toast", "Rice & Grilled Chicken"
    - Update macro values to be realistic for complete dishes
    - _Requirements: 3.1, 3.2, 3.3_
  - [x] 4.2 Update BrainService FOOD_DB with realistic meals
    - Add complete dish entries with realistic macros
    - Keep some simple foods for text parsing
    - _Requirements: 3.2_

- [x] 4.3 Write property test for quick add macro validity
  - **Property 6: Quick Add Macro Validity**
  - **Validates: Requirements 3.1, 3.2, 3.3**

- [x] 5. Implement simulated day endpoints
  - [x] 5.1 Add `GET /api/v1/profile/me/day` endpoint
    - Return current simulated_day and day name
    - _Requirements: 6.1_
  - [x] 5.2 Add `PUT /api/v1/profile/me/day` endpoint
    - Accept day number (0-6)
    - Update user's simulated_day
    - _Requirements: 6.2_
  - [x] 5.3 Update meal plan endpoint to use simulated_day
    - Modify `GET /api/v1/plans/meal/today` to filter by simulated_day
    - _Requirements: 4.2, 4.3, 6.2_
  - [x] 5.4 Update training routine endpoint to use simulated_day
    - Modify `GET /api/v1/plans/training/today` to filter by simulated_day
    - _Requirements: 6.2_

- [x] 5.5 Write property test for simulated day filtering
  - **Property 8: Simulated Day Affects Targets Only**
  - **Validates: Requirements 4.2, 4.3, 4.4, 6.2, 6.3, 6.4, 6.5**

- [x] 6. Add DaySelector component to frontend
  - [x] 6.1 Create DaySelector component
    - Display current day name (Monday-Sunday)
    - Dropdown or buttons to select different day
    - Call PUT /profile/me/day on change
    - _Requirements: 6.1, 6.2_
  - [x] 6.2 Integrate DaySelector in Dashboard
    - Add to header area
    - Invalidate meal plan and training queries on day change
    - _Requirements: 6.2_

- [x] 7. Phase 1 Checkpoint - Manual Testing
  - Ensure all tests pass
  - Manual test: Login as "cut" persona → verify 6-day training program
  - Manual test: Login as "bulk" persona → verify 4-day training program
  - Manual test: Login as "maintain" persona → verify 3-day training program
  - Manual test: Verify weekly meal plans exist for all 7 days
  - Manual test: Change simulated day → verify meal plan and training routine update
  - Manual test: Quick add buttons show realistic dishes with proper macros
  - Ask the user if questions arise

---

## Phase 2: Context Enhancement

This phase enhances the ContextBuilder to include all relevant data and ensures tenant isolation. Depends on Phase 1 data being correct.

- [x] 8. Enhance ContextBuilder with full context
  - [x] 8.1 Update UserContext dataclass
    - Add `simulated_day` field
    - Add `scheduled_meals` for simulated day's meal plan
    - Ensure `chat_history` only includes text content (no attachments)
    - _Requirements: 1.1, 1.2, 1.3, 1.4, 1.7_
  - [x] 8.2 Update build_context() to use simulated_day
    - Fetch meal plans for simulated_day (not real day)
    - Fetch training routines for simulated_day
    - Fetch real logs for progress calculation
    - _Requirements: 1.2, 1.3, 6.5_
  - [x] 8.3 Filter chat history to exclude attachments
    - Only include `role` and `content` fields
    - Exclude `attachment_url` and `attachment_type`
    - Limit to last 10 messages
    - _Requirements: 1.4, 1.7_

- [x] 8.4 Write property test for context completeness and safety
  - **Property 2: Context Completeness and Safety**
  - **Validates: Requirements 1.1, 1.2, 1.3, 1.4, 1.7**

- [x] 8.5 Write property test for chat history token safety
  - **Property 12: Chat History Token Safety**
  - **Validates: Requirements 1.4, 1.7**

- [x] 9. Ensure tenant isolation in context
  - [x] 9.1 Add user_id filter to all context queries
    - Verify meal logs query filters by user_id
    - Verify exercise logs query filters by user_id
    - Verify chat messages query filters by user_id
    - Verify meal plans query filters by user_id
    - _Requirements: 1.5, 8.1, 8.2, 8.3, 8.4, 8.5_

- [x] 9.2 Write property test for tenant isolation
  - **Property 1: Tenant Isolation in Context Building**
  - **Validates: Requirements 1.5, 8.1, 8.2, 8.3, 8.4, 8.5**

- [x] 10. Enhance assistant responses with context
  - [x] 10.1 Update BrainService to include progress in responses
    - After logging food, include "You're at X% of your calorie target"
    - After logging exercise, reference training plan progress
    - _Requirements: 1.6, 7.2, 7.3_
  - [x] 10.2 Update VisionService prompts with full context
    - Pass UserContext to gym equipment analysis
    - Pass UserContext to food analysis
    - Include goal-specific advice based on context
    - _Requirements: 1.6_

- [x] 10.3 Write property test for meal logging feedback
  - **Property 10: Meal Logging Feedback**
  - **Validates: Requirements 7.2**

- [x] 10.4 Write property test for exercise logging feedback
  - **Property 11: Exercise Logging Feedback**
  - **Validates: Requirements 7.3**

- [x] 11. Phase 2 Checkpoint - Manual Testing
  - Ensure all tests pass
  - Manual test: Send chat message → verify context includes profile data
  - Manual test: Log a meal → verify response includes progress feedback
  - Manual test: Log an exercise → verify response references training plan
  - Manual test: Login as different users → verify no data leakage
  - Manual test: Send image → verify context is passed to LLM
  - Ask the user if questions arise

---

## Phase 3: Vision UX Enhancement

This phase changes the API contract for vision responses and frontend interaction. Depends on Phase 2 context being correct.

- [x] 12. Add new action types for vision preview
  - [x] 12.1 Add PROPOSE_FOOD and PROPOSE_EXERCISE to ChatActionType enum
    - Add to models.py ChatActionType enum
    - These indicate "preview before tracking"
    - _Requirements: 2.1, 2.2, 2.3_
  - [x] 12.2 Update BrainService to return PROPOSE_* for images
    - Change `_handle_image_attachment()` to return PROPOSE_FOOD or PROPOSE_EXERCISE
    - Include `is_tracked: False` in action_data
    - Store form_cues in `action_data.hidden_context.form_cues`
    - _Requirements: 2.1, 2.5, 2.7_

- [x] 12.3 Write property test for vision preview mode
  - **Property 3: Vision Analysis Preview Mode**
  - **Validates: Requirements 2.1, 2.2, 2.3**

- [x] 12.4 Write property test for form tips storage
  - **Property 5: Form Tips Storage**
  - **Validates: Requirements 2.5, 2.6**

- [x] 13. Create tracking confirmation endpoint
  - [x] 13.1 Add `POST /api/v1/chat/{message_id}/confirm` endpoint
    - Validate message exists and belongs to user
    - Validate action_type is PROPOSE_FOOD or PROPOSE_EXERCISE
    - Validate is_tracked is False
    - Create MealLog or ExerciseLog from action_data
    - Update action_data.is_tracked to True
    - Return updated message
    - _Requirements: 2.4_
  - [x] 13.2 Handle already tracked case
    - If is_tracked is True, return 400 with "Already tracked" message
    - _Requirements: 2.4_

- [x] 13.3 Write property test for tracking confirmation
  - **Property 4: Tracking Confirmation Creates Log**
  - **Validates: Requirements 2.4, 2.7**

- [x] 14. Regenerate OpenAPI client
  - Run `just generate-client`
  - Verify new action types are in types.gen.ts
  - Verify confirmMessage endpoint is generated
  - _Enables frontend integration_

- [x] 15. Update VisionResponseCard for preview mode
  - [x] 15.1 Add "Add to Track" button
    - Show button when action_type is PROPOSE_FOOD or PROPOSE_EXERCISE
    - Hide button when is_tracked is True
    - On click, call POST /chat/{message_id}/confirm
    - Update UI to show "Tracked ✓" after confirmation
    - _Requirements: 2.2, 2.3, 2.4_
  - [x] 15.2 Add "Show Form Tips" button for gym equipment
    - Show button only for PROPOSE_EXERCISE
    - On click, read form_cues from action_data.hidden_context
    - Inject local message with form tips (no API call)
    - _Requirements: 2.5, 2.6_

- [x] 16. Update ChatInterface for new action types
  - [x] 16.1 Handle PROPOSE_* action types
    - Render VisionResponseCard for PROPOSE_FOOD and PROPOSE_EXERCISE
    - Pass is_tracked state to component
    - Invalidate logs/summary queries after tracking confirmation
    - _Requirements: 2.1, 2.2, 2.3, 2.4_

- [x] 17. Phase 3 Checkpoint - Manual Testing
  - Ensure all tests pass
  - Manual test: Upload food image → verify "Add to Track" button appears
  - Manual test: Click "Add to Track" → verify meal is logged and button changes to "Tracked ✓"
  - Manual test: Upload gym equipment image → verify form tips are hidden initially
  - Manual test: Click "Show Form Tips" → verify tips appear without loading indicator
  - Manual test: Verify Monitor updates after tracking confirmation
  - Ask the user if questions arise

---

## Final Checkpoint

- [x] 18. Final Integration Testing
  - Ensure all tests pass
  - Manual test: Full flow - Login → Change day → Upload image → Preview → Track → Verify logs
  - Manual test: Context includes all data (profile, progress, plans, chat history)
  - Manual test: No data leakage between users
  - Manual test: Quick add with realistic meals works correctly
  - Ask the user if questions arise
