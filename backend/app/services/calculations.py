"""
Calculation services for body metrics and energy expenditure.

Implements formulas for BMI, BMR, TDEE, NEAT, Energy Availability, and projections.
"""

from app.models import (
    ActivityLevel,
    BodyMetrics,
    EnergyAvailability,
    EnergyMetrics,
    GoalMethod,
    ProfileMetrics,
    User,
    WeeklySummary,
)

# Activity level multipliers for TDEE calculation
ACTIVITY_MULTIPLIERS: dict[ActivityLevel, float] = {
    ActivityLevel.SEDENTARY: 1.20,
    ActivityLevel.LIGHTLY_ACTIVE: 1.375,
    ActivityLevel.MODERATELY_ACTIVE: 1.55,
    ActivityLevel.VERY_ACTIVE: 1.725,
    ActivityLevel.SUPER_ACTIVE: 1.90,
}

# Goal method weekly weight change in kg
GOAL_WEEKLY_CHANGE: dict[GoalMethod, float] = {
    GoalMethod.MAINTENANCE: 0.0,
    GoalMethod.VERY_SLOW_CUT: -0.2,
    GoalMethod.SLOW_CUT: -0.25,
    GoalMethod.STANDARD_CUT: -0.5,
    GoalMethod.AGGRESSIVE_CUT: -0.75,
    GoalMethod.VERY_AGGRESSIVE_CUT: -1.0,
    GoalMethod.SLOW_GAIN: 0.25,
    GoalMethod.MODERATE_GAIN: 0.5,
    GoalMethod.CUSTOM: 0.0,  # Uses custom_kg_per_week
}

# Calories per kg of body weight change (approximate)
KCAL_PER_KG = 7700


class CalculationService:
    """Service for calculating body and energy metrics."""

    @staticmethod
    def calculate_bmi(weight_kg: float, height_cm: int) -> float:
        """
        Calculate Body Mass Index.

        BMI = weight (kg) / height (m)^2
        """
        height_m = height_cm / 100
        return round(weight_kg / (height_m**2), 1)

    @staticmethod
    def get_bmi_status(bmi: float) -> str:
        """Get BMI status category."""
        if bmi < 18.5:
            return "underweight"
        elif bmi < 25:
            return "normal"
        elif bmi < 30:
            return "overweight"
        else:
            return "obese"

    @staticmethod
    def calculate_fat_mass(weight_kg: float, body_fat_percentage: float) -> float:
        """Calculate fat mass in kg."""
        return round(weight_kg * (body_fat_percentage / 100), 1)

    @staticmethod
    def calculate_ffm(weight_kg: float, body_fat_percentage: float) -> float:
        """Calculate Fat-Free Mass (FFM) in kg."""
        fat_mass = weight_kg * (body_fat_percentage / 100)
        return round(weight_kg - fat_mass, 1)

    @staticmethod
    def calculate_bmr_mifflin_st_jeor(
        weight_kg: float, height_cm: int, age: int, sex: str
    ) -> int:
        """
        Calculate BMR using Mifflin-St Jeor equation.

        Men: BMR = (10 × weight) + (6.25 × height) - (5 × age) + 5
        Women: BMR = (10 × weight) + (6.25 × height) - (5 × age) - 161
        """
        base = (10 * weight_kg) + (6.25 * height_cm) - (5 * age)
        if sex.lower() == "male":
            return int(base + 5)
        else:
            return int(base - 161)

    @staticmethod
    def calculate_bmr_katch_mcardle(
        weight_kg: float, body_fat_percentage: float
    ) -> int:
        """
        Calculate BMR using Katch-McArdle equation.

        BMR = 370 + (21.6 × FFM)

        More accurate when body fat percentage is known.
        """
        ffm = weight_kg * (1 - body_fat_percentage / 100)
        return int(370 + (21.6 * ffm))

    @staticmethod
    def get_activity_multiplier(activity_level: ActivityLevel | None) -> float:
        """Get TDEE multiplier for activity level."""
        if activity_level is None:
            return ACTIVITY_MULTIPLIERS[ActivityLevel.SEDENTARY]
        return ACTIVITY_MULTIPLIERS.get(
            activity_level, ACTIVITY_MULTIPLIERS[ActivityLevel.SEDENTARY]
        )

    @staticmethod
    def calculate_tdee(bmr: int, activity_multiplier: float) -> int:
        """Calculate Total Daily Energy Expenditure."""
        return int(bmr * activity_multiplier)

    @staticmethod
    def calculate_neat(bmr: int, activity_multiplier: float) -> int:
        """
        Calculate Non-Exercise Activity Thermogenesis.

        NEAT = TDEE - BMR (simplified approximation)
        """
        tdee = int(bmr * activity_multiplier)
        return tdee - bmr

    @staticmethod
    def get_weekly_weight_change(
        goal_method: GoalMethod | None, custom_kg_per_week: float | None = None
    ) -> float:
        """Get target weekly weight change in kg."""
        if goal_method is None:
            return 0.0
        if goal_method == GoalMethod.CUSTOM and custom_kg_per_week is not None:
            return custom_kg_per_week
        return GOAL_WEEKLY_CHANGE.get(goal_method, 0.0)

    @staticmethod
    def calculate_daily_deficit(weekly_weight_change_kg: float) -> int:
        """
        Calculate daily caloric deficit/surplus.

        1 kg of body weight ≈ 7700 kcal
        """
        weekly_kcal = weekly_weight_change_kg * KCAL_PER_KG
        return int(weekly_kcal / 7)

    @staticmethod
    def calculate_energy_availability(
        daily_calories: int, ffm_kg: float | None
    ) -> tuple[float | None, str]:
        """
        Calculate Energy Availability (EA).

        EA = (Energy Intake - Exercise Energy Expenditure) / FFM

        Thresholds:
        - >= 45 kcal/kg FFM: Optimal
        - 30-45 kcal/kg FFM: Functional
        - < 30 kcal/kg FFM: Low EA (risk of health issues)
        """
        if ffm_kg is None or ffm_kg <= 0:
            return None, "need_bf"

        ea = daily_calories / ffm_kg

        if ea >= 45:
            status = "optimal"
        elif ea >= 30:
            status = "functional"
        else:
            status = "low_ea"

        return round(ea, 1), status

    @classmethod
    def calculate_body_metrics(cls, user: User) -> BodyMetrics | None:
        """Calculate body composition metrics for a user."""
        if user.weight_kg is None or user.height_cm is None:
            return None

        bmi = cls.calculate_bmi(user.weight_kg, user.height_cm)
        bmi_status = cls.get_bmi_status(bmi)

        ffm_kg = None
        fat_mass_kg = None
        if user.body_fat_percentage is not None:
            ffm_kg = cls.calculate_ffm(user.weight_kg, user.body_fat_percentage)
            fat_mass_kg = cls.calculate_fat_mass(
                user.weight_kg, user.body_fat_percentage
            )

        return BodyMetrics(
            weight_kg=user.weight_kg,
            height_cm=user.height_cm,
            bmi=bmi,
            bmi_status=bmi_status,
            ffm_kg=ffm_kg,
            fat_mass_kg=fat_mass_kg,
        )

    @classmethod
    def calculate_energy_metrics(cls, user: User) -> EnergyMetrics | None:
        """Calculate energy expenditure metrics for a user."""
        if (
            user.weight_kg is None
            or user.height_cm is None
            or user.age is None
            or user.sex is None
        ):
            return None

        # Choose BMR equation based on available data
        if user.body_fat_percentage is not None:
            bmr = cls.calculate_bmr_katch_mcardle(
                user.weight_kg, user.body_fat_percentage
            )
            bmr_equation = "katch_mcardle"
        else:
            bmr = cls.calculate_bmr_mifflin_st_jeor(
                user.weight_kg, user.height_cm, user.age, user.sex
            )
            bmr_equation = "mifflin_st_jeor"

        activity_multiplier = cls.get_activity_multiplier(user.activity_level)
        base_tdee = cls.calculate_tdee(bmr, activity_multiplier)
        neat = cls.calculate_neat(bmr, activity_multiplier)

        # Calculate deficit based on goal
        weekly_change = cls.get_weekly_weight_change(
            user.goal_method, user.custom_kg_per_week
        )
        daily_deficit = cls.calculate_daily_deficit(weekly_change)

        # Handle custom kcal per day override
        if user.custom_kcal_per_day is not None:
            estimated_daily_calories = user.custom_kcal_per_day
            daily_deficit = base_tdee - estimated_daily_calories
        else:
            estimated_daily_calories = (
                base_tdee + daily_deficit
            )  # deficit is negative for cuts

        return EnergyMetrics(
            bmr=bmr,
            bmr_equation=bmr_equation,
            activity_multiplier=activity_multiplier,
            neat=neat,
            base_tdee=base_tdee,
            daily_deficit=abs(daily_deficit),
            estimated_daily_calories=max(estimated_daily_calories, 0),
        )

    @classmethod
    def calculate_energy_availability_metrics(
        cls, user: User, energy_metrics: EnergyMetrics | None
    ) -> EnergyAvailability:
        """Calculate Energy Availability metrics."""
        if energy_metrics is None:
            return EnergyAvailability(ea_kcal_per_kg_ffm=None, ea_status="need_bf")

        ffm_kg = None
        if user.weight_kg is not None and user.body_fat_percentage is not None:
            ffm_kg = cls.calculate_ffm(user.weight_kg, user.body_fat_percentage)

        ea, status = cls.calculate_energy_availability(
            energy_metrics.estimated_daily_calories, ffm_kg
        )

        return EnergyAvailability(ea_kcal_per_kg_ffm=ea, ea_status=status)

    @classmethod
    def calculate_weekly_summary(
        cls, user: User, energy_metrics: EnergyMetrics | None
    ) -> WeeklySummary:
        """Calculate weekly projection metrics."""
        if energy_metrics is None:
            return WeeklySummary(
                weekly_deficit_kcal=0,
                expected_loss_kg_per_week=0.0,
                monthly_loss_kg=0.0,
                total_to_goal_kg=None,
            )

        weekly_deficit = energy_metrics.daily_deficit * 7
        expected_weekly_change = weekly_deficit / KCAL_PER_KG
        monthly_change = expected_weekly_change * 4.33  # Average weeks per month

        total_to_goal = None
        if user.weight_kg is not None and user.goal_weight_kg is not None:
            total_to_goal = round(abs(user.weight_kg - user.goal_weight_kg), 1)

        return WeeklySummary(
            weekly_deficit_kcal=weekly_deficit,
            expected_loss_kg_per_week=round(expected_weekly_change, 2),
            monthly_loss_kg=round(monthly_change, 1),
            total_to_goal_kg=total_to_goal,
        )

    @classmethod
    def calculate_profile_metrics(cls, user: User) -> ProfileMetrics | None:
        """Calculate all profile metrics for a user."""
        body_metrics = cls.calculate_body_metrics(user)
        if body_metrics is None:
            return None

        energy_metrics = cls.calculate_energy_metrics(user)
        if energy_metrics is None:
            return None

        energy_availability = cls.calculate_energy_availability_metrics(
            user, energy_metrics
        )
        weekly_summary = cls.calculate_weekly_summary(user, energy_metrics)

        return ProfileMetrics(
            body_metrics=body_metrics,
            energy_metrics=energy_metrics,
            energy_availability=energy_availability,
            weekly_summary=weekly_summary,
        )
