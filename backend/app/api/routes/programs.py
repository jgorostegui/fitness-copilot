"""
Training program endpoints.

Provides endpoints for listing and selecting training programs.
"""

import uuid

from fastapi import APIRouter, HTTPException

from app.api.deps import CurrentUser, SessionDep
from app.crud_fitness import (
    get_training_program,
    get_training_programs,
    get_training_routines_for_program,
    select_training_program,
)
from app.models import (
    TrainingProgramPublic,
    TrainingProgramsPublic,
    TrainingRoutinePublic,
    TrainingRoutinesPublic,
    UserProfilePublic,
)

router = APIRouter(prefix="/programs", tags=["programs"])


@router.get("", response_model=TrainingProgramsPublic)
def list_training_programs(session: SessionDep) -> TrainingProgramsPublic:
    """
    List all available training programs.
    
    Returns predefined training programs (4, 5, 6 days/week options).
    """
    programs = get_training_programs(session)
    return TrainingProgramsPublic(
        data=[
            TrainingProgramPublic(
                id=p.id,
                name=p.name,
                description=p.description,
                days_per_week=p.days_per_week,
                difficulty=p.difficulty,
            )
            for p in programs
        ],
        count=len(programs),
    )


@router.post("/{program_id}/select", response_model=UserProfilePublic)
def select_program(
    session: SessionDep,
    current_user: CurrentUser,
    program_id: uuid.UUID,
) -> UserProfilePublic:
    """
    Select a training program for the current user.
    
    Associates the specified program with the user's profile.
    """
    user = select_training_program(session, current_user, program_id)
    if user is None:
        raise HTTPException(status_code=404, detail="Training program not found")
    
    return UserProfilePublic(
        id=user.id,
        email=user.email,
        age=user.age,
        sex=user.sex,
        weight_kg=user.weight_kg,
        height_cm=user.height_cm,
        body_fat_percentage=user.body_fat_percentage,
        goal_method=user.goal_method,
        goal_weight_kg=user.goal_weight_kg,
        activity_level=user.activity_level,
        selected_program_id=user.selected_program_id,
        protein_g_per_kg=user.protein_g_per_kg,
        fat_rest_g_per_kg=user.fat_rest_g_per_kg,
        fat_train_g_per_kg=user.fat_train_g_per_kg,
        onboarding_complete=user.onboarding_complete,
    )


@router.get("/{program_id}/routines", response_model=TrainingRoutinesPublic)
def get_program_routines(
    session: SessionDep,
    program_id: uuid.UUID,
    day_of_week: int | None = None,
) -> TrainingRoutinesPublic:
    """
    Get routines for a specific training program.
    
    Optionally filter by day of week (0=Monday, 6=Sunday).
    """
    program = get_training_program(session, program_id)
    if program is None:
        raise HTTPException(status_code=404, detail="Training program not found")
    
    routines = get_training_routines_for_program(session, program_id, day_of_week)
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
