"""
Daily logging endpoints.

Provides endpoints for logging meals and exercises.
"""

from fastapi import APIRouter

from app.api.deps import CurrentUser, SessionDep
from app.crud_fitness import create_exercise_log, get_exercise_logs_for_today
from app.crud_nutrition import create_meal_log, get_meal_logs_for_today
from app.models import (
    DailyLogsResponse,
    ExerciseLogCreate,
    ExerciseLogPublic,
    MealLogCreate,
    MealLogPublic,
)

router = APIRouter(prefix="/logs", tags=["logs"])


@router.get("/today", response_model=DailyLogsResponse)
def get_todays_logs(
    session: SessionDep,
    current_user: CurrentUser,
) -> DailyLogsResponse:
    """
    Get today's meal and exercise logs.
    
    Returns all logs created on the current date for the authenticated user.
    """
    meal_logs = get_meal_logs_for_today(session, current_user.id)
    exercise_logs = get_exercise_logs_for_today(session, current_user.id)
    
    return DailyLogsResponse(
        meal_logs=[
            MealLogPublic(
                id=m.id,
                meal_name=m.meal_name,
                meal_type=m.meal_type,
                calories=m.calories,
                protein_g=m.protein_g,
                carbs_g=m.carbs_g,
                fat_g=m.fat_g,
                logged_at=m.logged_at,
            )
            for m in meal_logs
        ],
        exercise_logs=[
            ExerciseLogPublic(
                id=e.id,
                exercise_name=e.exercise_name,
                sets=e.sets,
                reps=e.reps,
                weight_kg=e.weight_kg,
                logged_at=e.logged_at,
            )
            for e in exercise_logs
        ],
    )


@router.post("/meal", response_model=MealLogPublic)
def log_meal(
    session: SessionDep,
    current_user: CurrentUser,
    meal_log_in: MealLogCreate,
) -> MealLogPublic:
    """
    Log a meal.
    
    Creates a new meal log entry for the authenticated user.
    """
    meal_log = create_meal_log(session, current_user.id, meal_log_in)
    
    return MealLogPublic(
        id=meal_log.id,
        meal_name=meal_log.meal_name,
        meal_type=meal_log.meal_type,
        calories=meal_log.calories,
        protein_g=meal_log.protein_g,
        carbs_g=meal_log.carbs_g,
        fat_g=meal_log.fat_g,
        logged_at=meal_log.logged_at,
    )


@router.post("/exercise", response_model=ExerciseLogPublic)
def log_exercise(
    session: SessionDep,
    current_user: CurrentUser,
    exercise_log_in: ExerciseLogCreate,
) -> ExerciseLogPublic:
    """
    Log an exercise.
    
    Creates a new exercise log entry for the authenticated user.
    """
    exercise_log = create_exercise_log(session, current_user.id, exercise_log_in)
    
    return ExerciseLogPublic(
        id=exercise_log.id,
        exercise_name=exercise_log.exercise_name,
        sets=exercise_log.sets,
        reps=exercise_log.reps,
        weight_kg=exercise_log.weight_kg,
        logged_at=exercise_log.logged_at,
    )
