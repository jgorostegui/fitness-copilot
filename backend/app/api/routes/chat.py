"""
Chat API endpoints.

Provides endpoints for the Oracle chat interface.
"""

import base64

from fastapi import APIRouter, Query

from app.api.deps import CurrentUser, SessionDep
from app.crud_chat import create_chat_message, delete_chat_messages, get_chat_messages
from app.models import (
    ChatActionType,
    ChatAttachment,
    ChatAttachmentType,
    ChatMessageCreate,
    ChatMessagePublic,
    ChatMessageRole,
    ChatMessagesPublic,
    Message,
)
from app.services.brain import BrainService

router = APIRouter(prefix="/chat", tags=["chat"])


@router.get("/messages", response_model=ChatMessagesPublic)
def get_messages(
    session: SessionDep,
    current_user: CurrentUser,
    limit: int = Query(default=50, ge=1, le=200),
) -> ChatMessagesPublic:
    """
    Get chat history for the current user.

    Returns messages ordered by created_at ascending (oldest first).
    """
    messages = get_chat_messages(session, current_user.id, limit=limit)

    return ChatMessagesPublic(
        data=[
            ChatMessagePublic(
                id=m.id,
                role=m.role,
                content=m.content,
                action_type=m.action_type,
                action_data=m.action_data,
                attachment_type=m.attachment_type,
                attachment_url=m.attachment_url,
                created_at=m.created_at,
            )
            for m in messages
        ],
        count=len(messages),
    )


@router.post("/messages", response_model=ChatMessagePublic)
async def send_message(
    session: SessionDep,
    current_user: CurrentUser,
    message_in: ChatMessageCreate,
) -> ChatMessagePublic:
    """
    Send a chat message and get a response from the Brain.

    This endpoint:
    1. Saves the user message
    2. Processes it through the Brain service (async for images)
    3. Creates logs if action_type is log_food or log_exercise
    4. Saves the assistant response
    5. Returns the assistant response
    """
    from app.crud_fitness import create_exercise_log
    from app.crud_nutrition import create_meal_log
    from app.models import ExerciseLogCreate, MealLogCreate

    # Get attachment type from input
    attachment_type = message_in.attachment_type or ChatAttachmentType.NONE

    # Save user message
    create_chat_message(
        session=session,
        user_id=current_user.id,
        content=message_in.content,
        role=ChatMessageRole.USER,
        action_type=ChatActionType.NONE,
        attachment_type=attachment_type,
        attachment_url=message_in.attachment_url,
    )

    # Process through Brain service
    brain = BrainService(session=session)

    # Handle image attachments with async vision processing
    if attachment_type == ChatAttachmentType.IMAGE and message_in.attachment_url:
        # Retrieve image from ChatAttachment table by attachment_id
        image_base64 = None
        try:
            import uuid as uuid_module

            attachment_id = uuid_module.UUID(message_in.attachment_url)
            attachment = session.get(ChatAttachment, attachment_id)
            if attachment:
                image_base64 = base64.b64encode(attachment.data).decode("utf-8")
        except (ValueError, TypeError):
            # Invalid UUID, treat as URL
            pass

        brain_response = await brain._handle_image_attachment(
            user_id=current_user.id,
            image_base64=image_base64,
            image_url=message_in.attachment_url if not image_base64 else None,
        )
    else:
        # Sync processing for text messages
        brain_response = brain.process_message(
            content=message_in.content,
            attachment_type=attachment_type,
        )

    # Create logs based on action type
    if (
        brain_response.action_type == ChatActionType.LOG_FOOD
        and brain_response.action_data
    ):
        meal_log_in = MealLogCreate(
            meal_name=brain_response.action_data.get("meal_name", "Unknown"),
            meal_type=brain_response.action_data.get("meal_type", "snack"),
            calories=brain_response.action_data.get("calories", 0),
            protein_g=brain_response.action_data.get("protein_g", 0),
            carbs_g=brain_response.action_data.get("carbs_g", 0),
            fat_g=brain_response.action_data.get("fat_g", 0),
        )
        create_meal_log(session, current_user.id, meal_log_in)

    elif (
        brain_response.action_type == ChatActionType.LOG_EXERCISE
        and brain_response.action_data
    ):
        exercise_log_in = ExerciseLogCreate(
            exercise_name=brain_response.action_data.get("exercise_name", "Unknown"),
            sets=brain_response.action_data.get("sets", 0),
            reps=brain_response.action_data.get("reps", 0),
            weight_kg=brain_response.action_data.get("weight_kg", 0),
        )
        create_exercise_log(session, current_user.id, exercise_log_in)

    elif brain_response.action_type == ChatActionType.RESET:
        from app.crud_fitness import delete_exercise_logs_for_today
        from app.crud_nutrition import delete_meal_logs_for_today

        delete_meal_logs_for_today(session, current_user.id)
        delete_exercise_logs_for_today(session, current_user.id)

    # Save assistant response
    assistant_message = create_chat_message(
        session=session,
        user_id=current_user.id,
        content=brain_response.content,
        role=ChatMessageRole.ASSISTANT,
        action_type=brain_response.action_type,
        action_data=brain_response.action_data,
    )

    return ChatMessagePublic(
        id=assistant_message.id,
        role=assistant_message.role,
        content=assistant_message.content,
        action_type=assistant_message.action_type,
        action_data=assistant_message.action_data,
        attachment_type=assistant_message.attachment_type,
        attachment_url=assistant_message.attachment_url,
        created_at=assistant_message.created_at,
    )


@router.delete("/messages", response_model=Message)
def clear_messages(
    session: SessionDep,
    current_user: CurrentUser,
) -> Message:
    """
    Delete all chat messages for the current user.

    This clears the entire chat history.
    """
    count = delete_chat_messages(session, current_user.id)
    return Message(message=f"Deleted {count} messages")
