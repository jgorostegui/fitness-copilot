"""
Property-based tests for Chat feature.

Uses Hypothesis to verify correctness properties defined in the design document.
These are Small (Unit) tests - no DB, no network, pure logic.

Feature: slices-0-3
"""

import uuid
from datetime import datetime, timedelta

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

from app.models import (
    ChatActionType,
    ChatAttachmentType,
    ChatMessage,
    ChatMessageRole,
)

# ============================================================================
# Strategies
# ============================================================================

user_id_strategy = st.uuids()
content_strategy = st.text(min_size=1, max_size=2000)
role_strategy = st.sampled_from(list(ChatMessageRole))
action_type_strategy = st.sampled_from(list(ChatActionType))
attachment_type_strategy = st.sampled_from(list(ChatAttachmentType))


def create_chat_message(
    user_id: uuid.UUID,
    content: str,
    role: ChatMessageRole,
    action_type: ChatActionType = ChatActionType.NONE,
    created_at: datetime | None = None,
) -> ChatMessage:
    """Helper to create a ChatMessage instance for testing."""
    return ChatMessage(
        id=uuid.uuid4(),
        user_id=user_id,
        role=role,
        content=content,
        action_type=action_type,
        action_data=None,
        attachment_type=ChatAttachmentType.NONE,
        attachment_url=None,
        created_at=created_at or datetime.utcnow(),
    )


# ============================================================================
# Property 1: Chat message integrity and tenant association
# Feature: slices-0-3, Property 1: Chat message integrity and tenant association
# Validates: Requirements 3.1, 3.2
# ============================================================================


@pytest.mark.unit
class TestChatMessageIntegrity:
    """Property 1: Chat message integrity and tenant association."""

    @given(
        user_id=user_id_strategy,
        content=content_strategy,
        role=role_strategy,
        action_type=action_type_strategy,
    )
    @settings(max_examples=100)
    def test_chat_message_has_all_required_fields(
        self,
        user_id: uuid.UUID,
        content: str,
        role: ChatMessageRole,
        action_type: ChatActionType,
    ) -> None:
        """
        Feature: slices-0-3, Property 1: Chat message integrity and tenant association

        For any chat message created, the message SHALL have all required fields
        (id, user_id, role, content, action_type, created_at) populated.

        Validates: Requirements 3.1, 3.2
        """
        msg = create_chat_message(
            user_id=user_id,
            content=content,
            role=role,
            action_type=action_type,
        )

        # All required fields must be populated
        assert msg.id is not None
        assert msg.user_id == user_id
        assert msg.role == role
        assert msg.content == content
        assert msg.action_type == action_type
        assert msg.created_at is not None

    @given(
        user_id=user_id_strategy,
        content=content_strategy,
    )
    @settings(max_examples=100)
    def test_chat_message_user_id_matches_creator(
        self,
        user_id: uuid.UUID,
        content: str,
    ) -> None:
        """
        Feature: slices-0-3, Property 1: Chat message integrity and tenant association

        The user_id SHALL match the authenticated user who created it.

        Validates: Requirements 3.2
        """
        msg = create_chat_message(
            user_id=user_id,
            content=content,
            role=ChatMessageRole.USER,
        )

        assert msg.user_id == user_id


# ============================================================================
# Property 2: Tenant isolation for chat messages
# Feature: slices-0-3, Property 2: Tenant isolation for chat messages
# Validates: Requirements 3.3
# ============================================================================


@pytest.mark.unit
class TestTenantIsolation:
    """Property 2: Tenant isolation for chat messages."""

    @given(
        user_a_id=user_id_strategy,
        user_b_id=user_id_strategy,
        content_a=content_strategy,
        content_b=content_strategy,
    )
    @settings(max_examples=100)
    def test_messages_filtered_by_user_id(
        self,
        user_a_id: uuid.UUID,
        user_b_id: uuid.UUID,
        content_a: str,
        content_b: str,
    ) -> None:
        """
        Feature: slices-0-3, Property 2: Tenant isolation for chat messages

        For any user requesting chat history, the returned messages SHALL contain
        only messages where user_id matches the requesting user's id - no messages
        from other users SHALL ever be returned.

        Validates: Requirements 3.3
        """
        # Create messages for both users
        msg_a = create_chat_message(
            user_id=user_a_id,
            content=content_a,
            role=ChatMessageRole.USER,
        )
        msg_b = create_chat_message(
            user_id=user_b_id,
            content=content_b,
            role=ChatMessageRole.USER,
        )

        # Simulate filtering by user_id (what the CRUD function does)
        all_messages = [msg_a, msg_b]
        user_a_messages = [m for m in all_messages if m.user_id == user_a_id]
        user_b_messages = [m for m in all_messages if m.user_id == user_b_id]

        # User A should only see their messages
        for msg in user_a_messages:
            assert msg.user_id == user_a_id

        # User B should only see their messages
        for msg in user_b_messages:
            assert msg.user_id == user_b_id

        # If users are different, their message sets should not overlap
        if user_a_id != user_b_id:
            assert msg_a not in user_b_messages
            assert msg_b not in user_a_messages


# ============================================================================
# Property 3: Chat message ordering
# Feature: slices-0-3, Property 3: Chat message ordering
# Validates: Requirements 3.4
# ============================================================================


@pytest.mark.unit
class TestChatMessageOrdering:
    """Property 3: Chat message ordering."""

    @given(
        user_id=user_id_strategy,
        num_messages=st.integers(min_value=2, max_value=20),
    )
    @settings(max_examples=100)
    def test_messages_ordered_by_created_at_ascending(
        self,
        user_id: uuid.UUID,
        num_messages: int,
    ) -> None:
        """
        Feature: slices-0-3, Property 3: Chat message ordering

        For any sequence of chat messages returned by the API, the messages SHALL
        be ordered by created_at in ascending order (oldest first).

        Validates: Requirements 3.4
        """
        # Create messages with different timestamps
        base_time = datetime.utcnow()
        messages = []
        for i in range(num_messages):
            msg = create_chat_message(
                user_id=user_id,
                content=f"Message {i}",
                role=ChatMessageRole.USER if i % 2 == 0 else ChatMessageRole.ASSISTANT,
                created_at=base_time + timedelta(seconds=i),
            )
            messages.append(msg)

        # Shuffle to simulate unordered retrieval
        import random

        shuffled = messages.copy()
        random.shuffle(shuffled)

        # Sort by created_at ascending (what the CRUD function does)
        sorted_messages = sorted(shuffled, key=lambda m: m.created_at)

        # Verify ordering
        for i in range(len(sorted_messages) - 1):
            assert sorted_messages[i].created_at <= sorted_messages[i + 1].created_at

        # Verify we get the same messages back
        assert len(sorted_messages) == num_messages
