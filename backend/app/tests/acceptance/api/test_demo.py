"""
API acceptance tests for demo mode endpoints.

These are Medium (Acceptance) tests - require DB.
"""

import pytest
from fastapi.testclient import TestClient

from app.core.config import settings


@pytest.mark.acceptance
def test_get_demo_users(client: TestClient) -> None:
    """Test GET /demo/users returns 3 personas."""
    r = client.get(f"{settings.API_V1_STR}/demo/users")
    assert r.status_code == 200

    personas = r.json()
    assert len(personas) == 3

    # Check all expected personas are present
    names = {p["name"] for p in personas}
    assert names == {"cut", "bulk", "maintain"}

    # Each persona should have a description
    for persona in personas:
        assert "description" in persona
        assert persona["description"]


@pytest.mark.acceptance
def test_demo_login_cut_creates_user(client: TestClient) -> None:
    """Test POST /demo/login/cut creates user with onboarding_complete=False."""
    r = client.post(f"{settings.API_V1_STR}/demo/login/cut")
    assert r.status_code == 200

    data = r.json()
    assert "access_token" in data
    assert data["access_token"]
    assert data["token_type"] == "bearer"

    # Verify user was created with correct settings
    headers = {"Authorization": f"Bearer {data['access_token']}"}
    profile_r = client.get(f"{settings.API_V1_STR}/profile/me", headers=headers)
    assert profile_r.status_code == 200

    profile = profile_r.json()
    assert profile["onboardingComplete"] is False
    assert profile["weightKg"] == 85.0
    assert profile["heightCm"] == 180
    assert profile["goalMethod"] == "standard_cut"


@pytest.mark.acceptance
def test_demo_login_bulk_creates_user(client: TestClient) -> None:
    """Test POST /demo/login/bulk creates user with bulk settings."""
    r = client.post(f"{settings.API_V1_STR}/demo/login/bulk")
    assert r.status_code == 200

    data = r.json()
    headers = {"Authorization": f"Bearer {data['access_token']}"}
    profile_r = client.get(f"{settings.API_V1_STR}/profile/me", headers=headers)

    profile = profile_r.json()
    assert profile["onboardingComplete"] is False
    assert profile["weightKg"] == 75.0  # Updated for smart-assistant feature
    assert profile["goalMethod"] == "moderate_gain"


@pytest.mark.acceptance
def test_demo_login_maintain_creates_user(client: TestClient) -> None:
    """Test POST /demo/login/maintain creates user with maintenance settings."""
    r = client.post(f"{settings.API_V1_STR}/demo/login/maintain")
    assert r.status_code == 200

    data = r.json()
    headers = {"Authorization": f"Bearer {data['access_token']}"}
    profile_r = client.get(f"{settings.API_V1_STR}/profile/me", headers=headers)

    profile = profile_r.json()
    assert profile["onboardingComplete"] is False
    assert profile["weightKg"] == 93.0  # Maintain persona weight
    assert profile["goalMethod"] == "maintenance"


@pytest.mark.acceptance
def test_demo_login_existing_user_returns_token(client: TestClient) -> None:
    """Test POST /demo/login/cut on existing user returns token without recreating."""
    # First login creates user
    r1 = client.post(f"{settings.API_V1_STR}/demo/login/cut")
    assert r1.status_code == 200
    token1 = r1.json()["access_token"]

    # Second login returns token for same user
    r2 = client.post(f"{settings.API_V1_STR}/demo/login/cut")
    assert r2.status_code == 200
    token2 = r2.json()["access_token"]

    # Both tokens should work and return same user
    headers1 = {"Authorization": f"Bearer {token1}"}
    headers2 = {"Authorization": f"Bearer {token2}"}

    profile1 = client.get(f"{settings.API_V1_STR}/profile/me", headers=headers1).json()
    profile2 = client.get(f"{settings.API_V1_STR}/profile/me", headers=headers2).json()

    assert profile1["id"] == profile2["id"]


@pytest.mark.acceptance
def test_demo_login_invalid_persona(client: TestClient) -> None:
    """Test POST /demo/login/invalid returns 404."""
    r = client.post(f"{settings.API_V1_STR}/demo/login/invalid")
    assert r.status_code == 404


@pytest.mark.acceptance
def test_demo_login_resets_profile_on_relogin(client: TestClient) -> None:
    """Test POST /demo/login resets profile to persona defaults on re-login.

    This ensures that when a user logs out and logs back in as the same persona,
    their profile is reset to the persona defaults (including onboarding_complete=False).
    """
    # First login
    r1 = client.post(f"{settings.API_V1_STR}/demo/login/cut")
    assert r1.status_code == 200
    token1 = r1.json()["access_token"]
    headers1 = {"Authorization": f"Bearer {token1}"}

    # Complete onboarding by updating profile
    client.put(
        f"{settings.API_V1_STR}/profile/me",
        headers=headers1,
        json={"onboarding_complete": True, "weight_kg": 100.0},
    )

    # Verify onboarding is complete and weight changed
    profile1 = client.get(f"{settings.API_V1_STR}/profile/me", headers=headers1).json()
    assert profile1["onboardingComplete"] is True
    assert profile1["weightKg"] == 100.0

    # Re-login as same persona
    r2 = client.post(f"{settings.API_V1_STR}/demo/login/cut")
    assert r2.status_code == 200
    token2 = r2.json()["access_token"]
    headers2 = {"Authorization": f"Bearer {token2}"}

    # Profile should be reset to persona defaults
    profile2 = client.get(f"{settings.API_V1_STR}/profile/me", headers=headers2).json()
    assert profile2["onboardingComplete"] is False  # Reset to show onboarding
    assert profile2["weightKg"] == 85.0  # Reset to cut persona default
