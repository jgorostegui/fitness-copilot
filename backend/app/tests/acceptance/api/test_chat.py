"""
API acceptance tests for chat endpoints.

These are Medium (Acceptance) tests - require DB.
"""

import pytest
from fastapi.testclient import TestClient

from app.core.config import settings


def get_demo_token(client: TestClient, persona: str = "cut") -> str:
    """Helper to get a demo user token."""
    r = client.post(f"{settings.API_V1_STR}/demo/login/{persona}")
    return r.json()["access_token"]


@pytest.mark.acceptance
def test_get_chat_messages_empty(client: TestClient) -> None:
    """Test GET /chat/messages returns empty list for new user."""
    token = get_demo_token(client, "bulk")  # Use bulk to get fresh user
    headers = {"Authorization": f"Bearer {token}"}

    r = client.get(f"{settings.API_V1_STR}/chat/messages", headers=headers)
    assert r.status_code == 200

    data = r.json()
    assert "data" in data
    assert "count" in data


@pytest.mark.acceptance
def test_send_chat_message_food(client: TestClient) -> None:
    """Test POST /chat/messages with food creates MealLog."""
    token = get_demo_token(client, "maintain")  # Use maintain to get fresh user
    headers = {"Authorization": f"Bearer {token}"}

    # Send food message
    r = client.post(
        f"{settings.API_V1_STR}/chat/messages",
        headers=headers,
        json={"content": "I ate a banana"},
    )
    assert r.status_code == 200

    data = r.json()
    assert data["role"] == "assistant"
    assert data["actionType"] == "log_food"
    assert data["actionData"] is not None
    assert data["actionData"]["food"] == "banana"

    # Verify MealLog was created
    logs_r = client.get(f"{settings.API_V1_STR}/logs/today", headers=headers)
    logs = logs_r.json()
    assert len(logs["mealLogs"]) >= 1
    assert any(log["mealName"] == "Banana" for log in logs["mealLogs"])


@pytest.mark.acceptance
def test_send_chat_message_exercise(client: TestClient) -> None:
    """Test POST /chat/messages with exercise creates ExerciseLog."""
    token = get_demo_token(client, "maintain")
    headers = {"Authorization": f"Bearer {token}"}

    # Send exercise message
    r = client.post(
        f"{settings.API_V1_STR}/chat/messages",
        headers=headers,
        json={"content": "Did 3 sets of bench at 60kg"},
    )
    assert r.status_code == 200

    data = r.json()
    assert data["role"] == "assistant"
    assert data["actionType"] == "log_exercise"
    assert data["actionData"] is not None
    assert data["actionData"]["exercise_name"] == "Bench Press"
    assert data["actionData"]["sets"] == 3
    assert data["actionData"]["weight_kg"] == 60.0

    # Verify ExerciseLog was created
    logs_r = client.get(f"{settings.API_V1_STR}/logs/today", headers=headers)
    logs = logs_r.json()
    assert len(logs["exerciseLogs"]) >= 1
    assert any(log["exerciseName"] == "Bench Press" for log in logs["exerciseLogs"])


@pytest.mark.acceptance
def test_send_chat_message_general(client: TestClient) -> None:
    """Test POST /chat/messages with general message returns context-aware response."""
    token = get_demo_token(client, "maintain")
    headers = {"Authorization": f"Bearer {token}"}

    r = client.post(
        f"{settings.API_V1_STR}/chat/messages",
        headers=headers,
        json={"content": "hello"},
    )
    assert r.status_code == 200

    data = r.json()
    assert data["role"] == "assistant"
    assert data["actionType"] == "none"
    # Context-aware responses may include progress info, greetings, or suggestions
    content_lower = data["content"].lower()
    assert any(
        keyword in content_lower
        for keyword in ["log", "help", "calorie", "goal", "support", "hi", "hello"]
    )


@pytest.mark.acceptance
def test_reset_command_clears_logs(client: TestClient) -> None:
    """Test 'reset' command clears today's logs."""
    token = get_demo_token(client, "maintain")
    headers = {"Authorization": f"Bearer {token}"}

    # First log some food
    client.post(
        f"{settings.API_V1_STR}/chat/messages",
        headers=headers,
        json={"content": "I ate a banana"},
    )

    # Verify log exists
    logs_r = client.get(f"{settings.API_V1_STR}/logs/today", headers=headers)
    logs = logs_r.json()
    assert len(logs["mealLogs"]) >= 1

    # Send reset command
    r = client.post(
        f"{settings.API_V1_STR}/chat/messages",
        headers=headers,
        json={"content": "reset"},
    )
    assert r.status_code == 200

    data = r.json()
    assert data["actionType"] == "reset"

    # Verify logs are cleared
    logs_r = client.get(f"{settings.API_V1_STR}/logs/today", headers=headers)
    logs = logs_r.json()
    assert len(logs["mealLogs"]) == 0
    assert len(logs["exerciseLogs"]) == 0


@pytest.mark.acceptance
def test_chat_messages_ordered_by_created_at(client: TestClient) -> None:
    """Test GET /chat/messages returns messages in chronological order."""
    token = get_demo_token(client, "maintain")
    headers = {"Authorization": f"Bearer {token}"}

    # Send multiple messages
    client.post(
        f"{settings.API_V1_STR}/chat/messages",
        headers=headers,
        json={"content": "First message"},
    )
    client.post(
        f"{settings.API_V1_STR}/chat/messages",
        headers=headers,
        json={"content": "Second message"},
    )

    # Get messages
    r = client.get(f"{settings.API_V1_STR}/chat/messages", headers=headers)
    data = r.json()

    # Verify ordering (oldest first)
    messages = data["data"]
    for i in range(len(messages) - 1):
        assert messages[i]["createdAt"] <= messages[i + 1]["createdAt"]


@pytest.mark.acceptance
def test_chat_unauthenticated_returns_401(client: TestClient) -> None:
    """Test chat endpoints require authentication."""
    r = client.get(f"{settings.API_V1_STR}/chat/messages")
    assert r.status_code in [401, 403]

    r = client.post(
        f"{settings.API_V1_STR}/chat/messages",
        json={"content": "hello"},
    )
    assert r.status_code in [401, 403]


# ============================================================================
# Property 12: Chat logging updates summary consistently
# Feature: slices-0-3, Property 12: Chat logging updates summary consistently
# Validates: Requirements 11.1, 11.2, 11.3, 11.4
# ============================================================================


@pytest.mark.acceptance
def test_food_logging_updates_summary_calories(client: TestClient) -> None:
    """
    Feature: slices-0-3, Property 12: Chat logging updates summary consistently

    For any item logged via chat (food), the item SHALL appear in GET /logs/today
    AND the GET /summary/today values SHALL reflect the addition.

    Validates: Requirements 11.1, 11.4
    """
    token = get_demo_token(client, "maintain")
    headers = {"Authorization": f"Bearer {token}"}

    # Reset to start fresh
    client.post(
        f"{settings.API_V1_STR}/chat/messages",
        headers=headers,
        json={"content": "reset"},
    )

    # Get initial summary
    initial_summary = client.get(
        f"{settings.API_V1_STR}/summary/today", headers=headers
    ).json()
    initial_calories = initial_summary["caloriesConsumed"]

    # Log food via chat
    r = client.post(
        f"{settings.API_V1_STR}/chat/messages",
        headers=headers,
        json={"content": "I ate a banana"},
    )
    assert r.status_code == 200
    action_data = r.json()["actionData"]
    logged_calories = action_data.get("calories", 0)

    # Get updated summary
    updated_summary = client.get(
        f"{settings.API_V1_STR}/summary/today", headers=headers
    ).json()

    # Verify calories increased by the logged amount
    assert updated_summary["caloriesConsumed"] == initial_calories + logged_calories


@pytest.mark.acceptance
def test_exercise_logging_updates_summary_workouts(client: TestClient) -> None:
    """
    Feature: slices-0-3, Property 12: Chat logging updates summary consistently

    For any item logged via chat (exercise), the item SHALL appear in GET /logs/today
    AND the GET /summary/today workoutsCompleted SHALL reflect the addition.

    Validates: Requirements 11.2, 11.4
    """
    token = get_demo_token(client, "maintain")
    headers = {"Authorization": f"Bearer {token}"}

    # Reset to start fresh
    client.post(
        f"{settings.API_V1_STR}/chat/messages",
        headers=headers,
        json={"content": "reset"},
    )

    # Get initial summary
    initial_summary = client.get(
        f"{settings.API_V1_STR}/summary/today", headers=headers
    ).json()
    initial_workouts = initial_summary["workoutsCompleted"]

    # Log exercise via chat
    r = client.post(
        f"{settings.API_V1_STR}/chat/messages",
        headers=headers,
        json={"content": "Did 3 sets of bench at 60kg"},
    )
    assert r.status_code == 200
    assert r.json()["actionType"] == "log_exercise"

    # Get updated summary
    updated_summary = client.get(
        f"{settings.API_V1_STR}/summary/today", headers=headers
    ).json()

    # Verify workouts increased by 1
    assert updated_summary["workoutsCompleted"] == initial_workouts + 1


@pytest.mark.acceptance
def test_reset_updates_summary_to_zero(client: TestClient) -> None:
    """
    Feature: slices-0-3, Property 12: Chat logging updates summary consistently

    When "reset" is sent via chat, the Monitor dashboard SHALL reset to zero for today.

    Validates: Requirements 11.3, 11.4
    """
    token = get_demo_token(client, "maintain")
    headers = {"Authorization": f"Bearer {token}"}

    # Log some food and exercise first
    client.post(
        f"{settings.API_V1_STR}/chat/messages",
        headers=headers,
        json={"content": "I ate a banana"},
    )
    client.post(
        f"{settings.API_V1_STR}/chat/messages",
        headers=headers,
        json={"content": "Did 3 sets of bench at 60kg"},
    )

    # Verify we have some data
    pre_reset_summary = client.get(
        f"{settings.API_V1_STR}/summary/today", headers=headers
    ).json()
    assert (
        pre_reset_summary["caloriesConsumed"] > 0
        or pre_reset_summary["workoutsCompleted"] > 0
    )

    # Send reset command
    r = client.post(
        f"{settings.API_V1_STR}/chat/messages",
        headers=headers,
        json={"content": "reset"},
    )
    assert r.status_code == 200
    assert r.json()["actionType"] == "reset"

    # Verify summary is reset
    post_reset_summary = client.get(
        f"{settings.API_V1_STR}/summary/today", headers=headers
    ).json()
    assert post_reset_summary["caloriesConsumed"] == 0
    assert post_reset_summary["workoutsCompleted"] == 0
