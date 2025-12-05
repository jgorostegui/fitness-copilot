"""
Demo Service for Fitness Copilot.

Provides demo mode functionality for showcasing the app without authentication complexity.
"""

from dataclasses import dataclass

from sqlmodel import Session, select

from app.core.security import get_password_hash
from app.models import ActivityLevel, GoalMethod, User


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


# Demo persona configurations
PERSONAS: dict[str, DemoPersona] = {
    "cut": DemoPersona(
        name="cut",
        description="Cutting phase - losing fat while preserving muscle",
        email="demo-cut@test.com",
        full_name="Demo User (Cutting)",
        sex="male",
        weight_kg=85.0,
        height_cm=180,
        age=30,
        goal_method=GoalMethod.STANDARD_CUT,
        activity_level=ActivityLevel.MODERATELY_ACTIVE,
    ),
    "bulk": DemoPersona(
        name="bulk",
        description="Bulking phase - building muscle mass",
        email="demo-bulk@test.com",
        full_name="Demo User (Bulking)",
        sex="male",
        weight_kg=90.0,
        height_cm=185,
        age=25,
        goal_method=GoalMethod.MODERATE_GAIN,
        activity_level=ActivityLevel.VERY_ACTIVE,
    ),
    "maintain": DemoPersona(
        name="maintain",
        description="Maintenance phase - maintaining current weight",
        email="demo-maintain@test.com",
        full_name="Demo User (Maintenance)",
        sex="female",
        weight_kg=60.0,
        height_cm=165,
        age=28,
        goal_method=GoalMethod.MAINTENANCE,
        activity_level=ActivityLevel.LIGHTLY_ACTIVE,
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

    Args:
        session: Database session
        persona: Persona name ("cut", "bulk", or "maintain")

    Returns:
        The demo user

    Raises:
        ValueError: If persona is not valid
    """
    if persona not in PERSONAS:
        raise ValueError(f"Invalid persona: {persona}. Must be one of: {list(PERSONAS.keys())}")

    config = PERSONAS[persona]

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
        session.add(existing_user)
        session.commit()
        session.refresh(existing_user)
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
    )
    session.add(user)
    session.commit()
    session.refresh(user)

    return user


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
