"""
Chat API endpoints.

Provides endpoints for the chat interface.
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

    # Process through Brain service (async for LLM and vision)
    brain = BrainService(session=session)

    # Prepare image data if attachment is an image
    image_base64 = None
    image_url = None
    if attachment_type == ChatAttachmentType.IMAGE and message_in.attachment_url:
        # Retrieve image from ChatAttachment table by attachment_id
        try:
            import uuid as uuid_module

            attachment_id = uuid_module.UUID(message_in.attachment_url)
            attachment = session.get(ChatAttachment, attachment_id)
            if attachment:
                image_base64 = base64.b64encode(attachment.data).decode("utf-8")
        except (ValueError, TypeError):
            # Invalid UUID, treat as URL
            image_url = message_in.attachment_url

    # Process message asynchronously (supports LLM for general chat)
    brain_response = await brain.process_message_async(
        content=message_in.content,
        attachment_type=attachment_type,
        user_id=current_user.id,
        image_base64=image_base64,
        image_url=image_url,
    )

    # Create logs based on action type (using user's simulated day)
    simulated_day = current_user.simulated_day

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
        create_meal_log(session, current_user.id, meal_log_in, simulated_day)

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
        create_exercise_log(session, current_user.id, exercise_log_in, simulated_day)

    elif brain_response.action_type == ChatActionType.RESET:
        from app.crud_fitness import delete_exercise_logs_for_simulated_day
        from app.crud_nutrition import delete_meal_logs_for_simulated_day

        delete_meal_logs_for_simulated_day(session, current_user.id, simulated_day)
        delete_exercise_logs_for_simulated_day(session, current_user.id, simulated_day)

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


@router.post("/messages/{message_id}/confirm", response_model=ChatMessagePublic)
def confirm_tracking(
    session: SessionDep,
    current_user: CurrentUser,
    message_id: str,
) -> ChatMessagePublic:
    """
    Confirm tracking for a vision analysis preview.

    This endpoint:
    1. Validates the message exists and belongs to the user
    2. Validates action_type is PROPOSE_FOOD or PROPOSE_EXERCISE
    3. Validates is_tracked is False
    4. Creates the corresponding log entry
    5. Updates action_data.is_tracked to True
    6. Returns the updated message
    """
    import uuid as uuid_module

    from fastapi import HTTPException

    from app.crud_fitness import create_exercise_log
    from app.crud_nutrition import create_meal_log
    from app.models import ChatMessage, ExerciseLogCreate, MealLogCreate

    # Parse message_id
    try:
        msg_uuid = uuid_module.UUID(message_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid message ID format")

    # Get the message
    message = session.get(ChatMessage, msg_uuid)
    if not message:
        raise HTTPException(status_code=404, detail="Message not found")

    # Verify ownership
    if message.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Message not found")

    # Validate action type is PROPOSE_*
    if message.action_type not in [
        ChatActionType.PROPOSE_FOOD,
        ChatActionType.PROPOSE_EXERCISE,
    ]:
        raise HTTPException(
            status_code=400,
            detail="Message is not a trackable vision analysis",
        )

    # Validate not already tracked (check both camelCase and snake_case for compatibility)
    if message.action_data and (
        message.action_data.get("isTracked") or message.action_data.get("is_tracked")
    ):
        raise HTTPException(status_code=400, detail="Already tracked")

    # Get simulated day for logging
    simulated_day = current_user.simulated_day

    # Create the log entry based on action type
    if message.action_type == ChatActionType.PROPOSE_FOOD and message.action_data:
        meal_log_in = MealLogCreate(
            meal_name=message.action_data.get("meal_name", "Unknown"),
            meal_type=message.action_data.get("meal_type", "snack"),
            calories=message.action_data.get("calories", 0),
            protein_g=message.action_data.get("protein_g", 0),
            carbs_g=message.action_data.get("carbs_g", 0),
            fat_g=message.action_data.get("fat_g", 0),
        )
        create_meal_log(session, current_user.id, meal_log_in, simulated_day)

    elif message.action_type == ChatActionType.PROPOSE_EXERCISE and message.action_data:
        exercise_log_in = ExerciseLogCreate(
            exercise_name=message.action_data.get("exercise_name", "Unknown"),
            sets=message.action_data.get("sets", 0),
            reps=message.action_data.get("reps", 0),
            weight_kg=message.action_data.get("weight_kg", 0),
        )
        create_exercise_log(session, current_user.id, exercise_log_in, simulated_day)

    # Update action_data.isTracked to True (camelCase for frontend consistency)
    updated_action_data = dict(message.action_data) if message.action_data else {}
    # Remove snake_case key if present, use camelCase
    updated_action_data.pop("is_tracked", None)
    updated_action_data["isTracked"] = True
    message.action_data = updated_action_data
    session.add(message)
    session.commit()
    session.refresh(message)

    return ChatMessagePublic(
        id=message.id,
        role=message.role,
        content=message.content,
        action_type=message.action_type,
        action_data=message.action_data,
        attachment_type=message.attachment_type,
        attachment_url=message.attachment_url,
        created_at=message.created_at,
    )
