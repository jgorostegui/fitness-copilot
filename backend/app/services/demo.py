"""
Demo Service for Fitness Copilot.

Provides demo mode functionality for showcasing the app without authentication complexity.
"""

from dataclasses import dataclass
from pathlib import Path

from sqlmodel import Session, select

from app.core.security import get_password_hash
from app.models import ActivityLevel, GoalMethod, MealPlan, User
from app.services.csv_import import CSVImportService


@dataclass
class DemoPersona:
    """Configuration for a demo persona."""

    name: str
    description: str
    email: str
    full_name: str
    sex: str
    weight_kg: float
    height_cm: int
    age: int
    goal_method: GoalMethod
    activity_level: ActivityLevel
    training_days: int  # Expected number of training days per week


# Demo persona configurations
PERSONAS: dict[str, DemoPersona] = {
    "cut": DemoPersona(
        name="cut",
        description="6-day PPL split, calorie deficit for fat loss",
        email="demo-cut@test.com",
        full_name="Alex (Cutting)",
        sex="male",
        weight_kg=85.0,
        height_cm=180,
        age=30,
        goal_method=GoalMethod.STANDARD_CUT,
        activity_level=ActivityLevel.VERY_ACTIVE,
        training_days=6,
    ),
    "bulk": DemoPersona(
        name="bulk",
        description="4-day Upper/Lower, calorie surplus for muscle growth",
        email="demo-bulk@test.com",
        full_name="Jordan (Bulking)",
        sex="male",
        weight_kg=75.0,
        height_cm=178,
        age=25,
        goal_method=GoalMethod.MODERATE_GAIN,
        activity_level=ActivityLevel.VERY_ACTIVE,
        training_days=4,
    ),
    "maintain": DemoPersona(
        name="maintain",
        description="3-day Full Body, maintenance calories",
        email="demo-maintain@test.com",
        full_name="Sam (Maintenance)",
        sex="female",
        weight_kg=65.0,
        height_cm=168,
        age=28,
        goal_method=GoalMethod.MAINTENANCE,
        activity_level=ActivityLevel.MODERATELY_ACTIVE,
        training_days=3,
    ),
}

# Default password for demo users
DEMO_PASSWORD = "demo1234"


def get_or_create_demo_user(session: Session, persona: str) -> User:
    """
    Get or create a demo user for the given persona.

    If the user already exists, updates their profile to match the persona config
    and resets onboarding_complete to False.
    If not, creates a new user with the persona's configuration.

    Also loads persona-specific training programs and meal plans.

    Args:
        session: Database session
        persona: Persona name ("cut", "bulk", or "maintain")

    Returns:
        The demo user

    Raises:
        ValueError: If persona is not valid
    """
    if persona not in PERSONAS:
        raise ValueError(
            f"Invalid persona: {persona}. Must be one of: {list(PERSONAS.keys())}"
        )

    config = PERSONAS[persona]

    # Initialize CSV import service with correct data directory
    # Path: demo.py -> services -> app -> backend -> data
    data_dir = Path(__file__).parent.parent.parent / "data"
    csv_service = CSVImportService(data_dir)

    # Load persona-specific training program (creates if not exists)
    program = csv_service.load_training_programs_for_persona(session, persona)

    # Check if user already exists
    statement = select(User).where(User.email == config.email)
    existing_user = session.exec(statement).first()

    if existing_user:
        # Update existing user's profile to match persona config
        # This ensures switching personas works correctly
        existing_user.full_name = config.full_name
        existing_user.sex = config.sex
        existing_user.weight_kg = config.weight_kg
        existing_user.height_cm = config.height_cm
        existing_user.age = config.age
        existing_user.goal_method = config.goal_method
        existing_user.activity_level = config.activity_level
        existing_user.onboarding_complete = False  # Reset to show onboarding
        existing_user.simulated_day = 0  # Reset to Monday

        # Assign training program if loaded
        if program:
            existing_user.selected_program_id = program.id

        session.add(existing_user)
        session.commit()
        session.refresh(existing_user)

        # Clear existing meal plans and reload for this persona
        _reload_meal_plans_for_user(session, existing_user.id, persona, csv_service)

        return existing_user

    # Create new demo user
    user = User(
        email=config.email,
        hashed_password=get_password_hash(DEMO_PASSWORD),
        full_name=config.full_name,
        sex=config.sex,
        weight_kg=config.weight_kg,
        height_cm=config.height_cm,
        age=config.age,
        goal_method=config.goal_method,
        activity_level=config.activity_level,
        onboarding_complete=False,  # Forces onboarding screen
        is_active=True,
        is_superuser=False,
        simulated_day=0,  # Start on Monday
        selected_program_id=program.id if program else None,
    )
    session.add(user)
    session.commit()
    session.refresh(user)

    # Load meal plans for the new user
    csv_service.load_meal_plans_for_persona(session, user.id, persona)

    return user


def _reload_meal_plans_for_user(
    session: Session,
    user_id,
    persona: str,
    csv_service: CSVImportService,
) -> None:
    """
    Clear existing meal plans and reload from persona CSV.

    Args:
        session: Database session
        user_id: User ID to reload meal plans for
        persona: Persona name for CSV selection
        csv_service: CSV import service instance
    """
    # Delete existing meal plans for this user
    existing_plans = session.exec(
        select(MealPlan).where(MealPlan.user_id == user_id)
    ).all()
    for plan in existing_plans:
        session.delete(plan)
    session.commit()

    # Load fresh meal plans from persona CSV
    csv_service.load_meal_plans_for_persona(session, user_id, persona)


def list_personas() -> list[dict]:
    """
    List available demo personas.

    Returns:
        List of persona info dicts with name and description
    """
    return [
        {
            "name": persona.name,
            "description": persona.description,
        }
        for persona in PERSONAS.values()
    ]
