"""
Profile management endpoints.

Provides endpoints for viewing and updating user profile and metrics.
"""

from fastapi import APIRouter, HTTPException

from app.api.deps import CurrentUser, SessionDep
from app.models import (
    ProfileMetrics,
    SimulatedDayResponse,
    SimulatedDayUpdate,
    UserProfilePublic,
    UserProfileUpdate,
)
from app.services.calculations import CalculationService

# Day names for simulated day
DAY_NAMES = [
    "Monday",
    "Tuesday",
    "Wednesday",
    "Thursday",
    "Friday",
    "Saturday",
    "Sunday",
]

router = APIRouter(prefix="/profile", tags=["profile"])


@router.get("/me", response_model=UserProfilePublic)
def get_current_user_profile(current_user: CurrentUser) -> UserProfilePublic:
    """
    Get current user's profile.

    Returns the authenticated user's profile information.
    """
    return UserProfilePublic(
        id=current_user.id,
        email=current_user.email,
        age=current_user.age,
        sex=current_user.sex,
        weight_kg=current_user.weight_kg,
        height_cm=current_user.height_cm,
        body_fat_percentage=current_user.body_fat_percentage,
        goal_method=current_user.goal_method,
        goal_weight_kg=current_user.goal_weight_kg,
        activity_level=current_user.activity_level,
        selected_program_id=current_user.selected_program_id,
        protein_g_per_kg=current_user.protein_g_per_kg,
        fat_rest_g_per_kg=current_user.fat_rest_g_per_kg,
        fat_train_g_per_kg=current_user.fat_train_g_per_kg,
        onboarding_complete=current_user.onboarding_complete,
        simulated_day=current_user.simulated_day,
    )


@router.put("/me", response_model=UserProfilePublic)
def update_current_user_profile(
    session: SessionDep,
    current_user: CurrentUser,
    profile_update: UserProfileUpdate,
) -> UserProfilePublic:
    """
    Update current user's profile.

    Updates the authenticated user's profile with the provided data.
    Only fields that are explicitly set will be updated.
    """
    update_data = profile_update.model_dump(exclude_unset=True)

    for field, value in update_data.items():
        setattr(current_user, field, value)

    session.add(current_user)
    session.commit()
    session.refresh(current_user)

    return UserProfilePublic(
        id=current_user.id,
        email=current_user.email,
        age=current_user.age,
        sex=current_user.sex,
        weight_kg=current_user.weight_kg,
        height_cm=current_user.height_cm,
        body_fat_percentage=current_user.body_fat_percentage,
        goal_method=current_user.goal_method,
        goal_weight_kg=current_user.goal_weight_kg,
        activity_level=current_user.activity_level,
        selected_program_id=current_user.selected_program_id,
        protein_g_per_kg=current_user.protein_g_per_kg,
        fat_rest_g_per_kg=current_user.fat_rest_g_per_kg,
        fat_train_g_per_kg=current_user.fat_train_g_per_kg,
        onboarding_complete=current_user.onboarding_complete,
        simulated_day=current_user.simulated_day,
    )


@router.get("/me/metrics", response_model=ProfileMetrics)
def get_current_user_metrics(current_user: CurrentUser) -> ProfileMetrics:
    """
    Get current user's calculated metrics.

    Returns calculated body metrics, energy metrics, energy availability,
    and weekly projections based on the user's profile data.

    Requires weight, height, age, and sex to be set in the profile.
    """
    metrics = CalculationService.calculate_profile_metrics(current_user)

    if metrics is None:
        raise HTTPException(
            status_code=400,
            detail="Profile incomplete. Please set weight, height, age, and sex.",
        )

    return metrics


@router.get("/me/day", response_model=SimulatedDayResponse)
def get_simulated_day(current_user: CurrentUser) -> SimulatedDayResponse:
    """
    Get current user's simulated day.

    Returns the simulated day number (0-6) and day name (Monday-Sunday).
    Used for demo purposes to test different days in the weekly plan.
    """
    return SimulatedDayResponse(
        simulated_day=current_user.simulated_day,
        day_name=DAY_NAMES[current_user.simulated_day],
    )


@router.put("/me/day", response_model=SimulatedDayResponse)
def update_simulated_day(
    session: SessionDep,
    current_user: CurrentUser,
    day_update: SimulatedDayUpdate,
) -> SimulatedDayResponse:
    """
    Update current user's simulated day.

    Sets the simulated day (0-6) for demo purposes.
    This affects which day's meal plan and training routine are shown.
    """
    current_user.simulated_day = day_update.simulated_day
    session.add(current_user)
    session.commit()
    session.refresh(current_user)

    return SimulatedDayResponse(
        simulated_day=current_user.simulated_day,
        day_name=DAY_NAMES[current_user.simulated_day],
    )
