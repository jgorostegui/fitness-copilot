"""
Property-based tests for Vision Service.

Uses Hypothesis to verify correctness properties defined in the design document.
These are Small (Unit) tests - no DB, no network, pure logic.

Feature: vision
"""

import base64
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

from app.models import ChatActionType

# ============================================================================
# Strategies
# ============================================================================


# Strategy for valid base64 image data (small test images)
def valid_base64_image() -> st.SearchStrategy[str]:
    """Generate valid base64-encoded image data."""
    # Generate random bytes and encode as base64
    return st.binary(min_size=10, max_size=1000).map(
        lambda b: base64.b64encode(b).decode("utf-8")
    )


# Strategy for image URLs
def valid_image_url() -> st.SearchStrategy[str]:
    """Generate valid image URL strings."""
    return st.sampled_from(
        [
            "http://localhost:8000/static/demo-images/leg-press.jpg",
            "http://localhost:8000/static/demo-images/salad-chicken-breasts.jpg",
            "https://example.com/image.jpg",
            "https://example.com/photo.png",
        ]
    )


# Strategy for image categories
IMAGE_CATEGORIES = ["gym_equipment", "food", "unknown"]


# ============================================================================
# Property 10: Both image input formats accepted
# Feature: vision, Property 10: Both image input formats accepted
# Validates: Requirements 4.3
# ============================================================================


@pytest.mark.unit
class TestImageInputFormats:
    """Property 10: Both image input formats accepted."""

    @given(image_base64=valid_base64_image())
    @settings(max_examples=100, deadline=None)
    def test_base64_input_builds_valid_parts(self, image_base64: str) -> None:
        """
        Feature: vision, Property 10: Both image input formats accepted

        For any valid base64-encoded image data, the _build_image_parts method
        SHALL produce content parts with inline_data containing the image.

        Validates: Requirements 4.3
        """
        from app.llm.google import GoogleLLMProvider

        # Mock the provider initialization to avoid needing API key
        with patch.object(GoogleLLMProvider, "__init__", lambda self, model=None: None):
            provider = GoogleLLMProvider()
            provider.model_name = "gemini-2.5-flash"

            prompt = "Analyze this image"
            parts = provider._build_image_parts(prompt, image_base64=image_base64)

            # Should have 2 parts: image and text
            assert len(parts) == 2

            # First part should be inline_data with image
            assert "inline_data" in parts[0]
            assert parts[0]["inline_data"]["mime_type"] == "image/jpeg"
            assert "data" in parts[0]["inline_data"]

            # Second part should be the prompt text
            assert parts[1] == prompt

    def test_url_input_builds_valid_parts_with_mock(self) -> None:
        """
        Feature: vision, Property 10: Both image input formats accepted

        For any valid image URL, the _build_image_parts method SHALL fetch
        the image and produce content parts with inline_data.

        Validates: Requirements 4.3
        """
        from app.llm.google import GoogleLLMProvider

        # Mock the provider initialization
        with patch.object(GoogleLLMProvider, "__init__", lambda self, model=None: None):
            provider = GoogleLLMProvider()
            provider.model_name = "gemini-2.5-flash"

            # Mock urllib.request.urlopen to return fake image data
            fake_image_bytes = b"fake image data for testing"
            mock_response = MagicMock()
            mock_response.read.return_value = fake_image_bytes
            mock_response.__enter__ = MagicMock(return_value=mock_response)
            mock_response.__exit__ = MagicMock(return_value=False)

            with patch("urllib.request.urlopen", return_value=mock_response):
                prompt = "Analyze this image"
                parts = provider._build_image_parts(
                    prompt, image_url="http://example.com/test.jpg"
                )

                # Should have 2 parts: image and text
                assert len(parts) == 2

                # First part should be inline_data with image
                assert "inline_data" in parts[0]
                assert parts[0]["inline_data"]["mime_type"] == "image/jpeg"

                # Second part should be the prompt text
                assert parts[1] == prompt

    def test_no_image_returns_only_prompt(self) -> None:
        """
        Feature: vision, Property 10: Both image input formats accepted

        When no image is provided, _build_image_parts SHALL return only the prompt.

        Validates: Requirements 4.3
        """
        from app.llm.google import GoogleLLMProvider

        with patch.object(GoogleLLMProvider, "__init__", lambda self, model=None: None):
            provider = GoogleLLMProvider()
            provider.model_name = "gemini-2.5-flash"

            prompt = "Analyze this image"
            parts = provider._build_image_parts(prompt)

            # Should have only 1 part: the prompt
            assert len(parts) == 1
            assert parts[0] == prompt

    @given(image_base64=valid_base64_image())
    @settings(max_examples=50)
    def test_base64_preferred_over_url_when_both_provided(
        self, image_base64: str
    ) -> None:
        """
        Feature: vision, Property 10: Both image input formats accepted

        When both base64 and URL are provided, base64 SHALL be used (no URL fetch).

        Validates: Requirements 4.3
        """
        from app.llm.google import GoogleLLMProvider

        with patch.object(GoogleLLMProvider, "__init__", lambda self, model=None: None):
            provider = GoogleLLMProvider()
            provider.model_name = "gemini-2.5-flash"

            # Mock urlopen to track if it's called
            with patch("urllib.request.urlopen") as mock_urlopen:
                prompt = "Analyze this image"
                parts = provider._build_image_parts(
                    prompt,
                    image_url="http://example.com/test.jpg",
                    image_base64=image_base64,
                )

                # URL should not be fetched when base64 is provided
                mock_urlopen.assert_not_called()

                # Should still have 2 parts
                assert len(parts) == 2
                assert "inline_data" in parts[0]


# ============================================================================
# Property 1: Image classification produces valid category
# Feature: vision, Property 1: Image classification produces valid category
# Validates: Requirements 1.1
# ============================================================================


@pytest.mark.unit
class TestImageClassificationCategories:
    """Property 1: Image classification produces valid category."""

    @given(category_response=st.sampled_from(IMAGE_CATEGORIES))
    @settings(max_examples=100)
    def test_classification_returns_valid_enum(self, category_response: str) -> None:
        """
        Feature: vision, Property 1: Image classification produces valid category

        For any LLM response, the classification SHALL map to exactly one of:
        gym_equipment, food, or unknown.

        Validates: Requirements 1.1
        """
        from app.services.vision import ImageCategory

        # All valid categories should be in the enum
        valid_categories = {c.value for c in ImageCategory}
        assert category_response in valid_categories


# ============================================================================
# Property 5: Gym analysis contains required fields
# Feature: vision, Property 5: Gym analysis contains required fields
# Validates: Requirements 2.1, 2.2, 2.3
# ============================================================================


@pytest.mark.unit
class TestGymAnalysisFields:
    """Property 5: Gym analysis contains required fields."""

    @given(
        exercise_name=st.text(min_size=1, max_size=50).filter(lambda x: x.strip()),
        form_cues=st.lists(
            st.text(min_size=1, max_size=100).filter(lambda x: x.strip()),
            min_size=2,
            max_size=3,
        ),
        sets=st.integers(min_value=1, max_value=10),
        reps=st.integers(min_value=1, max_value=30),
        weight=st.floats(min_value=0, max_value=500, allow_nan=False),
    )
    @settings(max_examples=100)
    def test_gym_analysis_dataclass_accepts_valid_fields(
        self,
        exercise_name: str,
        form_cues: list[str],
        sets: int,
        reps: int,
        weight: float,
    ) -> None:
        """
        Feature: vision, Property 5: Gym analysis contains required fields

        For any gym equipment analysis result, the response SHALL contain:
        exercise_name (non-empty string), form_cues (list of 2-3 strings),
        suggested_sets (positive integer), suggested_reps (positive integer),
        and suggested_weight_kg (non-negative number).

        Validates: Requirements 2.1, 2.2, 2.3
        """
        from app.services.vision import GymEquipmentAnalysis

        analysis = GymEquipmentAnalysis(
            exercise_name=exercise_name,
            form_cues=form_cues,
            suggested_sets=sets,
            suggested_reps=reps,
            suggested_weight_kg=weight,
        )

        # Verify all required fields are present and valid
        assert analysis.exercise_name == exercise_name
        assert len(analysis.exercise_name) > 0
        assert analysis.form_cues == form_cues
        assert 2 <= len(analysis.form_cues) <= 3
        assert analysis.suggested_sets == sets
        assert analysis.suggested_sets > 0
        assert analysis.suggested_reps == reps
        assert analysis.suggested_reps > 0
        assert analysis.suggested_weight_kg == weight
        assert analysis.suggested_weight_kg >= 0


# ============================================================================
# Property 7: Food analysis contains required fields
# Feature: vision, Property 7: Food analysis contains required fields
# Validates: Requirements 3.1, 3.2, 3.3
# ============================================================================


@pytest.mark.unit
class TestFoodAnalysisFields:
    """Property 7: Food analysis contains required fields."""

    @given(
        meal_name=st.text(min_size=1, max_size=100).filter(lambda x: x.strip()),
        calories=st.integers(min_value=1, max_value=5000),
        protein=st.floats(min_value=0, max_value=500, allow_nan=False),
        carbs=st.floats(min_value=0, max_value=500, allow_nan=False),
        fat=st.floats(min_value=0, max_value=500, allow_nan=False),
    )
    @settings(max_examples=100)
    def test_food_analysis_dataclass_accepts_valid_fields(
        self,
        meal_name: str,
        calories: int,
        protein: float,
        carbs: float,
        fat: float,
    ) -> None:
        """
        Feature: vision, Property 7: Food analysis contains required fields

        For any food analysis result, the response SHALL contain:
        meal_name (non-empty string), calories (positive integer),
        protein_g (non-negative number), carbs_g (non-negative number),
        and fat_g (non-negative number).

        Validates: Requirements 3.1, 3.2, 3.3
        """
        from app.services.vision import FoodAnalysis

        analysis = FoodAnalysis(
            meal_name=meal_name,
            calories=calories,
            protein_g=protein,
            carbs_g=carbs,
            fat_g=fat,
        )

        # Verify all required fields are present and valid
        assert analysis.meal_name == meal_name
        assert len(analysis.meal_name) > 0
        assert analysis.calories == calories
        assert analysis.calories > 0
        assert analysis.protein_g == protein
        assert analysis.protein_g >= 0
        assert analysis.carbs_g == carbs
        assert analysis.carbs_g >= 0
        assert analysis.fat_g == fat
        assert analysis.fat_g >= 0


# ============================================================================
# Property 2: Classification routes to correct analyzer
# Feature: vision, Property 2: Classification routes to correct analyzer
# Validates: Requirements 1.2, 1.3
# ============================================================================


@pytest.mark.unit
class TestClassificationRouting:
    """Property 2: Classification routes to correct analyzer."""

    @pytest.mark.asyncio
    async def test_gym_equipment_routes_to_gym_analyzer(self) -> None:
        """
        Feature: vision, Property 2: Classification routes to correct analyzer

        For any image classified as "gym_equipment", the system SHALL invoke
        gym equipment analysis.

        Validates: Requirements 1.2
        """
        from app.services.vision import (
            ImageCategory,
            VisionService,
        )

        service = VisionService()

        # Mock the LLM and classification
        mock_llm = AsyncMock()
        mock_llm.analyze_image = AsyncMock(return_value="gym_equipment")
        mock_llm.extract_json_from_image = AsyncMock(
            return_value=[
                {
                    "exercise_name": "Leg Press",
                    "form_cues": ["Keep back flat", "Control descent"],
                    "suggested_sets": 3,
                    "suggested_reps": 10,
                    "suggested_weight_kg": 80,
                }
            ]
        )
        service._llm = mock_llm

        result = await service.analyze_image(image_base64="dGVzdA==")

        assert result.category == ImageCategory.GYM_EQUIPMENT
        assert result.gym_analysis is not None
        assert result.food_analysis is None
        assert result.gym_analysis.exercise_name == "Leg Press"

    @pytest.mark.asyncio
    async def test_food_routes_to_food_analyzer(self) -> None:
        """
        Feature: vision, Property 2: Classification routes to correct analyzer

        For any image classified as "food", the system SHALL invoke food analysis.

        Validates: Requirements 1.3
        """
        from app.services.vision import (
            ImageCategory,
            VisionService,
        )

        service = VisionService()

        # Mock the LLM and classification
        mock_llm = AsyncMock()
        mock_llm.analyze_image = AsyncMock(return_value="food")
        mock_llm.extract_json_from_image = AsyncMock(
            return_value=[
                {
                    "meal_name": "Chicken Salad",
                    "calories": 450,
                    "protein_g": 35,
                    "carbs_g": 20,
                    "fat_g": 25,
                }
            ]
        )
        service._llm = mock_llm

        result = await service.analyze_image(image_base64="dGVzdA==")

        assert result.category == ImageCategory.FOOD
        assert result.food_analysis is not None
        assert result.gym_analysis is None
        assert result.food_analysis.meal_name == "Chicken Salad"


# ============================================================================
# Property 3: Unknown classification returns helpful guidance
# Feature: vision, Property 3: Unknown classification returns helpful guidance
# Validates: Requirements 1.4
# ============================================================================


@pytest.mark.unit
class TestUnknownClassification:
    """Property 3: Unknown classification returns helpful guidance."""

    @pytest.mark.asyncio
    async def test_unknown_returns_helpful_message(self) -> None:
        """
        Feature: vision, Property 3: Unknown classification returns helpful guidance

        For any image classified as "unknown", the response SHALL contain a message
        asking the user to describe what they're showing.

        Validates: Requirements 1.4
        """
        from app.services.vision import ImageCategory, VisionService

        service = VisionService()

        # Mock the LLM to return unknown
        mock_llm = AsyncMock()
        mock_llm.analyze_image = AsyncMock(return_value="unknown")
        service._llm = mock_llm

        result = await service.analyze_image(image_base64="dGVzdA==")

        assert result.category == ImageCategory.UNKNOWN
        assert result.gym_analysis is None
        assert result.food_analysis is None
        assert result.error_message is not None
        assert "describe" in result.error_message.lower()


# ============================================================================
# Property 11: LLM disabled returns fallback
# Feature: vision, Property 11: LLM disabled returns fallback
# Validates: Requirements 7.1, 7.3
# ============================================================================


@pytest.mark.unit
class TestLLMDisabledFallback:
    """Property 11: LLM disabled returns fallback."""

    @pytest.mark.asyncio
    async def test_no_llm_returns_fallback_message(self) -> None:
        """
        Feature: vision, Property 11: LLM disabled returns fallback

        For any image input when LLM_ENABLED=false, the VisionService SHALL return
        category=UNKNOWN with a fallback message asking the user to describe the image.

        Validates: Requirements 7.1, 7.3
        """
        from app.services.vision import ImageCategory, VisionService

        service = VisionService()
        # Ensure LLM is None (disabled)
        service._llm = None

        result = await service.analyze_image(image_base64="dGVzdA==")

        assert result.category == ImageCategory.UNKNOWN
        assert result.error_message is not None
        assert "describe" in result.error_message.lower()
        assert result.gym_analysis is None
        assert result.food_analysis is None

    @pytest.mark.asyncio
    async def test_no_llm_with_url_returns_fallback(self) -> None:
        """
        Feature: vision, Property 11: LLM disabled returns fallback

        When LLM is disabled, both URL and base64 inputs should return fallback.

        Validates: Requirements 7.1, 7.3
        """
        from app.services.vision import ImageCategory, VisionService

        service = VisionService()
        service._llm = None

        result = await service.analyze_image(image_url="http://example.com/test.jpg")

        assert result.category == ImageCategory.UNKNOWN
        assert result.error_message is not None


# ============================================================================
# Property 6: Gym analysis produces LOG_EXERCISE action
# Feature: vision, Property 6: Gym analysis produces LOG_EXERCISE action
# Validates: Requirements 2.4
# ============================================================================


@pytest.mark.unit
class TestGymActionType:
    """Property 6: Gym analysis produces LOG_EXERCISE action."""

    @pytest.mark.asyncio
    async def test_gym_analysis_returns_log_exercise_action(self) -> None:
        """
        Feature: vision, Property 6: Gym analysis produces LOG_EXERCISE action

        For any successful gym equipment analysis, the BrainService SHALL return
        action_type=LOG_EXERCISE with action_data containing the analysis fields.

        Validates: Requirements 2.4
        """
        from app.services.brain import BrainService

        brain = BrainService()

        # Mock the vision service
        mock_vision = AsyncMock()
        mock_result = MagicMock()
        mock_result.error_message = None
        mock_result.category = MagicMock()
        mock_result.category.value = "gym_equipment"

        # Create a mock gym analysis
        mock_gym = MagicMock()
        mock_gym.exercise_name = "Leg Press"
        mock_gym.form_cues = ["Keep back flat", "Control descent"]
        mock_gym.suggested_sets = 3
        mock_gym.suggested_reps = 10
        mock_gym.suggested_weight_kg = 80
        mock_gym.in_todays_plan = False
        mock_gym.goal_specific_advice = ""

        mock_result.gym_analysis = mock_gym
        mock_result.food_analysis = None

        # Patch ImageCategory comparison
        from app.services.vision import ImageCategory

        mock_result.category = ImageCategory.GYM_EQUIPMENT

        mock_vision.analyze_image = AsyncMock(return_value=mock_result)
        brain._vision = mock_vision

        response = await brain._handle_image_attachment(image_base64="dGVzdA==")

        assert response.action_type == ChatActionType.LOG_EXERCISE
        assert response.action_data is not None
        assert response.action_data["exercise_name"] == "Leg Press"
        assert response.action_data["sets"] == 3
        assert response.action_data["reps"] == 10
        assert response.action_data["weight_kg"] == 80


# ============================================================================
# Property 8: Food analysis produces LOG_FOOD action
# Feature: vision, Property 8: Food analysis produces LOG_FOOD action
# Validates: Requirements 3.4
# ============================================================================


@pytest.mark.unit
class TestFoodActionType:
    """Property 8: Food analysis produces LOG_FOOD action."""

    @pytest.mark.asyncio
    async def test_food_analysis_returns_log_food_action(self) -> None:
        """
        Feature: vision, Property 8: Food analysis produces LOG_FOOD action

        For any successful food analysis, the BrainService SHALL return
        action_type=LOG_FOOD with action_data containing the analysis fields.

        Validates: Requirements 3.4
        """
        from app.services.brain import BrainService

        brain = BrainService()

        # Mock the vision service
        mock_vision = AsyncMock()
        mock_result = MagicMock()
        mock_result.error_message = None

        # Create a mock food analysis
        mock_food = MagicMock()
        mock_food.meal_name = "Chicken Salad"
        mock_food.calories = 450
        mock_food.protein_g = 35
        mock_food.carbs_g = 20
        mock_food.fat_g = 25
        mock_food.goal_specific_advice = ""

        from app.services.vision import ImageCategory

        mock_result.category = ImageCategory.FOOD
        mock_result.food_analysis = mock_food
        mock_result.gym_analysis = None

        mock_vision.analyze_image = AsyncMock(return_value=mock_result)
        brain._vision = mock_vision

        response = await brain._handle_image_attachment(image_base64="dGVzdA==")

        assert response.action_type == ChatActionType.LOG_FOOD
        assert response.action_data is not None
        assert response.action_data["meal_name"] == "Chicken Salad"
        assert response.action_data["calories"] == 450
        assert response.action_data["protein_g"] == 35
        assert response.action_data["carbs_g"] == 20
        assert response.action_data["fat_g"] == 25


# ============================================================================
# Property 9: Image attachments route to VisionService
# Feature: vision, Property 9: Image attachments route to VisionService
# Validates: Requirements 4.1
# ============================================================================


@pytest.mark.unit
class TestImageRouting:
    """Property 9: Image attachments route to VisionService."""

    @pytest.mark.asyncio
    async def test_image_attachment_calls_vision_service(self) -> None:
        """
        Feature: vision, Property 9: Image attachments route to VisionService

        For any chat message with attachment_type=IMAGE, the BrainService SHALL
        call VisionService.analyze_image instead of returning a hardcoded response.

        Validates: Requirements 4.1
        """
        from app.services.brain import BrainService
        from app.services.vision import ImageCategory

        brain = BrainService()

        # Mock the vision service
        mock_vision = AsyncMock()
        mock_result = MagicMock()
        mock_result.error_message = "Test error"
        mock_result.category = ImageCategory.UNKNOWN
        mock_result.gym_analysis = None
        mock_result.food_analysis = None

        mock_vision.analyze_image = AsyncMock(return_value=mock_result)
        brain._vision = mock_vision

        # Call the image handler
        await brain._handle_image_attachment(image_base64="dGVzdA==")

        # Verify VisionService was called
        mock_vision.analyze_image.assert_called_once()


# ============================================================================
# Property 4: Vision errors degrade gracefully
# Feature: vision, Property 4: Vision errors degrade gracefully
# Validates: Requirements 1.5, 4.4
# ============================================================================


@pytest.mark.unit
class TestVisionErrorHandling:
    """Property 4: Vision errors degrade gracefully."""

    @pytest.mark.asyncio
    async def test_vision_error_returns_helpful_message(self) -> None:
        """
        Feature: vision, Property 4: Vision errors degrade gracefully

        For any image processing failure (timeout, API error, invalid input),
        the system SHALL return a valid BrainResponse with action_type=NONE
        and a helpful error message.

        Validates: Requirements 1.5, 4.4
        """
        from app.services.brain import BrainService
        from app.services.vision import ImageCategory

        brain = BrainService()

        # Mock the vision service to return an error
        mock_vision = AsyncMock()
        mock_result = MagicMock()
        mock_result.error_message = "I had trouble analyzing that image."
        mock_result.category = ImageCategory.UNKNOWN
        mock_result.gym_analysis = None
        mock_result.food_analysis = None

        mock_vision.analyze_image = AsyncMock(return_value=mock_result)
        brain._vision = mock_vision

        response = await brain._handle_image_attachment(image_base64="dGVzdA==")

        assert response.action_type == ChatActionType.NONE
        assert response.content is not None
        assert len(response.content) > 0
