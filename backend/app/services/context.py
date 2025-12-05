"""
Context Builder for LLM prompts.

Gathers all relevant context for a user to provide personalized LLM responses.
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime

from sqlmodel import Session

from app.crud_chat import get_chat_messages
from app.crud_fitness import (
    get_exercise_logs_for_today,
    get_training_routines_for_program,
)
from app.crud_nutrition import get_meal_logs_for_today
from app.models import User
from app.services.calculations import CalculationService


@dataclass
class UserContext:
    """All context needed for LLM prompts."""

    # User Profile
    user_id: str
    goal_method: str  # "standard_cut", "moderate_gain", "maintenance"
    weight_kg: float
    sex: str

    # Today's Progress
    calories_consumed: int
    calories_target: int
    protein_consumed: float
    protein_target: float
    workouts_completed: int

    # Today's Training Plan (from DB)
    scheduled_exercises: list[dict] = field(default_factory=list)
    # [{"name": "Leg Press", "sets": 4, "reps": 10, "target_weight": 80}]

    allowed_exercises: list[str] = field(default_factory=list)
    # ["Leg Press", "Squat", "Deadlift", ...]

    # Recent Chat History (last 5 messages)
    chat_history: list[dict] = field(default_factory=list)
    # [{"role": "user", "content": "..."}, ...]


class ContextBuilder:
    """Builds context for LLM prompts."""

    def build_context(
        self,
        session: Session,
        user_id: uuid.UUID,
    ) -> UserContext:
        """Gather all context for a user."""
        user = session.get(User, user_id)
        if not user:
            return self._default_context(str(user_id))

        # Get today's meal logs for calorie/protein consumed
        meal_logs = get_meal_logs_for_today(session, user_id)
        calories_consumed = sum(m.calories for m in meal_logs)
        protein_consumed = sum(m.protein_g for m in meal_logs)

        # Get today's exercise logs for workouts completed
        exercise_logs = get_exercise_logs_for_today(session, user_id)
        workouts_completed = len(exercise_logs)

        # Calculate targets from user profile
        energy_metrics = CalculationService.calculate_energy_metrics(user)
        if energy_metrics is not None:
            calories_target = energy_metrics.estimated_daily_calories
        else:
            calories_target = 2000  # Default

        # Calculate protein target
        if user.weight_kg is not None:
            protein_target = user.protein_g_per_kg * user.weight_kg
        else:
            protein_target = 150.0  # Default

        # Get today's training plan
        scheduled_exercises: list[dict] = []
        allowed_exercises: list[str] = []

        if user.selected_program_id:
            today = datetime.utcnow().weekday()  # 0=Monday, 6=Sunday
            routines = get_training_routines_for_program(
                session, user.selected_program_id, day_of_week=today
            )
            scheduled_exercises = [
                {
                    "name": r.exercise_name,
                    "sets": r.sets,
                    "reps": r.reps,
                    "target_weight": r.target_load_kg,
                }
                for r in routines
            ]

            # Get all exercises from the program for allowed list
            all_routines = get_training_routines_for_program(
                session, user.selected_program_id
            )
            allowed_exercises = list({r.exercise_name for r in all_routines})

        # Get recent chat history (last 5 messages)
        recent_messages = get_chat_messages(session, user_id, limit=10)
        # Take last 5 messages
        chat_history = [
            {"role": m.role.value, "content": m.content} for m in recent_messages[-5:]
        ]

        return UserContext(
            user_id=str(user_id),
            goal_method=user.goal_method.value if user.goal_method else "maintenance",
            weight_kg=user.weight_kg or 70,
            sex=user.sex or "unknown",
            calories_consumed=calories_consumed,
            calories_target=calories_target,
            protein_consumed=protein_consumed,
            protein_target=protein_target,
            workouts_completed=workouts_completed,
            scheduled_exercises=scheduled_exercises,
            allowed_exercises=allowed_exercises,
            chat_history=chat_history,
        )

    def _default_context(self, user_id: str) -> UserContext:
        """Return default context when user not found."""
        return UserContext(
            user_id=user_id,
            goal_method="maintenance",
            weight_kg=70,
            sex="unknown",
            calories_consumed=0,
            calories_target=2000,
            protein_consumed=0,
            protein_target=150,
            workouts_completed=0,
            scheduled_exercises=[],
            allowed_exercises=[],
            chat_history=[],
        )
