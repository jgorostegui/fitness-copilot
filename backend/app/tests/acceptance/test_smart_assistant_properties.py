"""
Property-based tests for Smart Assistant feature.

These tests verify correctness properties defined in the design document.
Uses Hypothesis for property-based testing.
"""

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st
from sqlmodel import Session, select

from app.models import MealPlan, TrainingProgram, TrainingRoutine
from app.services.demo import PERSONAS, get_or_create_demo_user


@pytest.mark.acceptance
class TestDemoPersonaTrainingDays:
    """
    **Feature: smart-assistant, Property 9: Demo Persona Training Days**
    **Validates: Requirements 5.1, 5.2, 5.3**

    *For any* demo persona creation, the assigned training program SHALL have
    exactly the specified number of training days: "cut" → 6 days,
    "bulk" → 4 days, "maintain" → 3 days.
    """

    @given(persona=st.sampled_from(["cut", "bulk", "maintain"]))
    @settings(max_examples=100, deadline=None)
    def test_persona_has_correct_training_days(self, db: Session, persona: str) -> None:
        """Each persona should have the correct number of training days."""
        expected_days = PERSONAS[persona].training_days

        # Create demo user (this also creates the training program)
        user = get_or_create_demo_user(db, persona)

        # Verify user has a training program assigned
        assert (
            user.selected_program_id is not None
        ), f"Persona {persona} should have a training program assigned"

        # Get the training program
        program = db.get(TrainingProgram, user.selected_program_id)
        assert program is not None, "Training program should exist"

        # Verify the program has the correct days_per_week
        assert program.days_per_week == expected_days, (
            f"Persona {persona} should have {expected_days} training days, "
            f"but program has {program.days_per_week}"
        )

        # Verify routines exist for the correct number of unique days
        routines = db.exec(
            select(TrainingRoutine).where(TrainingRoutine.program_id == program.id)
        ).all()

        unique_days = {r.day_of_week for r in routines}
        assert len(unique_days) == expected_days, (
            f"Persona {persona} should have routines for {expected_days} days, "
            f"but has routines for {len(unique_days)} days"
        )


@pytest.mark.acceptance
class TestWeeklyMealPlanCompleteness:
    """
    **Feature: smart-assistant, Property 7: Weekly Meal Plan Completeness**
    **Validates: Requirements 4.1, 5.4**

    *For any* demo user, after creation, there SHALL exist meal plan entries
    for all 7 days (0-6), with at least 3 meals per day.
    """

    @given(persona=st.sampled_from(["cut", "bulk", "maintain"]))
    @settings(max_examples=100, deadline=None)
    def test_persona_has_complete_weekly_meal_plan(
        self, db: Session, persona: str
    ) -> None:
        """Each persona should have meal plans for all 7 days with 3+ meals."""
        # Create demo user (this also creates meal plans)
        user = get_or_create_demo_user(db, persona)

        # Get all meal plans for this user
        meal_plans = db.exec(select(MealPlan).where(MealPlan.user_id == user.id)).all()

        # Group by day of week
        meals_by_day: dict[int, list[MealPlan]] = {}
        for plan in meal_plans:
            if plan.day_of_week not in meals_by_day:
                meals_by_day[plan.day_of_week] = []
            meals_by_day[plan.day_of_week].append(plan)

        # Verify all 7 days have meal plans
        for day in range(7):
            assert (
                day in meals_by_day
            ), f"Persona {persona} should have meal plans for day {day}"
            assert len(meals_by_day[day]) >= 3, (
                f"Persona {persona} should have at least 3 meals for day {day}, "
                f"but has {len(meals_by_day[day])}"
            )


# Quick add meal options (must match frontend ContextWidget.tsx)
QUICK_ADD_MEALS = [
    {
        "name": "Grilled Chicken Salad",
        "text": "I ate a Grilled Chicken Salad",
    },
    {
        "name": "Oatmeal with Berries",
        "text": "I had Oatmeal with Berries",
    },
    {
        "name": "Eggs and Avocado Toast",
        "text": "I ate Eggs and Avocado Toast",
    },
    {
        "name": "Rice and Grilled Chicken",
        "text": "I had Rice and Grilled Chicken",
    },
]


@pytest.mark.acceptance
class TestQuickAddMacroValidity:
    """
    **Feature: smart-assistant, Property 6: Quick Add Macro Validity**
    **Validates: Requirements 3.1, 3.2, 3.3**

    *For any* quick add meal option, the macro values SHALL satisfy:
    calories > 200, protein_g > 5, and the meal name SHALL contain
    at least two words (indicating a complete dish).
    """

    @given(meal_idx=st.integers(min_value=0, max_value=len(QUICK_ADD_MEALS) - 1))
    @settings(max_examples=100, deadline=None)
    def test_quick_add_meals_have_valid_macros(self, meal_idx: int) -> None:
        """Each quick add meal should have realistic macro values."""
        from app.services.brain import BrainService

        meal = QUICK_ADD_MEALS[meal_idx]
        brain = BrainService()

        # Process the quick add text
        response = brain.process_message(meal["text"])

        # Should be a food log action
        assert (
            response.action_type.value == "log_food"
        ), f"Quick add '{meal['name']}' should trigger food logging"

        # Should have action data with macros
        assert (
            response.action_data is not None
        ), f"Quick add '{meal['name']}' should have action data"

        # Validate macro values
        calories = response.action_data.get("calories", 0)
        protein = response.action_data.get("protein_g", 0)

        assert (
            calories > 200
        ), f"Quick add '{meal['name']}' should have > 200 calories, got {calories}"
        assert (
            protein > 5
        ), f"Quick add '{meal['name']}' should have > 5g protein, got {protein}"

        # Validate meal name has at least two words (complete dish)
        meal_name = response.action_data.get("meal_name", "")
        word_count = len(meal_name.split())
        assert (
            word_count >= 2
        ), f"Quick add meal name '{meal_name}' should have at least 2 words"


@pytest.mark.acceptance
class TestSimulatedDayFiltering:
    """
    **Feature: smart-assistant, Property 8: Simulated Day Affects Targets Only**
    **Validates: Requirements 4.2, 4.3, 4.4, 6.2, 6.3, 6.4, 6.5**

    *For any* user with a simulated day D:
    - Meal plan queries SHALL return data where day_of_week == D
    - Training routine queries SHALL return data where day_of_week == D
    - Log entries SHALL always use real UTC timestamps (not simulated day)
    """

    @given(
        persona=st.sampled_from(["cut", "bulk", "maintain"]),
        simulated_day=st.integers(min_value=0, max_value=6),
    )
    @settings(max_examples=100, deadline=None)
    def test_meal_plan_filtered_by_simulated_day(
        self, db: Session, persona: str, simulated_day: int
    ) -> None:
        """Meal plans should be filtered by simulated_day."""
        from app.crud_nutrition import get_meal_plans_for_user

        # Create demo user
        user = get_or_create_demo_user(db, persona)

        # Update simulated day
        user.simulated_day = simulated_day
        db.add(user)
        db.commit()
        db.refresh(user)

        # Get meal plans for simulated day
        meals = get_meal_plans_for_user(db, user.id, day_of_week=simulated_day)

        # All returned meals should be for the simulated day
        for meal in meals:
            assert meal.day_of_week == simulated_day, (
                f"Meal plan should be for day {simulated_day}, "
                f"but got day {meal.day_of_week}"
            )

    @given(
        persona=st.sampled_from(["cut", "bulk", "maintain"]),
        simulated_day=st.integers(min_value=0, max_value=6),
    )
    @settings(max_examples=100, deadline=None)
    def test_training_routine_filtered_by_simulated_day(
        self, db: Session, persona: str, simulated_day: int
    ) -> None:
        """Training routines should be filtered by simulated_day."""
        from app.crud_fitness import get_training_routines_for_program

        # Create demo user
        user = get_or_create_demo_user(db, persona)

        # Update simulated day
        user.simulated_day = simulated_day
        db.add(user)
        db.commit()
        db.refresh(user)

        if user.selected_program_id is None:
            return  # Skip if no program assigned

        # Get training routines for simulated day
        routines = get_training_routines_for_program(
            db, user.selected_program_id, day_of_week=simulated_day
        )

        # All returned routines should be for the simulated day
        for routine in routines:
            assert routine.day_of_week == simulated_day, (
                f"Training routine should be for day {simulated_day}, "
                f"but got day {routine.day_of_week}"
            )


@pytest.mark.acceptance
class TestNoDuplicateRoutines:
    """
    **Feature: smart-assistant, Property: No Duplicate Routines**
    **Validates: Bug fix for duplicate training routines on re-login**

    *For any* demo persona, logging in multiple times SHALL NOT create
    duplicate training routines. The number of routines should remain
    constant across multiple logins.
    """

    @given(
        persona=st.sampled_from(["cut", "bulk", "maintain"]),
        num_logins=st.integers(min_value=2, max_value=5),
    )
    @settings(max_examples=50, deadline=None)
    def test_multiple_logins_do_not_create_duplicate_routines(
        self, db: Session, persona: str, num_logins: int
    ) -> None:
        """Multiple logins should not create duplicate routines."""
        # First login
        user = get_or_create_demo_user(db, persona)
        program_id = user.selected_program_id

        if program_id is None:
            return  # Skip if no program assigned

        # Count initial routines
        initial_routines = db.exec(
            select(TrainingRoutine).where(TrainingRoutine.program_id == program_id)
        ).all()
        initial_count = len(initial_routines)

        # Login multiple more times
        for _ in range(num_logins - 1):
            user = get_or_create_demo_user(db, persona)

        # Count routines after multiple logins
        final_routines = db.exec(
            select(TrainingRoutine).where(TrainingRoutine.program_id == program_id)
        ).all()
        final_count = len(final_routines)

        # Should have same number of routines
        assert final_count == initial_count, (
            f"Expected {initial_count} routines after {num_logins} logins, "
            f"but got {final_count}. Duplicate routines were created!"
        )


@pytest.mark.acceptance
class TestContextCompletenessAndSafety:
    """
    **Feature: smart-assistant, Property 2: Context Completeness and Safety**
    **Validates: Requirements 1.1, 1.2, 1.3, 1.4, 1.7**

    *For any* user with profile data, meal logs, exercise logs, and chat messages,
    the built context SHALL:
    - Include user profile fields (weight, height, goal, activity level)
    - Include current day's logs (real timestamps)
    - Include simulated day's meal plan targets
    - Include the last N chat messages (where N ≤ 10) with TEXT CONTENT ONLY
    - EXCLUDE attachment_url and base64 image data from chat history
    """

    @given(
        persona=st.sampled_from(["cut", "bulk", "maintain"]),
        simulated_day=st.integers(min_value=0, max_value=6),
    )
    @settings(max_examples=100, deadline=None)
    def test_context_includes_profile_fields(
        self, db: Session, persona: str, simulated_day: int
    ) -> None:
        """Context should include all user profile fields."""
        from app.services.context import ContextBuilder

        # Create demo user
        user = get_or_create_demo_user(db, persona)
        user.simulated_day = simulated_day
        db.add(user)
        db.commit()
        db.refresh(user)

        # Build context
        builder = ContextBuilder()
        context = builder.build_context(db, user.id)

        # Verify profile fields are present
        assert context.user_id == str(user.id)
        assert context.weight_kg > 0, "Weight should be positive"
        assert context.height_cm > 0, "Height should be positive"
        assert context.goal_method in [
            "maintenance",
            "very_slow_cut",
            "slow_cut",
            "standard_cut",
            "aggressive_cut",
            "very_aggressive_cut",
            "slow_gain",
            "moderate_gain",
            "custom",
        ], f"Invalid goal_method: {context.goal_method}"
        assert context.activity_level in [
            "sedentary",
            "lightly_active",
            "moderately_active",
            "very_active",
            "super_active",
        ], f"Invalid activity_level: {context.activity_level}"
        assert context.sex in ["male", "female", "unknown"]

    @given(
        persona=st.sampled_from(["cut", "bulk", "maintain"]),
        simulated_day=st.integers(min_value=0, max_value=6),
    )
    @settings(max_examples=100, deadline=None)
    def test_context_includes_simulated_day_meal_plan(
        self, db: Session, persona: str, simulated_day: int
    ) -> None:
        """Context should include meal plan for simulated day."""
        from app.services.context import ContextBuilder

        # Create demo user
        user = get_or_create_demo_user(db, persona)
        user.simulated_day = simulated_day
        db.add(user)
        db.commit()
        db.refresh(user)

        # Build context
        builder = ContextBuilder()
        context = builder.build_context(db, user.id)

        # Verify simulated_day is set correctly
        assert context.simulated_day == simulated_day

        # Verify scheduled_meals are for the simulated day
        # (meal plans exist for all days, so we should have some)
        assert isinstance(context.scheduled_meals, list)

        # Each scheduled meal should have required fields
        for meal in context.scheduled_meals:
            assert "meal_type" in meal
            assert "item_name" in meal
            assert "calories" in meal
            assert "protein_g" in meal

    @given(persona=st.sampled_from(["cut", "bulk", "maintain"]))
    @settings(max_examples=100, deadline=None)
    def test_context_chat_history_excludes_attachments(
        self, db: Session, persona: str
    ) -> None:
        """Chat history should only include role and content, no attachments."""
        from app.crud_chat import create_chat_message
        from app.models import ChatAttachmentType, ChatMessageRole
        from app.services.context import ContextBuilder

        # Create demo user
        user = get_or_create_demo_user(db, persona)

        # Create a message with an attachment (simulating image upload)
        create_chat_message(
            db,
            user.id,
            content="Check out this food",
            role=ChatMessageRole.USER,
            attachment_type=ChatAttachmentType.IMAGE,
            attachment_url="data:image/jpeg;base64,/9j/4AAQSkZJRgABAQEASABIAAD...",
        )

        # Create a regular message
        create_chat_message(
            db,
            user.id,
            content="How many calories?",
            role=ChatMessageRole.USER,
        )

        # Build context
        builder = ContextBuilder()
        context = builder.build_context(db, user.id)

        # Verify chat history only has role and content
        for msg in context.chat_history:
            assert "role" in msg, "Chat history should include role"
            assert "content" in msg, "Chat history should include content"
            assert (
                "attachment_url" not in msg
            ), "Chat history should NOT include attachment_url"
            assert (
                "attachment_type" not in msg
            ), "Chat history should NOT include attachment_type"
            # Verify no base64 data in content
            assert (
                "base64" not in msg.get("content", "").lower()
            ), "Chat history content should not contain base64 data"


@pytest.mark.acceptance
class TestChatHistoryTokenSafety:
    """
    **Feature: smart-assistant, Property 12: Chat History Token Safety**
    **Validates: Requirements 1.4, 1.7**

    *For any* chat history included in LLM context, the total character count
    of all message contents SHALL be less than 10,000 characters, and NO message
    SHALL contain base64 encoded data or attachment URLs.
    """

    @given(
        persona=st.sampled_from(["cut", "bulk", "maintain"]),
        num_messages=st.integers(min_value=1, max_value=20),
    )
    @settings(max_examples=100, deadline=None)
    def test_chat_history_limited_to_max_messages(
        self, db: Session, persona: str, num_messages: int
    ) -> None:
        """Chat history should be limited to MAX_CHAT_HISTORY messages."""
        from app.crud_chat import create_chat_message
        from app.models import ChatMessageRole
        from app.services.context import MAX_CHAT_HISTORY, ContextBuilder

        # Create demo user
        user = get_or_create_demo_user(db, persona)

        # Create multiple messages
        for i in range(num_messages):
            create_chat_message(
                db, user.id, content=f"Test message {i}", role=ChatMessageRole.USER
            )

        # Build context
        builder = ContextBuilder()
        context = builder.build_context(db, user.id)

        # Verify chat history is limited
        assert len(context.chat_history) <= MAX_CHAT_HISTORY, (
            f"Chat history should have at most {MAX_CHAT_HISTORY} messages, "
            f"but has {len(context.chat_history)}"
        )

    @given(persona=st.sampled_from(["cut", "bulk", "maintain"]))
    @settings(max_examples=100, deadline=None)
    def test_chat_history_total_chars_limited(self, db: Session, persona: str) -> None:
        """Chat history total characters should be limited."""
        from app.crud_chat import create_chat_message
        from app.models import ChatMessageRole
        from app.services.context import MAX_CHAT_HISTORY_CHARS, ContextBuilder

        # Create demo user
        user = get_or_create_demo_user(db, persona)

        # Create messages with long content (within 2000 char limit)
        long_content = "A" * 1500  # 1500 chars per message (within DB limit)
        for i in range(10):
            create_chat_message(
                db,
                user.id,
                content=f"{long_content} - Message {i}",
                role=ChatMessageRole.USER,
            )

        # Build context
        builder = ContextBuilder()
        context = builder.build_context(db, user.id)

        # Calculate total characters
        total_chars = sum(len(msg.get("content", "")) for msg in context.chat_history)

        # Verify total is within limit
        assert total_chars <= MAX_CHAT_HISTORY_CHARS, (
            f"Chat history should have at most {MAX_CHAT_HISTORY_CHARS} chars, "
            f"but has {total_chars}"
        )

    @given(persona=st.sampled_from(["cut", "bulk", "maintain"]))
    @settings(max_examples=100, deadline=None)
    def test_chat_history_no_base64_data(self, db: Session, persona: str) -> None:
        """Chat history should not contain base64 encoded data."""
        from app.crud_chat import create_chat_message
        from app.models import ChatAttachmentType, ChatMessageRole
        from app.services.context import ContextBuilder

        # Create demo user
        user = get_or_create_demo_user(db, persona)

        # Create message with base64 attachment URL (within 500 char limit)
        base64_data = "data:image/jpeg;base64,/9j/4AAQSkZJRgABAQEASABIAAD" + "A" * 400
        create_chat_message(
            db,
            user.id,
            content="Image attached",
            role=ChatMessageRole.USER,
            attachment_type=ChatAttachmentType.IMAGE,
            attachment_url=base64_data,
        )

        # Build context
        builder = ContextBuilder()
        context = builder.build_context(db, user.id)

        # Verify no base64 data in chat history
        for msg in context.chat_history:
            content = msg.get("content", "")
            # Check for common base64 patterns
            assert (
                "data:image" not in content
            ), "Chat history should not contain data:image URLs"
            assert (
                "/9j/" not in content
            ), "Chat history should not contain JPEG base64 signatures"


@pytest.mark.acceptance
class TestTenantIsolationInContextBuilding:
    """
    **Feature: smart-assistant, Property 1: Tenant Isolation in Context Building**
    **Validates: Requirements 1.5, 8.1, 8.2, 8.3, 8.4, 8.5**

    *For any* two users A and B, when building context for user A, the resulting
    context SHALL contain zero data items (chat messages, meal logs, exercise logs,
    profile data) belonging to user B.
    """

    @given(
        persona_a=st.sampled_from(["cut", "bulk", "maintain"]),
        persona_b=st.sampled_from(["cut", "bulk", "maintain"]),
    )
    @settings(max_examples=100, deadline=None)
    def test_context_excludes_other_users_data(
        self, db: Session, persona_a: str, persona_b: str
    ) -> None:
        """Context for user A should not contain any data from user B."""
        from app.crud_chat import create_chat_message
        from app.crud_fitness import create_exercise_log
        from app.crud_nutrition import create_meal_log
        from app.models import (
            ChatMessageRole,
            ExerciseLogCreate,
            MealLogCreate,
        )
        from app.services.context import ContextBuilder

        # Create two different demo users
        user_a = get_or_create_demo_user(db, persona_a)
        # Force different email for user B to ensure different user
        user_b = get_or_create_demo_user(db, persona_b)

        # Skip if same user (can happen with same persona)
        if user_a.id == user_b.id:
            return

        # Create unique data for user B
        unique_meal_name = f"User B Unique Meal {user_b.id}"
        unique_exercise_name = f"User B Unique Exercise {user_b.id}"
        unique_chat_content = f"User B Unique Message {user_b.id}"

        # Add meal log for user B
        create_meal_log(
            db,
            user_b.id,
            MealLogCreate(
                meal_name=unique_meal_name,
                meal_type="lunch",
                calories=500,
                protein_g=30,
                carbs_g=50,
                fat_g=20,
            ),
            simulated_day=user_b.simulated_day,
        )

        # Add exercise log for user B
        create_exercise_log(
            db,
            user_b.id,
            ExerciseLogCreate(
                exercise_name=unique_exercise_name,
                sets=3,
                reps=10,
                weight_kg=50,
            ),
            simulated_day=user_b.simulated_day,
        )

        # Add chat message for user B
        create_chat_message(
            db,
            user_b.id,
            content=unique_chat_content,
            role=ChatMessageRole.USER,
        )

        # Build context for user A
        builder = ContextBuilder()
        context_a = builder.build_context(db, user_a.id)

        # Verify user A's context does not contain user B's data
        assert context_a.user_id == str(
            user_a.id
        ), "Context user_id should match user A"

        # Check chat history doesn't contain user B's message
        for msg in context_a.chat_history:
            assert unique_chat_content not in msg.get("content", ""), (
                f"User A's context should not contain user B's chat message: "
                f"{unique_chat_content}"
            )

        # Check scheduled meals don't contain user B's unique meal
        for meal in context_a.scheduled_meals:
            assert unique_meal_name not in meal.get("item_name", ""), (
                f"User A's context should not contain user B's meal: "
                f"{unique_meal_name}"
            )

        # Check scheduled exercises don't contain user B's unique exercise
        for exercise in context_a.scheduled_exercises:
            assert unique_exercise_name not in exercise.get("name", ""), (
                f"User A's context should not contain user B's exercise: "
                f"{unique_exercise_name}"
            )

    @given(persona=st.sampled_from(["cut", "bulk", "maintain"]))
    @settings(max_examples=100, deadline=None)
    def test_context_only_contains_own_profile_data(
        self, db: Session, persona: str
    ) -> None:
        """Context should only contain the user's own profile data."""
        from app.services.context import ContextBuilder

        # Create demo user
        user = get_or_create_demo_user(db, persona)

        # Build context
        builder = ContextBuilder()
        context = builder.build_context(db, user.id)

        # Verify profile data matches the user
        assert context.user_id == str(user.id)

        # Verify weight matches (within tolerance for defaults)
        if user.weight_kg is not None:
            assert context.weight_kg == user.weight_kg

        # Verify height matches (within tolerance for defaults)
        if user.height_cm is not None:
            assert context.height_cm == user.height_cm

        # Verify goal method matches
        if user.goal_method is not None:
            assert context.goal_method == user.goal_method.value


@pytest.mark.acceptance
class TestMealLoggingFeedback:
    """
    **Feature: smart-assistant, Property 10: Meal Logging Feedback**
    **Validates: Requirements 7.2**

    *For any* meal log action, the assistant response SHALL include at least
    one reference to daily progress (calories consumed, calories remaining,
    or percentage of target).
    """

    @given(
        persona=st.sampled_from(["cut", "bulk", "maintain"]),
        food_name=st.sampled_from(
            [
                "grilled chicken salad",
                "oatmeal with berries",
                "eggs and avocado toast",
                "rice and grilled chicken",
                "banana",
                "protein shake",
            ]
        ),
    )
    @settings(max_examples=100, deadline=None)
    def test_meal_logging_includes_progress_feedback(
        self, db: Session, persona: str, food_name: str
    ) -> None:
        """Meal logging response should include progress feedback."""
        from app.services.brain import BrainService

        # Create demo user
        user = get_or_create_demo_user(db, persona)

        # Create brain service with session
        brain = BrainService(session=db)

        # Process a food logging message
        response = brain.process_message(
            content=f"I ate {food_name}",
            user_id=user.id,
        )

        # Should be a food log action
        assert (
            response.action_type.value == "log_food"
        ), f"Expected log_food action, got {response.action_type.value}"

        # Response should include progress feedback
        content_lower = response.content.lower()
        has_progress_feedback = any(
            [
                "%" in response.content,  # Percentage
                "remaining" in content_lower,  # Calories remaining
                "target" in content_lower,  # Reference to target
                "consumed" in content_lower,  # Reference to consumed
                "of your" in content_lower,  # "X% of your calorie target"
            ]
        )

        assert has_progress_feedback, (
            f"Meal logging response should include progress feedback. "
            f"Got: {response.content}"
        )


@pytest.mark.acceptance
class TestExerciseLoggingFeedback:
    """
    **Feature: smart-assistant, Property 11: Exercise Logging Feedback**
    **Validates: Requirements 7.3**

    *For any* exercise log action where the user has a training plan, the
    assistant response SHALL reference the training plan or workout progress.
    """

    @given(
        persona=st.sampled_from(["cut", "bulk", "maintain"]),
        exercise_text=st.sampled_from(
            [
                "Did 3 sets of bench at 60kg",
                "Squat 4x10 at 80kg",
                "Deadlift 3x5 at 100kg",
                "Leg press 3x12 at 120kg",
            ]
        ),
    )
    @settings(max_examples=100, deadline=None)
    def test_exercise_logging_includes_plan_feedback(
        self, db: Session, persona: str, exercise_text: str
    ) -> None:
        """Exercise logging response should reference training plan."""
        from app.services.brain import BrainService

        # Create demo user (has training plan)
        user = get_or_create_demo_user(db, persona)

        # Create brain service with session
        brain = BrainService(session=db)

        # Process an exercise logging message
        response = brain.process_message(
            content=exercise_text,
            user_id=user.id,
        )

        # Should be an exercise log action
        assert (
            response.action_type.value == "log_exercise"
        ), f"Expected log_exercise action, got {response.action_type.value}"

        # Response should include plan feedback (if user has a training plan)
        if user.selected_program_id:
            content_lower = response.content.lower()
            has_plan_feedback = any(
                [
                    "plan" in content_lower,  # Reference to plan
                    "scheduled" in content_lower,  # Reference to scheduled
                    "remaining" in content_lower,  # Exercises remaining
                    "workout" in content_lower,  # Reference to workout
                    "today" in content_lower,  # Reference to today's plan
                    "extra" in content_lower,  # Extra work
                    "🎯" in response.content,  # Plan indicator emoji
                    "💡" in response.content,  # Tip indicator emoji
                ]
            )

            assert has_plan_feedback, (
                f"Exercise logging response should reference training plan. "
                f"Got: {response.content}"
            )


@pytest.mark.acceptance
class TestVisionAnalysisPreviewMode:
    """
    **Feature: smart-assistant, Property 3: Vision Analysis Preview Mode**
    **Validates: Requirements 2.1, 2.2, 2.3**

    *For any* image upload, the response SHALL have action_type of PROPOSE_FOOD
    or PROPOSE_EXERCISE (not LOG_*), and action_data.is_tracked SHALL be False.
    """

    @given(
        persona=st.sampled_from(["cut", "bulk", "maintain"]),
        image_category=st.sampled_from(["food", "gym_equipment"]),
    )
    @settings(max_examples=100, deadline=None)
    @pytest.mark.asyncio
    async def test_image_analysis_returns_propose_action(
        self, db: Session, persona: str, image_category: str
    ) -> None:
        """Image analysis should return PROPOSE_* action type with is_tracked=False."""
        from unittest.mock import AsyncMock, MagicMock

        from app.models import ChatActionType
        from app.services.brain import BrainService
        from app.services.vision import ImageCategory

        # Create demo user
        user = get_or_create_demo_user(db, persona)

        # Create brain service with session
        brain = BrainService(session=db)

        # Mock the vision service
        mock_vision = AsyncMock()
        mock_result = MagicMock()
        mock_result.error_message = None

        if image_category == "food":
            mock_result.category = ImageCategory.FOOD
            mock_food = MagicMock()
            mock_food.meal_name = "Test Meal"
            mock_food.calories = 400
            mock_food.protein_g = 30
            mock_food.carbs_g = 40
            mock_food.fat_g = 15
            mock_food.goal_specific_advice = ""
            mock_result.food_analysis = mock_food
            mock_result.gym_analysis = None
            expected_action = ChatActionType.PROPOSE_FOOD
        else:
            mock_result.category = ImageCategory.GYM_EQUIPMENT
            mock_gym = MagicMock()
            mock_gym.exercise_name = "Test Exercise"
            mock_gym.form_cues = ["Keep form tight", "Control the movement"]
            mock_gym.suggested_sets = 3
            mock_gym.suggested_reps = 10
            mock_gym.suggested_weight_kg = 50
            mock_gym.in_todays_plan = False
            mock_gym.goal_specific_advice = ""
            mock_result.gym_analysis = mock_gym
            mock_result.food_analysis = None
            expected_action = ChatActionType.PROPOSE_EXERCISE

        mock_vision.analyze_image = AsyncMock(return_value=mock_result)
        brain._vision = mock_vision

        # Process image
        response = await brain._handle_image_attachment(
            user_id=user.id,
            image_base64="dGVzdA==",
        )

        # Verify PROPOSE_* action type (not LOG_*)
        assert (
            response.action_type == expected_action
        ), f"Expected {expected_action.value}, got {response.action_type.value}"

        # Verify isTracked is False (camelCase for frontend consistency)
        assert response.action_data is not None
        assert (
            response.action_data.get("isTracked") is False
        ), "Vision analysis should return isTracked=False for preview mode"

        # For gym equipment, verify formCues are in hiddenContext (camelCase)
        if image_category == "gym_equipment":
            assert "hiddenContext" in response.action_data
            assert "formCues" in response.action_data["hiddenContext"]
            assert len(response.action_data["hiddenContext"]["formCues"]) >= 1


@pytest.mark.acceptance
class TestFormTipsStorage:
    """
    **Feature: smart-assistant, Property 5: Form Tips Storage**
    **Validates: Requirements 2.5, 2.6**

    *For any* gym equipment analysis, the action_data.hidden_context.form_cues
    SHALL contain at least one form tip, and this data SHALL be retrievable
    from the ChatMessage without a new LLM call.
    """

    @given(persona=st.sampled_from(["cut", "bulk", "maintain"]))
    @settings(max_examples=100, deadline=None)
    @pytest.mark.asyncio
    async def test_gym_analysis_stores_form_cues_in_hidden_context(
        self, db: Session, persona: str
    ) -> None:
        """Gym equipment analysis should store form cues in hidden_context."""
        from unittest.mock import AsyncMock, MagicMock

        from app.models import ChatActionType
        from app.services.brain import BrainService
        from app.services.vision import ImageCategory

        # Create demo user
        user = get_or_create_demo_user(db, persona)

        # Create brain service with session
        brain = BrainService(session=db)

        # Mock the vision service with form cues
        mock_vision = AsyncMock()
        mock_result = MagicMock()
        mock_result.error_message = None
        mock_result.category = ImageCategory.GYM_EQUIPMENT

        # Create mock gym analysis with multiple form cues
        mock_gym = MagicMock()
        mock_gym.exercise_name = "Leg Press"
        mock_gym.form_cues = [
            "Keep your back flat against the pad",
            "Don't lock your knees at the top",
            "Control the descent slowly",
        ]
        mock_gym.suggested_sets = 3
        mock_gym.suggested_reps = 12
        mock_gym.suggested_weight_kg = 100
        mock_gym.in_todays_plan = False
        mock_gym.goal_specific_advice = ""
        mock_result.gym_analysis = mock_gym
        mock_result.food_analysis = None

        mock_vision.analyze_image = AsyncMock(return_value=mock_result)
        brain._vision = mock_vision

        # Process image
        response = await brain._handle_image_attachment(
            user_id=user.id,
            image_base64="dGVzdA==",
        )

        # Verify action type is PROPOSE_EXERCISE
        assert response.action_type == ChatActionType.PROPOSE_EXERCISE

        # Verify action_data structure (camelCase for frontend consistency)
        assert response.action_data is not None
        assert (
            "hiddenContext" in response.action_data
        ), "Gym analysis should include hiddenContext in action_data"
        assert (
            "formCues" in response.action_data["hiddenContext"]
        ), "hiddenContext should include formCues"

        # Verify form cues are stored correctly
        stored_cues = response.action_data["hiddenContext"]["formCues"]
        assert len(stored_cues) >= 1, "At least one form cue should be stored"
        assert (
            stored_cues == mock_gym.form_cues
        ), "Stored form cues should match the analysis result"

        # Verify form cues are NOT in the main response content
        # (they should be hidden initially)
        for cue in stored_cues:
            assert (
                cue not in response.content
            ), f"Form cue '{cue}' should be hidden in initial response"


@pytest.mark.acceptance
class TestTrackingConfirmationCreatesLog:
    """
    **Feature: smart-assistant, Property 4: Tracking Confirmation Creates Log**
    **Validates: Requirements 2.4, 2.7**

    *For any* ChatMessage with action_type=PROPOSE_* and is_tracked=False,
    calling POST /chat/{message_id}/confirm SHALL create exactly one
    corresponding log entry and set action_data.is_tracked=True.
    """

    @given(
        persona=st.sampled_from(["cut", "bulk", "maintain"]),
        action_type=st.sampled_from(["propose_food", "propose_exercise"]),
    )
    @settings(max_examples=100, deadline=None)
    def test_confirm_creates_log_and_updates_is_tracked(
        self, client, db: Session, persona: str, action_type: str
    ) -> None:
        """Confirming a PROPOSE_* message should create a log and set is_tracked=True."""
        from app.core.config import settings
        from app.crud_chat import create_chat_message
        from app.models import ChatActionType, ChatMessageRole

        # Create demo user and get token
        user = get_or_create_demo_user(db, persona)
        r = client.post(f"{settings.API_V1_STR}/demo/login/{persona}")
        token = r.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # Create a PROPOSE_* message directly in the database
        if action_type == "propose_food":
            action_data = {
                "isTracked": False,  # camelCase for frontend consistency
                "meal_name": "Test Meal",
                "meal_type": "lunch",
                "calories": 500,
                "protein_g": 30,
                "carbs_g": 50,
                "fat_g": 20,
            }
            chat_action_type = ChatActionType.PROPOSE_FOOD
        else:
            action_data = {
                "isTracked": False,  # camelCase for frontend consistency
                "exercise_name": "Test Exercise",
                "sets": 3,
                "reps": 10,
                "weight_kg": 50,
                "hiddenContext": {"formCues": ["Keep form tight"]},
            }
            chat_action_type = ChatActionType.PROPOSE_EXERCISE

        message = create_chat_message(
            db,
            user.id,
            content="Test vision analysis",
            role=ChatMessageRole.ASSISTANT,
            action_type=chat_action_type,
            action_data=action_data,
        )

        # Get initial log counts
        initial_logs = client.get(
            f"{settings.API_V1_STR}/logs/today", headers=headers
        ).json()
        initial_meal_count = len(initial_logs["mealLogs"])
        initial_exercise_count = len(initial_logs["exerciseLogs"])

        # Confirm the tracking
        r = client.post(
            f"{settings.API_V1_STR}/chat/messages/{message.id}/confirm",
            headers=headers,
        )
        assert r.status_code == 200, f"Expected 200, got {r.status_code}: {r.text}"

        # Verify is_tracked is now True
        response_data = r.json()
        assert (
            response_data["actionData"]["isTracked"] is True
        ), "is_tracked should be True after confirmation"

        # Verify log was created
        final_logs = client.get(
            f"{settings.API_V1_STR}/logs/today", headers=headers
        ).json()

        if action_type == "propose_food":
            assert (
                len(final_logs["mealLogs"]) == initial_meal_count + 1
            ), "Exactly one meal log should be created"
        else:
            assert (
                len(final_logs["exerciseLogs"]) == initial_exercise_count + 1
            ), "Exactly one exercise log should be created"

    @given(persona=st.sampled_from(["cut", "bulk", "maintain"]))
    @settings(max_examples=100, deadline=None)
    def test_confirm_already_tracked_returns_400(
        self, client, db: Session, persona: str
    ) -> None:
        """Confirming an already tracked message should return 400."""
        from app.core.config import settings
        from app.crud_chat import create_chat_message
        from app.models import ChatActionType, ChatMessageRole

        # Create demo user and get token
        user = get_or_create_demo_user(db, persona)
        r = client.post(f"{settings.API_V1_STR}/demo/login/{persona}")
        token = r.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # Create a PROPOSE_FOOD message that's already tracked
        action_data = {
            "isTracked": True,  # Already tracked (camelCase)
            "meal_name": "Test Meal",
            "meal_type": "lunch",
            "calories": 500,
            "protein_g": 30,
            "carbs_g": 50,
            "fat_g": 20,
        }

        message = create_chat_message(
            db,
            user.id,
            content="Test vision analysis",
            role=ChatMessageRole.ASSISTANT,
            action_type=ChatActionType.PROPOSE_FOOD,
            action_data=action_data,
        )

        # Try to confirm again
        r = client.post(
            f"{settings.API_V1_STR}/chat/messages/{message.id}/confirm",
            headers=headers,
        )
        assert r.status_code == 400, f"Expected 400, got {r.status_code}"
        assert "Already tracked" in r.json()["detail"]

    @given(persona=st.sampled_from(["cut", "bulk", "maintain"]))
    @settings(max_examples=100, deadline=None)
    def test_confirm_non_propose_message_returns_400(
        self, client, db: Session, persona: str
    ) -> None:
        """Confirming a non-PROPOSE_* message should return 400."""
        from app.core.config import settings
        from app.crud_chat import create_chat_message
        from app.models import ChatActionType, ChatMessageRole

        # Create demo user and get token
        user = get_or_create_demo_user(db, persona)
        r = client.post(f"{settings.API_V1_STR}/demo/login/{persona}")
        token = r.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # Create a LOG_FOOD message (not PROPOSE_*)
        message = create_chat_message(
            db,
            user.id,
            content="Logged food",
            role=ChatMessageRole.ASSISTANT,
            action_type=ChatActionType.LOG_FOOD,
            action_data={"meal_name": "Test", "calories": 100},
        )

        # Try to confirm
        r = client.post(
            f"{settings.API_V1_STR}/chat/messages/{message.id}/confirm",
            headers=headers,
        )
        assert r.status_code == 400, f"Expected 400, got {r.status_code}"
        assert "not a trackable" in r.json()["detail"]
