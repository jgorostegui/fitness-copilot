"""
CRUD operations for nutrition features.

Includes: Meal plans, meal logs.
"""

import uuid
from datetime import datetime, time

from sqlmodel import Session, select

from app.models import (
    MealLog,
    MealLogCreate,
    MealPlan,
)


# ============================================================================
# Meal Plans (tenant-isolated)
# ============================================================================


def get_meal_plans_for_user(
    session: Session, user_id: uuid.UUID, day_of_week: int | None = None
) -> list[MealPlan]:
    """Get meal plans for a user, optionally filtered by day."""
    statement = select(MealPlan).where(MealPlan.user_id == user_id)
    if day_of_week is not None:
        statement = statement.where(MealPlan.day_of_week == day_of_week)
    return list(session.exec(statement).all())


def get_meal_plans_for_today(session: Session, user_id: uuid.UUID) -> list[MealPlan]:
    """Get meal plans for today (current day of week)."""
    today = datetime.utcnow().weekday()  # 0=Monday, 6=Sunday
    return get_meal_plans_for_user(session, user_id, day_of_week=today)


# ============================================================================
# Meal Logs (tenant-isolated)
# ============================================================================


def create_meal_log(
    session: Session, user_id: uuid.UUID, meal_log_in: MealLogCreate
) -> MealLog:
    """Create a meal log for a user."""
    meal_log = MealLog(
        user_id=user_id,
        meal_name=meal_log_in.meal_name,
        meal_type=meal_log_in.meal_type,
        calories=meal_log_in.calories,
        protein_g=meal_log_in.protein_g,
        carbs_g=meal_log_in.carbs_g,
        fat_g=meal_log_in.fat_g,
        logged_at=datetime.utcnow(),
    )
    session.add(meal_log)
    session.commit()
    session.refresh(meal_log)
    return meal_log


def get_meal_logs_for_user(
    session: Session,
    user_id: uuid.UUID,
    start_date: datetime | None = None,
    end_date: datetime | None = None,
) -> list[MealLog]:
    """Get meal logs for a user within a date range."""
    statement = select(MealLog).where(MealLog.user_id == user_id)
    if start_date is not None:
        statement = statement.where(MealLog.logged_at >= start_date)
    if end_date is not None:
        statement = statement.where(MealLog.logged_at < end_date)
    statement = statement.order_by(MealLog.logged_at)
    return list(session.exec(statement).all())


def get_meal_logs_for_today(session: Session, user_id: uuid.UUID) -> list[MealLog]:
    """Get meal logs for today (UTC)."""
    today = datetime.utcnow().date()
    start = datetime.combine(today, time.min)
    end = datetime.combine(today, time.max)
    return get_meal_logs_for_user(session, user_id, start_date=start, end_date=end)
