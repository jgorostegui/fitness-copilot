"""
Demo mode API endpoints.

Provides endpoints for demo login without authentication complexity.
Only available in local environment.
"""

from datetime import timedelta

from fastapi import APIRouter, HTTPException

from app.api.deps import SessionDep
from app.core.config import settings
from app.core.security import create_access_token
from app.models import Token
from app.services.demo import PERSONAS, get_or_create_demo_user, list_personas

router = APIRouter(prefix="/demo", tags=["demo"])


@router.get("/users")
def get_demo_users() -> list[dict]:
    """
    List available demo personas.

    Returns a list of available demo personas (cut, bulk, maintain)
    with their descriptions.
    """
    return list_personas()


@router.post("/login/{persona}", response_model=Token)
def demo_login(
    session: SessionDep,
    persona: str,
) -> Token:
    """
    Login as a demo user.

    Creates the demo user if it doesn't exist, then returns a JWT token.
    Demo users have onboarding_complete=False so the frontend shows
    the onboarding screen with pre-filled data.

    Args:
        persona: The persona to login as ("cut", "bulk", or "maintain")

    Returns:
        JWT access token
    """
    if persona not in PERSONAS:
        raise HTTPException(
            status_code=404,
            detail=f"Unknown persona: {persona}. Available: {list(PERSONAS.keys())}",
        )

    # Get or create the demo user
    user = get_or_create_demo_user(session, persona)

    # Create and return JWT token
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        subject=str(user.id), expires_delta=access_token_expires
    )
    return Token(access_token=access_token)
