"""
Plan endpoints for today's meal and training plans.

Provides endpoints for viewing today's scheduled meals and exercises.
Uses simulated_day from user profile for demo purposes.
"""

from fastapi import APIRouter

from app.api.deps import CurrentUser, SessionDep
from app.crud_fitness import get_training_routines_for_program
from app.crud_nutrition import get_meal_plans_for_user
from app.models import (
    MealPlanPublic,
    MealPlansPublic,
    TrainingRoutinePublic,
    TrainingRoutinesPublic,
)

router = APIRouter(prefix="/plans", tags=["plans"])


@router.get("/training/today", response_model=TrainingRoutinesPublic)
def get_todays_training(
    session: SessionDep,
    current_user: CurrentUser,
) -> TrainingRoutinesPublic:
    """
    Get today's training routine.

    Returns exercises from the user's selected program for the simulated day.
    Uses simulated_day from user profile (for demo purposes).
    Returns empty list if no program is selected.
    """
    if current_user.selected_program_id is None:
        return TrainingRoutinesPublic(data=[], count=0)

    # Use simulated_day instead of real day for demo purposes
    simulated_day = current_user.simulated_day
    routines = get_training_routines_for_program(
        session, current_user.selected_program_id, day_of_week=simulated_day
    )

    return TrainingRoutinesPublic(
        data=[
            TrainingRoutinePublic(
                id=r.id,
                program_id=r.program_id,
                day_of_week=r.day_of_week,
                exercise_name=r.exercise_name,
                machine_hint=r.machine_hint,
                sets=r.sets,
                reps=r.reps,
                target_load_kg=r.target_load_kg,
            )
            for r in routines
        ],
        count=len(routines),
    )


@router.get("/meal/today", response_model=MealPlansPublic)
def get_todays_meal_plan(
    session: SessionDep,
    current_user: CurrentUser,
) -> MealPlansPublic:
    """
    Get today's meal plan.

    Returns meal plan items for the simulated day.
    Uses simulated_day from user profile (for demo purposes).
    """
    # Use simulated_day instead of real day for demo purposes
    simulated_day = current_user.simulated_day
    meals = get_meal_plans_for_user(session, current_user.id, day_of_week=simulated_day)

    return MealPlansPublic(
        data=[
            MealPlanPublic(
                id=m.id,
                day_of_week=m.day_of_week,
                meal_type=m.meal_type,
                item_name=m.item_name,
                calories=m.calories,
                protein_g=m.protein_g,
                carbs_g=m.carbs_g,
                fat_g=m.fat_g,
            )
            for m in meals
        ],
        count=len(meals),
    )
