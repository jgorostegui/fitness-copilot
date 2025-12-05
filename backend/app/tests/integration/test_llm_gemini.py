"""
Integration tests for Google Gemini LLM provider.

These tests hit the live Gemini API and are skipped by default.
Run with: RUN_INTEGRATION_TESTS=1 uv run pytest -m integration
"""

from __future__ import annotations

import base64
import os
from pathlib import Path

import pytest

# Skip all tests in this module unless RUN_INTEGRATION_TESTS is set
pytestmark = [
    pytest.mark.integration,
    pytest.mark.skipif(
        not os.getenv("RUN_INTEGRATION_TESTS"),
        reason="Integration tests skipped by default. Set RUN_INTEGRATION_TESTS=1 to run.",
    ),
]

# Path to demo images (relative to project root)
DEMO_IMAGES_DIR = Path(__file__).parent.parent.parent.parent.parent / "demo-images"


@pytest.fixture
def llm_provider():
    """Get a configured LLM provider for testing."""
    from app.llm.google import GoogleLLMProvider

    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        pytest.skip("GOOGLE_API_KEY not set")

    return GoogleLLMProvider(model="gemini-2.5-flash")


@pytest.fixture
def leg_press_image_base64() -> str:
    """Load leg-press.jpg as base64."""
    image_path = DEMO_IMAGES_DIR / "leg-press.jpg"
    if not image_path.exists():
        pytest.skip(f"Demo image not found: {image_path}")
    with open(image_path, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")


@pytest.fixture
def food_image_base64() -> str:
    """Load salad-chicken-breasts.jpg as base64."""
    image_path = DEMO_IMAGES_DIR / "salad-chicken-breasts.jpg"
    if not image_path.exists():
        pytest.skip(f"Demo image not found: {image_path}")
    with open(image_path, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")


@pytest.mark.asyncio
async def test_gemini_health_check(llm_provider):
    """Test that the Gemini API is reachable."""
    is_healthy = await llm_provider.is_healthy()
    assert is_healthy is True


@pytest.mark.asyncio
async def test_gemini_generate_text(llm_provider):
    """Test basic text generation."""
    prompt = "Say 'hello world' and nothing else."
    result = await llm_provider.generate(prompt, timeout_s=30.0)

    assert result is not None
    assert "hello" in result.lower()


@pytest.mark.asyncio
async def test_gemini_extract_json(llm_provider):
    """Test JSON extraction from structured prompt."""
    prompt = """
    Return a JSON object with the following structure:
    {"name": "test", "value": 42}

    Return ONLY the JSON, no other text.
    """
    result = await llm_provider.extract_json(prompt, timeout_s=30.0)

    assert isinstance(result, list)
    assert len(result) > 0
    assert "name" in result[0]
    assert "value" in result[0]


# =============================================================================
# Vision Integration Tests
# =============================================================================


@pytest.mark.asyncio
async def test_vision_analyze_gym_equipment_image(llm_provider, leg_press_image_base64):
    """Test that Gemini can analyze a gym equipment image."""
    prompt = """Analyze this image and classify it into exactly one category:
- "gym_equipment": gym machines, weights, exercise equipment
- "food": meals, snacks, ingredients, drinks
- "unknown": anything else

Respond with ONLY the category name, nothing else."""

    result = await llm_provider.analyze_image(
        prompt=prompt,
        image_base64=leg_press_image_base64,
        timeout_s=30.0,
    )

    print(f"\n[LLM] Gym classification result: {result}")

    assert result is not None
    result_lower = result.lower().strip()
    # Should classify as gym equipment
    assert (
        "gym" in result_lower or "equipment" in result_lower
    ), f"Expected gym_equipment, got: {result}"


@pytest.mark.asyncio
async def test_vision_analyze_food_image(llm_provider, food_image_base64):
    """Test that Gemini can analyze a food image."""
    prompt = """Analyze this image and classify it into exactly one category:
- "gym_equipment": gym machines, weights, exercise equipment
- "food": meals, snacks, ingredients, drinks
- "unknown": anything else

Respond with ONLY the category name, nothing else."""

    result = await llm_provider.analyze_image(
        prompt=prompt,
        image_base64=food_image_base64,
        timeout_s=30.0,
    )

    print(f"\n[LLM] Food classification result: {result}")

    assert result is not None
    result_lower = result.lower().strip()
    # Should classify as food
    assert "food" in result_lower, f"Expected food, got: {result}"


@pytest.mark.asyncio
async def test_vision_extract_gym_analysis_json(llm_provider, leg_press_image_base64):
    """Test that Gemini can extract structured gym analysis from image."""
    prompt = """Analyze this gym equipment image.

Identify the exercise and provide guidance.

Respond in JSON format ONLY (no markdown, no explanation):
{"exercise_name": "Name of exercise", "form_cues": ["Tip 1", "Tip 2"], "suggested_sets": 3, "suggested_reps": 10, "suggested_weight_kg": 0}"""

    result = await llm_provider.extract_json_from_image(
        prompt=prompt,
        image_base64=leg_press_image_base64,
        timeout_s=30.0,
    )

    print(f"\n[LLM] Gym analysis JSON: {result}")

    assert isinstance(result, list)
    assert len(result) > 0
    data = result[0]

    # Verify required fields
    assert "exercise_name" in data
    assert isinstance(data["exercise_name"], str)
    assert len(data["exercise_name"]) > 0

    assert "form_cues" in data
    assert isinstance(data["form_cues"], list)

    assert "suggested_sets" in data
    assert isinstance(data["suggested_sets"], int)

    assert "suggested_reps" in data
    assert isinstance(data["suggested_reps"], int)

    # Should identify as leg press or similar
    exercise_lower = data["exercise_name"].lower()
    assert (
        "leg" in exercise_lower or "press" in exercise_lower
    ), f"Expected leg press, got: {data['exercise_name']}"


@pytest.mark.asyncio
async def test_vision_extract_food_analysis_json(llm_provider, food_image_base64):
    """Test that Gemini can extract structured food analysis from image."""
    prompt = """Analyze this food image.

Estimate the nutritional content of this meal.

Respond in JSON format ONLY (no markdown, no explanation):
{"meal_name": "Description", "calories": 500, "protein_g": 30, "carbs_g": 40, "fat_g": 20}"""

    result = await llm_provider.extract_json_from_image(
        prompt=prompt,
        image_base64=food_image_base64,
        timeout_s=30.0,
    )

    print(f"\n[LLM] Food analysis JSON: {result}")

    assert isinstance(result, list)
    assert len(result) > 0
    data = result[0]

    # Verify required fields
    assert "meal_name" in data
    assert isinstance(data["meal_name"], str)
    assert len(data["meal_name"]) > 0

    assert "calories" in data
    assert isinstance(data["calories"], int | float)
    assert data["calories"] > 0

    assert "protein_g" in data
    assert isinstance(data["protein_g"], int | float)
    assert data["protein_g"] >= 0

    assert "carbs_g" in data
    assert isinstance(data["carbs_g"], int | float)

    assert "fat_g" in data
    assert isinstance(data["fat_g"], int | float)

    # Should identify chicken/salad
    meal_lower = data["meal_name"].lower()
    assert (
        "chicken" in meal_lower or "salad" in meal_lower or "breast" in meal_lower
    ), f"Expected chicken salad, got: {data['meal_name']}"


@pytest.mark.asyncio
async def test_vision_service_full_flow_gym(llm_provider, leg_press_image_base64):
    """Test the full VisionService flow with gym equipment image."""
    from app.services.vision import ImageCategory, VisionService

    vision = VisionService()
    # Inject the provider to avoid creating a new one
    vision._llm = llm_provider

    result = await vision.analyze_image(image_base64=leg_press_image_base64)

    print(
        f"\n[VisionService] Gym result: category={result.category}, exercise={result.gym_analysis.exercise_name if result.gym_analysis else None}"
    )
    if result.gym_analysis:
        print(f"[VisionService] Form cues: {result.gym_analysis.form_cues}")
        print(
            f"[VisionService] Sets/Reps/Weight: {result.gym_analysis.suggested_sets}x{result.gym_analysis.suggested_reps} @ {result.gym_analysis.suggested_weight_kg}kg"
        )

    assert result.category == ImageCategory.GYM_EQUIPMENT
    assert result.gym_analysis is not None
    assert result.error_message is None

    # Verify gym analysis fields
    ga = result.gym_analysis
    assert len(ga.exercise_name) > 0
    assert len(ga.form_cues) >= 1
    assert ga.suggested_sets > 0
    assert ga.suggested_reps > 0


@pytest.mark.asyncio
async def test_vision_service_full_flow_food(llm_provider, food_image_base64):
    """Test the full VisionService flow with food image."""
    from app.services.vision import ImageCategory, VisionService

    vision = VisionService()
    # Inject the provider to avoid creating a new one
    vision._llm = llm_provider

    result = await vision.analyze_image(image_base64=food_image_base64)

    print(
        f"\n[VisionService] Food result: category={result.category}, meal={result.food_analysis.meal_name if result.food_analysis else None}"
    )
    if result.food_analysis:
        print(
            f"[VisionService] Macros: {result.food_analysis.calories}kcal, {result.food_analysis.protein_g}g protein, {result.food_analysis.carbs_g}g carbs, {result.food_analysis.fat_g}g fat"
        )

    assert result.category == ImageCategory.FOOD
    assert result.food_analysis is not None
    assert result.error_message is None

    # Verify food analysis fields
    fa = result.food_analysis
    assert len(fa.meal_name) > 0
    assert fa.calories > 0
    assert fa.protein_g >= 0
    assert fa.carbs_g >= 0
    assert fa.fat_g >= 0
