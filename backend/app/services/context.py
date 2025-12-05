"""
Context Builder for LLM prompts.

Gathers all relevant context for a user to provide personalized LLM responses.
"""

from __future__ import annotations

import logging
import uuid
from dataclasses import dataclass, field

from sqlmodel import Session

from app.crud_chat import get_chat_messages
from app.crud_fitness import (
    get_exercise_logs_for_simulated_day,
    get_training_routines_for_program,
)
from app.crud_nutrition import (
    get_meal_logs_for_simulated_day,
    get_meal_plans_for_user,
)
from app.models import User
from app.services.calculations import CalculationService

logger = logging.getLogger(__name__)

# Maximum number of chat messages to include in context
MAX_CHAT_HISTORY = 10
# Maximum total characters for chat history to prevent token bloat
MAX_CHAT_HISTORY_CHARS = 10000


@dataclass
class UserContext:
    """All context needed for LLM prompts."""

    # User Profile
    user_id: str
    goal_method: str  # "standard_cut", "moderate_gain", "maintenance"
    weight_kg: float
    height_cm: int
    activity_level: str  # "sedentary", "lightly_active", etc.
    sex: str

    # Daily Progress (from REAL logs for simulated_day)
    calories_consumed: int
    calories_target: int  # From simulated day's plan or calculated
    protein_consumed: float
    protein_target: float  # From simulated day's plan or calculated
    workouts_completed: int

    # Simulated Day's Plan (targets)
    scheduled_meals: list[dict] = field(default_factory=list)
    # [{"meal_type": "breakfast", "item_name": "Oatmeal", "calories": 300, ...}]

    scheduled_exercises: list[dict] = field(default_factory=list)
    # [{"name": "Leg Press", "sets": 4, "reps": 10, "target_weight": 80}]

    completed_exercises: list[dict] = field(default_factory=list)
    # [{"name": "Leg Press", "sets": 2, "reps": 10, "weight_kg": 80}]
    # Actual exercise logs for the simulated day

    allowed_exercises: list[str] = field(default_factory=list)
    # ["Leg Press", "Squat", "Deadlift", ...]

    # Conversation (TEXT ONLY - no attachments)
    chat_history: list[dict] = field(default_factory=list)
    # [{"role": "user", "content": "..."}, ...] - Last 10 messages, content only

    # Simulation
    simulated_day: int = 0  # 0-6 (Monday-Sunday)

    @property
    def simulated_day_name(self) -> str:
        """Get the name of the simulated day."""
        day_names = [
            "Monday",
            "Tuesday",
            "Wednesday",
            "Thursday",
            "Friday",
            "Saturday",
            "Sunday",
        ]
        return (
            day_names[self.simulated_day] if 0 <= self.simulated_day <= 6 else "Unknown"
        )


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

        # Get simulated day from user profile
        simulated_day = user.simulated_day

        # Get meal logs for simulated day (real logs filtered by simulated_day)
        meal_logs = get_meal_logs_for_simulated_day(session, user_id, simulated_day)
        calories_consumed = sum(m.calories for m in meal_logs)
        protein_consumed = sum(m.protein_g for m in meal_logs)

        # Get exercise logs for simulated day
        exercise_logs = get_exercise_logs_for_simulated_day(
            session, user_id, simulated_day
        )
        workouts_completed = len(exercise_logs)

        # Build completed exercises list with details
        completed_exercises = [
            {
                "name": log.exercise_name,
                "sets": log.sets,
                "reps": log.reps,
                "weight_kg": log.weight_kg,
            }
            for log in exercise_logs
        ]

        # Get scheduled meals for simulated day (targets from meal plan)
        meal_plans = get_meal_plans_for_user(
            session, user_id, day_of_week=simulated_day
        )
        scheduled_meals = [
            {
                "meal_type": mp.meal_type,
                "item_name": mp.item_name,
                "calories": mp.calories,
                "protein_g": mp.protein_g,
                "carbs_g": mp.carbs_g,
                "fat_g": mp.fat_g,
            }
            for mp in meal_plans
        ]

        # Calculate targets - prefer meal plan totals, fall back to calculated
        if meal_plans:
            calories_target = sum(mp.calories for mp in meal_plans)
            protein_target = sum(mp.protein_g for mp in meal_plans)
        else:
            # Fall back to calculated targets from user profile
            energy_metrics = CalculationService.calculate_energy_metrics(user)
            if energy_metrics is not None:
                calories_target = energy_metrics.estimated_daily_calories
            else:
                calories_target = 2000  # Default

            if user.weight_kg is not None:
                protein_target = user.protein_g_per_kg * user.weight_kg
            else:
                protein_target = 150.0  # Default

        # Get training plan for simulated day
        scheduled_exercises: list[dict] = []
        allowed_exercises: list[str] = []

        if user.selected_program_id:
            routines = get_training_routines_for_program(
                session, user.selected_program_id, day_of_week=simulated_day
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

        # Get recent chat history (TEXT ONLY - no attachments)
        chat_history = self._build_chat_history(session, user_id)

        context = UserContext(
            user_id=str(user_id),
            goal_method=user.goal_method.value if user.goal_method else "maintenance",
            weight_kg=user.weight_kg or 70,
            height_cm=user.height_cm or 170,
            activity_level=(
                user.activity_level.value
                if user.activity_level
                else "moderately_active"
            ),
            sex=user.sex or "unknown",
            calories_consumed=calories_consumed,
            calories_target=calories_target,
            protein_consumed=protein_consumed,
            protein_target=protein_target,
            workouts_completed=workouts_completed,
            scheduled_meals=scheduled_meals,
            scheduled_exercises=scheduled_exercises,
            completed_exercises=completed_exercises,
            allowed_exercises=allowed_exercises,
            chat_history=chat_history,
            simulated_day=simulated_day,
        )

        # Log context for debugging
        logger.info(
            f"Built context for user {user_id}: "
            f"day={simulated_day}, "
            f"scheduled_exercises={len(scheduled_exercises)}, "
            f"completed_exercises={len(completed_exercises)}, "
            f"calories={calories_consumed}/{calories_target}"
        )
        logger.debug(f"Scheduled exercises: {scheduled_exercises}")
        logger.debug(f"Completed exercises: {completed_exercises}")

        return context

    def _build_chat_history(self, session: Session, user_id: uuid.UUID) -> list[dict]:
        """
        Build chat history for LLM context.

        CRITICAL: Only includes text content, excludes attachment_url and base64 data
        to prevent token bloat.

        Returns:
            List of dicts with only 'role' and 'content' fields, limited to
            MAX_CHAT_HISTORY messages and MAX_CHAT_HISTORY_CHARS total characters.
        """
        recent_messages = get_chat_messages(session, user_id, limit=MAX_CHAT_HISTORY)

        # Build history with TEXT ONLY - exclude attachment_url and attachment_type
        chat_history: list[dict] = []
        total_chars = 0

        for msg in recent_messages:
            # Only include role and content (text)
            content = msg.content or ""

            # Skip if adding this message would exceed character limit
            if total_chars + len(content) > MAX_CHAT_HISTORY_CHARS:
                break

            chat_history.append({"role": msg.role.value, "content": content})
            total_chars += len(content)

        return chat_history

    def _default_context(self, user_id: str) -> UserContext:
        """Return default context when user not found."""
        return UserContext(
            user_id=user_id,
            goal_method="maintenance",
            weight_kg=70,
            height_cm=170,
            activity_level="moderately_active",
            sex="unknown",
            calories_consumed=0,
            calories_target=2000,
            protein_consumed=0,
            protein_target=150,
            workouts_completed=0,
            scheduled_meals=[],
            scheduled_exercises=[],
            completed_exercises=[],
            allowed_exercises=[],
            chat_history=[],
            simulated_day=0,
        )
