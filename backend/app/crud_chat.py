"""
CRUD operations for chat features.

Includes: Chat messages.
"""

import uuid
from datetime import datetime

from sqlmodel import Session, select

from app.models import (
    ChatActionType,
    ChatAttachmentType,
    ChatMessage,
    ChatMessageRole,
)


def create_chat_message(
    session: Session,
    user_id: uuid.UUID,
    content: str,
    role: ChatMessageRole,
    action_type: ChatActionType = ChatActionType.NONE,
    action_data: dict | None = None,
    attachment_type: ChatAttachmentType = ChatAttachmentType.NONE,
    attachment_url: str | None = None,
) -> ChatMessage:
    """Create a chat message for a user."""
    chat_message = ChatMessage(
        user_id=user_id,
        role=role,
        content=content,
        action_type=action_type,
        action_data=action_data,
        attachment_type=attachment_type,
        attachment_url=attachment_url,
        created_at=datetime.utcnow(),
    )
    session.add(chat_message)
    session.commit()
    session.refresh(chat_message)
    return chat_message


def get_chat_messages(
    session: Session,
    user_id: uuid.UUID,
    limit: int = 50,
) -> list[ChatMessage]:
    """
    Get chat messages for a user, ordered by created_at ascending.

    Args:
        session: Database session
        user_id: User ID to filter by (tenant isolation)
        limit: Maximum number of messages to return

    Returns:
        List of chat messages ordered by created_at ascending (oldest first)
    """
    statement = (
        select(ChatMessage)
        .where(ChatMessage.user_id == user_id)
        .order_by(ChatMessage.created_at.asc())
        .limit(limit)
    )
    return list(session.exec(statement).all())


def delete_chat_messages(
    session: Session,
    user_id: uuid.UUID,
) -> int:
    """
    Delete all chat messages for a user.

    Args:
        session: Database session
        user_id: User ID to filter by (tenant isolation)

    Returns:
        Number of messages deleted
    """
    statement = select(ChatMessage).where(ChatMessage.user_id == user_id)
    messages = list(session.exec(statement).all())
    count = len(messages)
    for msg in messages:
        session.delete(msg)
    session.commit()
    return count
