"""
Property-based tests for Brain Service.

Uses Hypothesis to verify correctness properties defined in the design document.
These are Small (Unit) tests - no DB, no network, pure logic.

Feature: slices-0-3
"""

import pytest
from hypothesis import given, settings, assume
from hypothesis import strategies as st

from app.models import ChatActionType, ChatAttachmentType
from app.services.brain import BrainService


# ============================================================================
# Strategies
# ============================================================================

# Food keywords from BrainService
FOOD_KEYWORDS = {"ate", "eaten", "had", "breakfast", "lunch", "dinner", "snack", "eating", "eat"}

# Known foods from BrainService.FOOD_DB
KNOWN_FOODS = {"banana", "chicken", "rice", "eggs", "oats", "salmon", "broccoli", "apple", "bread", "milk"}

# Exercise keywords
EXERCISE_KEYWORDS = {"bench", "squat", "deadlift", "press", "row", "curl", "sets", "reps", "kg", "lbs", "pullup", "dip"}

# Strategy for messages with food keywords
food_keyword_strategy = st.sampled_from(list(FOOD_KEYWORDS))
known_food_strategy = st.sampled_from(list(KNOWN_FOODS))
random_text_strategy = st.text(min_size=0, max_size=100, alphabet=st.characters(whitelist_categories=("L", "N", "P", "Z")))


def message_with_food_keyword(keyword: str, prefix: str = "", suffix: str = "") -> str:
    """Create a message containing a food keyword."""
    return f"{prefix} {keyword} {suffix}".strip()


def message_with_known_food(food: str, keyword: str) -> str:
    """Create a message with a known food and food keyword."""
    return f"I {keyword} a {food}"


# ============================================================================
# Property 4: Food keyword detection triggers parsing
# Feature: slices-0-3, Property 4: Food keyword detection triggers parsing
# Validates: Requirements 5.1
# ============================================================================


@pytest.mark.unit
class TestFoodKeywordDetection:
    """Property 4: Food keyword detection triggers parsing."""

    @given(
        keyword=food_keyword_strategy,
        prefix=random_text_strategy,
        suffix=random_text_strategy,
    )
    @settings(max_examples=100)
    def test_food_keywords_detected(
        self,
        keyword: str,
        prefix: str,
        suffix: str,
    ) -> None:
        """
        Feature: slices-0-3, Property 4: Food keyword detection triggers parsing

        For any message containing food keywords (ate, eaten, had, breakfast, lunch,
        dinner, snack), the Brain Service SHALL invoke the food parser before falling
        back to general response.

        Validates: Requirements 5.1
        """
        brain = BrainService()
        message = message_with_food_keyword(keyword, prefix, suffix)

        # The _has_food_keywords method should return True
        assert brain._has_food_keywords(message) is True

    @given(
        text=st.text(min_size=1, max_size=200, alphabet=st.characters(whitelist_categories=("L", "N", "Z"))),
    )
    @settings(max_examples=100)
    def test_non_food_keywords_not_detected(
        self,
        text: str,
    ) -> None:
        """
        Feature: slices-0-3, Property 4: Food keyword detection triggers parsing

        Messages without food keywords or food names should not trigger food parsing.

        Validates: Requirements 5.1
        """
        # Ensure the text doesn't contain any food keywords or known food names
        lower_text = text.lower()
        assume(not any(kw in lower_text for kw in FOOD_KEYWORDS))
        assume(not any(food in lower_text for food in KNOWN_FOODS))

        brain = BrainService()
        assert brain._has_food_keywords(text) is False


# ============================================================================
# Property 5: Known food parsing produces correct action
# Feature: slices-0-3, Property 5: Known food parsing produces correct action
# Validates: Requirements 5.2
# ============================================================================


@pytest.mark.unit
class TestKnownFoodParsing:
    """Property 5: Known food parsing produces correct action."""

    @given(
        food=known_food_strategy,
        keyword=food_keyword_strategy,
    )
    @settings(max_examples=100)
    def test_known_food_returns_log_food_action(
        self,
        food: str,
        keyword: str,
    ) -> None:
        """
        Feature: slices-0-3, Property 5: Known food parsing produces correct action

        For any message containing a known food name from FOOD_DB, the Brain Service
        SHALL return action_type=log_food with action_data containing the correct
        macro values from the database.

        Validates: Requirements 5.2
        """
        brain = BrainService()
        message = message_with_known_food(food, keyword)

        response = brain.process_message(message)

        # Should return LOG_FOOD action
        assert response.action_type == ChatActionType.LOG_FOOD

        # action_data should contain correct macro values
        assert response.action_data is not None
        assert response.action_data["food"] == food

        # Verify macros match the database
        expected_macros = brain.FOOD_DB[food]
        assert response.action_data["calories"] == expected_macros.calories
        assert response.action_data["protein_g"] == expected_macros.protein
        assert response.action_data["carbs_g"] == expected_macros.carbs
        assert response.action_data["fat_g"] == expected_macros.fat

    @given(food=known_food_strategy)
    @settings(max_examples=100)
    def test_known_food_response_contains_food_name_and_calories(
        self,
        food: str,
    ) -> None:
        """
        Feature: slices-0-3, Property 5: Known food parsing produces correct action

        The assistant response SHALL contain the food name and calorie count.

        Validates: Requirements 5.2
        """
        brain = BrainService()
        message = f"I ate a {food}"

        response = brain.process_message(message)

        # Response content should mention the food and calories
        assert food in response.content.lower()
        expected_calories = brain.FOOD_DB[food].calories
        assert str(expected_calories) in response.content


# ============================================================================
# Property 7: Unknown food falls back gracefully
# Feature: slices-0-3, Property 7: Unknown food falls back gracefully
# Validates: Requirements 5.5
# ============================================================================


@pytest.mark.unit
class TestUnknownFoodFallback:
    """Property 7: Unknown food falls back gracefully."""

    @given(
        unknown_food=st.text(min_size=3, max_size=20, alphabet=st.characters(whitelist_categories=("L",))),
        keyword=food_keyword_strategy,
    )
    @settings(max_examples=100)
    def test_unknown_food_returns_none_action(
        self,
        unknown_food: str,
        keyword: str,
    ) -> None:
        """
        Feature: slices-0-3, Property 7: Unknown food falls back gracefully

        For any message mentioning food keywords but containing no known food name,
        the Brain Service SHALL return action_type=none without error.

        Validates: Requirements 5.5
        """
        # Ensure the food is not in the known foods list
        assume(unknown_food.lower() not in KNOWN_FOODS)
        # Also ensure it doesn't contain any known food as substring
        assume(not any(known in unknown_food.lower() for known in KNOWN_FOODS))
        # Also ensure it doesn't contain any exercise keywords
        assume(not any(kw in unknown_food.lower() for kw in EXERCISE_KEYWORDS))

        brain = BrainService()
        message = f"I {keyword} some {unknown_food}"

        response = brain.process_message(message)

        # Should return NONE action (general response)
        assert response.action_type == ChatActionType.NONE
        # Should not have action_data
        assert response.action_data is None


# ============================================================================
# Property 11: Non-matching messages get helpful response
# Feature: slices-0-3, Property 11: Non-matching messages get helpful response
# Validates: Requirements 7.1, 7.2, 7.3
# ============================================================================


@pytest.mark.unit
class TestGeneralResponse:
    """Property 11: Non-matching messages get helpful response."""

    @given(
        text=st.text(min_size=1, max_size=200, alphabet=st.characters(whitelist_categories=("L", "N", "Z"))),
    )
    @settings(max_examples=100)
    def test_non_matching_returns_none_action(
        self,
        text: str,
    ) -> None:
        """
        Feature: slices-0-3, Property 11: Non-matching messages get helpful response

        For any message that does not match food or exercise patterns, the Brain
        Service SHALL return action_type=none with a response containing example commands.

        Validates: Requirements 7.1, 7.2, 7.3
        """
        # Ensure the text doesn't contain any food keywords, food names, or exercise keywords
        lower_text = text.lower()
        assume(not any(kw in lower_text for kw in FOOD_KEYWORDS))
        assume(not any(food in lower_text for food in KNOWN_FOODS))
        assume(not any(kw in lower_text for kw in EXERCISE_KEYWORDS))
        assume("reset" not in lower_text)

        brain = BrainService()
        response = brain.process_message(text)

        # Should return NONE action
        assert response.action_type == ChatActionType.NONE

        # Response should contain helpful suggestions
        assert "log" in response.content.lower() or "help" in response.content.lower() or "try" in response.content.lower()

    def test_general_response_contains_examples(self) -> None:
        """
        Feature: slices-0-3, Property 11: Non-matching messages get helpful response

        The general response SHALL suggest example commands the user can try.

        Validates: Requirements 7.3
        """
        brain = BrainService()
        response = brain._general_response()

        # Should contain example commands
        assert "banana" in response.content.lower() or "food" in response.content.lower()
        assert "bench" in response.content.lower() or "exercise" in response.content.lower()



# ============================================================================
# Property 8: Exercise keyword detection triggers parsing
# Feature: slices-0-3, Property 8: Exercise keyword detection triggers parsing
# Validates: Requirements 6.1
# ============================================================================


@pytest.mark.unit
class TestExerciseKeywordDetection:
    """Property 8: Exercise keyword detection triggers parsing."""

    @given(
        keyword=st.sampled_from(list(EXERCISE_KEYWORDS)),
        prefix=random_text_strategy,
        suffix=random_text_strategy,
    )
    @settings(max_examples=100)
    def test_exercise_keywords_detected(
        self,
        keyword: str,
        prefix: str,
        suffix: str,
    ) -> None:
        """
        Feature: slices-0-3, Property 8: Exercise keyword detection triggers parsing

        For any message containing exercise keywords (bench, squat, deadlift, press,
        row, curl, sets, reps, kg, lbs), the Brain Service SHALL invoke the exercise parser.

        Validates: Requirements 6.1
        """
        brain = BrainService()
        message = f"{prefix} {keyword} {suffix}".strip()

        # The _has_exercise_keywords method should return True
        assert brain._has_exercise_keywords(message) is True


# ============================================================================
# Property 9: Exercise parsing extracts or defaults values
# Feature: slices-0-3, Property 9: Exercise parsing extracts or defaults values
# Validates: Requirements 6.2, 6.3
# ============================================================================


# Known exercises from BrainService.EXERCISE_MAP
KNOWN_EXERCISES = {"bench", "squat", "deadlift", "press", "row", "curl", "pullup", "pull-up", "dip"}


@pytest.mark.unit
class TestExerciseParsing:
    """Property 9: Exercise parsing extracts or defaults values."""

    @given(
        exercise=st.sampled_from(list(KNOWN_EXERCISES)),
        sets=st.integers(min_value=1, max_value=10),
        reps=st.integers(min_value=1, max_value=30),
        weight=st.integers(min_value=1, max_value=300),  # Use integers for cleaner parsing
    )
    @settings(max_examples=100)
    def test_exercise_with_values_extracts_correctly(
        self,
        exercise: str,
        sets: int,
        reps: int,
        weight: int,
    ) -> None:
        """
        Feature: slices-0-3, Property 9: Exercise parsing extracts or defaults values

        For any exercise message, the Brain Service SHALL extract sets, reps, and
        weight if present.

        Validates: Requirements 6.2
        """
        brain = BrainService()
        message = f"Did {sets} sets of {exercise} for {reps} reps at {weight}kg"

        response = brain.process_message(message)

        # Should return LOG_EXERCISE action
        assert response.action_type == ChatActionType.LOG_EXERCISE
        assert response.action_data is not None

        # Values should be extracted
        assert response.action_data["sets"] == sets
        assert response.action_data["reps"] == reps
        assert response.action_data["weight_kg"] == float(weight)

    @given(exercise=st.sampled_from(list(KNOWN_EXERCISES)))
    @settings(max_examples=100)
    def test_exercise_without_values_uses_defaults(
        self,
        exercise: str,
    ) -> None:
        """
        Feature: slices-0-3, Property 9: Exercise parsing extracts or defaults values

        When sets/reps/weight are not specified, the System SHALL use defaults
        (3 sets, 10 reps, 0 kg).

        Validates: Requirements 6.3
        """
        brain = BrainService()
        message = f"Did some {exercise}"

        response = brain.process_message(message)

        # Should return LOG_EXERCISE action
        assert response.action_type == ChatActionType.LOG_EXERCISE
        assert response.action_data is not None

        # Should use default values
        assert response.action_data["sets"] == 3
        assert response.action_data["reps"] == 10
        assert response.action_data["weight_kg"] == 0.0

    @given(exercise=st.sampled_from(list(KNOWN_EXERCISES)))
    @settings(max_examples=100)
    def test_exercise_response_contains_exercise_name(
        self,
        exercise: str,
    ) -> None:
        """
        Feature: slices-0-3, Property 9: Exercise parsing extracts or defaults values

        The assistant response SHALL contain the exercise name and logged values.

        Validates: Requirements 6.5
        """
        brain = BrainService()
        message = f"Did some {exercise}"

        response = brain.process_message(message)

        # Response should mention the exercise
        # The exercise name is mapped to a proper name
        assert response.action_data is not None
        exercise_name = response.action_data["exercise_name"]
        assert exercise_name in response.content



# ============================================================================
# Property 6: Food logging creates record and confirms
# Feature: slices-0-3, Property 6: Food logging creates record and confirms
# Validates: Requirements 5.3, 5.4
# ============================================================================


@pytest.mark.unit
class TestFoodLoggingResponse:
    """Property 6: Food logging creates record and confirms."""

    @given(food=known_food_strategy)
    @settings(max_examples=100)
    def test_food_logging_returns_action_data_for_meal_log(
        self,
        food: str,
    ) -> None:
        """
        Feature: slices-0-3, Property 6: Food logging creates record and confirms

        For any successful food parse (action_type=log_food), the action_data SHALL
        contain all fields needed to create a MealLog record.

        Validates: Requirements 5.3
        """
        brain = BrainService()
        message = f"I ate a {food}"

        response = brain.process_message(message)

        # Should return LOG_FOOD action
        assert response.action_type == ChatActionType.LOG_FOOD
        assert response.action_data is not None

        # action_data should contain all fields needed for MealLog
        assert "meal_name" in response.action_data
        assert "meal_type" in response.action_data
        assert "calories" in response.action_data
        assert "protein_g" in response.action_data
        assert "carbs_g" in response.action_data
        assert "fat_g" in response.action_data

    @given(food=known_food_strategy)
    @settings(max_examples=100)
    def test_food_logging_response_confirms_with_calories(
        self,
        food: str,
    ) -> None:
        """
        Feature: slices-0-3, Property 6: Food logging creates record and confirms

        The assistant response SHALL confirm what was logged with calories and protein.

        Validates: Requirements 5.4
        """
        brain = BrainService()
        message = f"I ate a {food}"

        response = brain.process_message(message)

        # Response should contain confirmation with calories
        assert "kcal" in response.content.lower() or "cal" in response.content.lower()
        assert "protein" in response.content.lower()


# ============================================================================
# Property 10: Exercise logging creates record and confirms
# Feature: slices-0-3, Property 10: Exercise logging creates record and confirms
# Validates: Requirements 6.4, 6.5
# ============================================================================


@pytest.mark.unit
class TestExerciseLoggingResponse:
    """Property 10: Exercise logging creates record and confirms."""

    @given(exercise=st.sampled_from(list(KNOWN_EXERCISES)))
    @settings(max_examples=100)
    def test_exercise_logging_returns_action_data_for_exercise_log(
        self,
        exercise: str,
    ) -> None:
        """
        Feature: slices-0-3, Property 10: Exercise logging creates record and confirms

        For any successful exercise parse (action_type=log_exercise), the action_data
        SHALL contain all fields needed to create an ExerciseLog record.

        Validates: Requirements 6.4
        """
        brain = BrainService()
        message = f"Did some {exercise}"

        response = brain.process_message(message)

        # Should return LOG_EXERCISE action
        assert response.action_type == ChatActionType.LOG_EXERCISE
        assert response.action_data is not None

        # action_data should contain all fields needed for ExerciseLog
        assert "exercise_name" in response.action_data
        assert "sets" in response.action_data
        assert "reps" in response.action_data
        assert "weight_kg" in response.action_data

    @given(exercise=st.sampled_from(list(KNOWN_EXERCISES)))
    @settings(max_examples=100)
    def test_exercise_logging_response_confirms_details(
        self,
        exercise: str,
    ) -> None:
        """
        Feature: slices-0-3, Property 10: Exercise logging creates record and confirms

        The assistant response SHALL confirm the logged exercise details.

        Validates: Requirements 6.5
        """
        brain = BrainService()
        message = f"Did some {exercise}"

        response = brain.process_message(message)

        # Response should contain the exercise name
        assert response.action_data is not None
        exercise_name = response.action_data["exercise_name"]
        assert exercise_name in response.content

        # Response should contain sets x reps format
        assert "x" in response.content.lower() or "sets" in response.content.lower()
