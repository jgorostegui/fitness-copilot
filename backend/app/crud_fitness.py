"""
CRUD operations for fitness/training features.

Includes: Training programs, training routines, exercise logs.
"""

import uuid
from datetime import datetime, time

from sqlmodel import Session, select

from app.models import (
    ExerciseLog,
    ExerciseLogCreate,
    TrainingProgram,
    TrainingRoutine,
    User,
)

# ============================================================================
# Training Programs (shared across all users)
# ============================================================================


def get_training_programs(session: Session) -> list[TrainingProgram]:
    """Get all available training programs."""
    statement = select(TrainingProgram)
    return list(session.exec(statement).all())


def get_training_program(
    session: Session, program_id: uuid.UUID
) -> TrainingProgram | None:
    """Get a training program by ID."""
    return session.get(TrainingProgram, program_id)


def get_training_routines_for_program(
    session: Session, program_id: uuid.UUID, day_of_week: int | None = None
) -> list[TrainingRoutine]:
    """Get training routines for a program, optionally filtered by day."""
    statement = select(TrainingRoutine).where(TrainingRoutine.program_id == program_id)
    if day_of_week is not None:
        statement = statement.where(TrainingRoutine.day_of_week == day_of_week)
    return list(session.exec(statement).all())


def select_training_program(
    session: Session, user: User, program_id: uuid.UUID
) -> User | None:
    """Select a training program for a user."""
    program = get_training_program(session, program_id)
    if program is None:
        return None

    user.selected_program_id = program_id
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


# ============================================================================
# Exercise Logs (tenant-isolated)
# ============================================================================


def create_exercise_log(
    session: Session,
    user_id: uuid.UUID,
    exercise_log_in: ExerciseLogCreate,
    simulated_day: int = 0,
) -> ExerciseLog:
    """Create an exercise log for a user on a specific simulated day."""
    exercise_log = ExerciseLog(
        user_id=user_id,
        exercise_name=exercise_log_in.exercise_name,
        sets=exercise_log_in.sets,
        reps=exercise_log_in.reps,
        weight_kg=exercise_log_in.weight_kg,
        simulated_day=simulated_day,
        logged_at=datetime.utcnow(),
    )
    session.add(exercise_log)
    session.commit()
    session.refresh(exercise_log)
    return exercise_log


def get_exercise_logs_for_user(
    session: Session,
    user_id: uuid.UUID,
    start_date: datetime | None = None,
    end_date: datetime | None = None,
) -> list[ExerciseLog]:
    """Get exercise logs for a user within a date range."""
    statement = select(ExerciseLog).where(ExerciseLog.user_id == user_id)
    if start_date is not None:
        statement = statement.where(ExerciseLog.logged_at >= start_date)
    if end_date is not None:
        statement = statement.where(ExerciseLog.logged_at < end_date)
    statement = statement.order_by(ExerciseLog.logged_at)
    return list(session.exec(statement).all())


def get_exercise_logs_for_today(
    session: Session, user_id: uuid.UUID
) -> list[ExerciseLog]:
    """Get exercise logs for today (UTC). Deprecated - use get_exercise_logs_for_simulated_day."""
    today = datetime.utcnow().date()
    start = datetime.combine(today, time.min)
    end = datetime.combine(today, time.max)
    return get_exercise_logs_for_user(session, user_id, start_date=start, end_date=end)


def get_exercise_logs_for_simulated_day(
    session: Session, user_id: uuid.UUID, simulated_day: int
) -> list[ExerciseLog]:
    """Get exercise logs for a specific simulated day."""
    statement = (
        select(ExerciseLog)
        .where(ExerciseLog.user_id == user_id)
        .where(ExerciseLog.simulated_day == simulated_day)
        .order_by(ExerciseLog.logged_at)
    )
    return list(session.exec(statement).all())


def delete_exercise_logs_for_today(session: Session, user_id: uuid.UUID) -> int:
    """
    Delete all exercise logs for today for a user. Deprecated - use delete_exercise_logs_for_simulated_day.

    Returns:
        Number of logs deleted
    """
    from datetime import time

    from sqlmodel import delete

    today = datetime.utcnow().date()
    start = datetime.combine(today, time.min)
    end = datetime.combine(today, time.max)

    statement = (
        delete(ExerciseLog)
        .where(ExerciseLog.user_id == user_id)
        .where(ExerciseLog.logged_at >= start)
        .where(ExerciseLog.logged_at < end)
    )
    result = session.exec(statement)  # type: ignore
    session.commit()
    return result.rowcount  # type: ignore


def delete_exercise_logs_for_simulated_day(
    session: Session, user_id: uuid.UUID, simulated_day: int
) -> int:
    """
    Delete all exercise logs for a specific simulated day for a user.

    Returns:
        Number of logs deleted
    """
    from sqlmodel import delete

    statement = (
        delete(ExerciseLog)
        .where(ExerciseLog.user_id == user_id)
        .where(ExerciseLog.simulated_day == simulated_day)
    )
    result = session.exec(statement)  # type: ignore
    session.commit()
    return result.rowcount  # type: ignore
