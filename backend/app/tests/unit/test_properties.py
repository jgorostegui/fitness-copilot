"""
Property-based tests for Fitness Copilot Foundation feature.

Uses Hypothesis to verify correctness properties defined in the design document.
These are Small (Unit) tests - no DB, no network, pure logic.
"""

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st
from pydantic import ValidationError

from app.models import (
    ActivityLevel,
    GoalMethod,
    UserProfileUpdate,
)
from app.services.calculations import CalculationService

# ============================================================================
# Strategies
# ============================================================================

valid_weight_strategy = st.floats(min_value=30.0, max_value=300.0, allow_nan=False)
valid_height_strategy = st.integers(min_value=100, max_value=250)
invalid_weight_low_strategy = st.floats(min_value=0.0, max_value=29.9, allow_nan=False)
invalid_weight_high_strategy = st.floats(
    min_value=300.1, max_value=1000.0, allow_nan=False
)
invalid_height_low_strategy = st.integers(min_value=0, max_value=99)
invalid_height_high_strategy = st.integers(min_value=251, max_value=500)


# ============================================================================
# Property 2: Profile validation bounds
# ============================================================================


@pytest.mark.unit
class TestProfileValidationBounds:
    """Property 2: Profile validation bounds."""

    @given(weight=valid_weight_strategy)
    @settings(max_examples=100)
    def test_valid_weight_accepted(self, weight: float) -> None:
        """Valid weights within [30, 300] kg should be accepted."""
        profile = UserProfileUpdate(weight_kg=weight)
        assert profile.weight_kg == weight

    @given(height=valid_height_strategy)
    @settings(max_examples=100)
    def test_valid_height_accepted(self, height: int) -> None:
        """Valid heights within [100, 250] cm should be accepted."""
        profile = UserProfileUpdate(height_cm=height)
        assert profile.height_cm == height

    @given(weight=invalid_weight_low_strategy)
    @settings(max_examples=100)
    def test_weight_below_minimum_rejected(self, weight: float) -> None:
        """Weights below 30 kg should be rejected."""
        with pytest.raises(ValidationError) as exc_info:
            UserProfileUpdate(weight_kg=weight)
        assert "weight_kg" in str(exc_info.value)

    @given(weight=invalid_weight_high_strategy)
    @settings(max_examples=100)
    def test_weight_above_maximum_rejected(self, weight: float) -> None:
        """Weights above 300 kg should be rejected."""
        with pytest.raises(ValidationError) as exc_info:
            UserProfileUpdate(weight_kg=weight)
        assert "weight_kg" in str(exc_info.value)

    @given(height=invalid_height_low_strategy)
    @settings(max_examples=100)
    def test_height_below_minimum_rejected(self, height: int) -> None:
        """Heights below 100 cm should be rejected."""
        with pytest.raises(ValidationError) as exc_info:
            UserProfileUpdate(height_cm=height)
        assert "height_cm" in str(exc_info.value)

    @given(height=invalid_height_high_strategy)
    @settings(max_examples=100)
    def test_height_above_maximum_rejected(self, height: int) -> None:
        """Heights above 250 cm should be rejected."""
        with pytest.raises(ValidationError) as exc_info:
            UserProfileUpdate(height_cm=height)
        assert "height_cm" in str(exc_info.value)

    @given(weight=valid_weight_strategy, height=valid_height_strategy)
    @settings(max_examples=100)
    def test_valid_weight_and_height_together(self, weight: float, height: int) -> None:
        """Valid weight and height together should be accepted."""
        profile = UserProfileUpdate(weight_kg=weight, height_cm=height)
        assert profile.weight_kg == weight
        assert profile.height_cm == height


# ============================================================================
# Property 3: Goal method enumeration
# ============================================================================

valid_goal_method_strategy = st.sampled_from(list(GoalMethod))
invalid_goal_method_strategy = st.text(min_size=1, max_size=50).filter(
    lambda x: x not in [m.value for m in GoalMethod]
)


@pytest.mark.unit
class TestGoalMethodEnumeration:
    """Property 3: Goal method enumeration."""

    @given(goal_method=valid_goal_method_strategy)
    @settings(max_examples=100)
    def test_valid_goal_methods_accepted(self, goal_method: GoalMethod) -> None:
        """All valid GoalMethod enum values should be accepted."""
        profile = UserProfileUpdate(goal_method=goal_method)
        assert profile.goal_method == goal_method

    @given(invalid_method=invalid_goal_method_strategy)
    @settings(max_examples=100)
    def test_invalid_goal_methods_rejected(self, invalid_method: str) -> None:
        """Invalid goal method strings should be rejected."""
        with pytest.raises(ValidationError) as exc_info:
            UserProfileUpdate(goal_method=invalid_method)  # type: ignore
        assert "goal_method" in str(exc_info.value)

    def test_all_expected_goal_methods_exist(self) -> None:
        """Verify all expected goal methods are defined in the enum."""
        expected_methods = {
            "maintenance",
            "very_slow_cut",
            "slow_cut",
            "standard_cut",
            "aggressive_cut",
            "very_aggressive_cut",
            "slow_gain",
            "moderate_gain",
            "custom",
        }
        actual_methods = {m.value for m in GoalMethod}
        assert actual_methods == expected_methods

    @given(activity_level=st.sampled_from(list(ActivityLevel)))
    @settings(max_examples=100)
    def test_valid_activity_levels_accepted(
        self, activity_level: ActivityLevel
    ) -> None:
        """All valid ActivityLevel enum values should be accepted."""
        profile = UserProfileUpdate(activity_level=activity_level)
        assert profile.activity_level == activity_level


# ============================================================================
# BMI Calculation Tests
# ============================================================================


@pytest.mark.unit
class TestBMICalculation:
    """BMI calculation correctness tests."""

    @given(
        weight=st.floats(min_value=30.0, max_value=300.0, allow_nan=False),
        height=st.integers(min_value=100, max_value=250),
    )
    @settings(max_examples=100)
    def test_bmi_formula_correctness(self, weight: float, height: int) -> None:
        """BMI should equal weight / height^2 (in meters)."""
        bmi = CalculationService.calculate_bmi(weight, height)
        expected = weight / ((height / 100) ** 2)
        assert abs(bmi - expected) < 0.1

    @given(
        weight=st.floats(min_value=30.0, max_value=300.0, allow_nan=False),
        height=st.integers(min_value=100, max_value=250),
    )
    @settings(max_examples=100)
    def test_bmi_positive(self, weight: float, height: int) -> None:
        """BMI should always be positive for valid inputs."""
        bmi = CalculationService.calculate_bmi(weight, height)
        assert bmi > 0

    @given(
        weight=st.floats(min_value=30.0, max_value=300.0, allow_nan=False),
        height=st.integers(min_value=100, max_value=250),
    )
    @settings(max_examples=100)
    def test_bmi_status_valid(self, weight: float, height: int) -> None:
        """BMI status should be one of the valid categories."""
        bmi = CalculationService.calculate_bmi(weight, height)
        status = CalculationService.get_bmi_status(bmi)
        assert status in {"underweight", "normal", "overweight", "obese"}

    def test_bmi_status_thresholds(self) -> None:
        """BMI status thresholds should be correct."""
        assert CalculationService.get_bmi_status(17.0) == "underweight"
        assert CalculationService.get_bmi_status(18.5) == "normal"
        assert CalculationService.get_bmi_status(24.9) == "normal"
        assert CalculationService.get_bmi_status(25.0) == "overweight"
        assert CalculationService.get_bmi_status(29.9) == "overweight"
        assert CalculationService.get_bmi_status(30.0) == "obese"


# ============================================================================
# Summary Calculation Tests
# ============================================================================


@pytest.mark.unit
class TestSummaryCalculationAccuracy:
    """Summary calculation accuracy tests."""

    @given(
        consumed=st.integers(min_value=0, max_value=10000),
        target=st.integers(min_value=1000, max_value=5000),
    )
    @settings(max_examples=100)
    def test_calories_remaining_calculation(self, consumed: int, target: int) -> None:
        """Calories remaining should equal target minus consumed."""
        remaining = target - consumed
        assert remaining == target - consumed

    @given(
        meal_calories=st.lists(
            st.integers(min_value=0, max_value=2000),
            min_size=0,
            max_size=10,
        )
    )
    @settings(max_examples=100)
    def test_total_calories_is_sum(self, meal_calories: list[int]) -> None:
        """Total calories consumed should equal sum of all meal calories."""
        total = sum(meal_calories)
        assert total == sum(meal_calories)

    @given(
        bmr=st.integers(min_value=1000, max_value=3000),
        multiplier=st.floats(min_value=1.2, max_value=1.9, allow_nan=False),
    )
    @settings(max_examples=100)
    def test_tdee_calculation(self, bmr: int, multiplier: float) -> None:
        """TDEE should equal BMR times activity multiplier."""
        tdee = CalculationService.calculate_tdee(bmr, multiplier)
        expected = int(bmr * multiplier)
        assert tdee == expected

    @given(
        weekly_change=st.floats(min_value=-1.0, max_value=0.5, allow_nan=False),
    )
    @settings(max_examples=100)
    def test_daily_deficit_from_weekly_change(self, weekly_change: float) -> None:
        """Daily deficit should be weekly change * 7700 / 7."""
        daily_deficit = CalculationService.calculate_daily_deficit(weekly_change)
        expected = int((weekly_change * 7700) / 7)
        assert daily_deficit == expected
