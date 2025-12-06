"""
Daily summary endpoint.

Provides endpoint for viewing daily progress metrics.
"""

from fastapi import APIRouter

from app.api.deps import CurrentUser, SessionDep
from app.crud_fitness import get_exercise_logs_for_simulated_day
from app.crud_nutrition import get_meal_logs_for_simulated_day, get_meal_plans_for_user
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
    # Get logs for the user's current simulated day
    simulated_day = current_user.simulated_day
    meal_logs = get_meal_logs_for_simulated_day(session, current_user.id, simulated_day)
    exercise_logs = get_exercise_logs_for_simulated_day(
        session, current_user.id, simulated_day
    )

    # Calculate consumed totals
    calories_consumed = sum(m.calories for m in meal_logs)
    protein_consumed = sum(m.protein_g for m in meal_logs)

    # Count unique exercises as workouts
    workouts_completed = len(exercise_logs)

    # Calculate targets - prefer meal plan totals, fall back to calculated
    meal_plans = get_meal_plans_for_user(
        session, current_user.id, day_of_week=simulated_day
    )

    if meal_plans:
        calories_target = sum(mp.calories for mp in meal_plans)
        protein_target = sum(mp.protein_g for mp in meal_plans)
    else:
        # Fall back to calculated targets from user profile
        energy_metrics = CalculationService.calculate_energy_metrics(current_user)
        if energy_metrics is not None:
            calories_target = energy_metrics.estimated_daily_calories
        else:
            calories_target = 2000  # Default

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
