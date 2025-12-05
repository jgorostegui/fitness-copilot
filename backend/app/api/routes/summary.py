"""
Daily summary endpoint.

Provides endpoint for viewing daily progress metrics.
"""

from fastapi import APIRouter

from app.api.deps import CurrentUser, SessionDep
from app.crud_fitness import get_exercise_logs_for_today
from app.crud_nutrition import get_meal_logs_for_today
from app.models import DailySummary
from app.services.calculations import CalculationService

router = APIRouter(prefix="/summary", tags=["summary"])


@router.get("/today", response_model=DailySummary)
def get_todays_summary(
    session: SessionDep,
    current_user: CurrentUser,
) -> DailySummary:
    """
    Get today's daily summary.

    Returns calculated metrics including:
    - Total calories consumed
    - Total protein consumed
    - Number of workouts completed
    - Calories remaining (target - consumed)
    - Protein remaining (target - consumed)
    """
    # Get today's logs
    meal_logs = get_meal_logs_for_today(session, current_user.id)
    exercise_logs = get_exercise_logs_for_today(session, current_user.id)

    # Calculate consumed totals
    calories_consumed = sum(m.calories for m in meal_logs)
    protein_consumed = sum(m.protein_g for m in meal_logs)

    # Count unique exercises as workouts
    workouts_completed = len(exercise_logs)

    # Calculate targets from user profile
    energy_metrics = CalculationService.calculate_energy_metrics(current_user)

    if energy_metrics is not None:
        calories_target = energy_metrics.estimated_daily_calories
    else:
        # Default target if profile incomplete
        calories_target = 2000

    # Calculate protein target (protein_g_per_kg * weight)
    if current_user.weight_kg is not None:
        protein_target = current_user.protein_g_per_kg * current_user.weight_kg
    else:
        protein_target = 150.0  # Default

    # Calculate remaining
    calories_remaining = calories_target - calories_consumed
    protein_remaining = protein_target - protein_consumed

    return DailySummary(
        calories_consumed=calories_consumed,
        calories_target=calories_target,
        protein_consumed=protein_consumed,
        protein_target=protein_target,
        workouts_completed=workouts_completed,
        calories_remaining=calories_remaining,
        protein_remaining=protein_remaining,
    )
