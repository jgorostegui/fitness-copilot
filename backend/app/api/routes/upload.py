"""
Upload API endpoints.

Provides endpoints for uploading images for chat attachments.
"""

import base64
import uuid

from fastapi import APIRouter, HTTPException
from fastapi.responses import Response

from app.api.deps import CurrentUser, SessionDep
from app.models import ChatAttachment, ImageUploadRequest, ImageUploadResponse

router = APIRouter(prefix="/upload", tags=["upload"])


@router.post("/image", response_model=ImageUploadResponse)
def upload_image(
    request: ImageUploadRequest,
    session: SessionDep,
    current_user: CurrentUser,
) -> ImageUploadResponse:
    """
    Upload an image and return an attachment ID.

    The image is stored in the database and can be referenced
    in chat messages via the attachment_url field.
    """
    try:
        # Decode base64 to bytes
        image_bytes = base64.b64decode(request.image_base64)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid base64 image data")

    # Validate content type
    allowed_types = {"image/jpeg", "image/png", "image/gif", "image/webp"}
    if request.content_type not in allowed_types:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid content type. Allowed: {', '.join(allowed_types)}",
        )

    # Create attachment record
    attachment = ChatAttachment(
        user_id=current_user.id,
        content_type=request.content_type,
        data=image_bytes,
    )
    session.add(attachment)
    session.commit()
    session.refresh(attachment)

    return ImageUploadResponse(attachment_id=str(attachment.id))


@router.get("/image/{attachment_id}")
def get_image(
    attachment_id: str,
    session: SessionDep,
    current_user: CurrentUser,
) -> Response:
    """
    Get an uploaded image by its attachment ID.

    Returns the raw image bytes with appropriate content type.
    Only the owner of the image can access it.
    """
    try:
        attachment_uuid = uuid.UUID(attachment_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid attachment ID")

    attachment = session.get(ChatAttachment, attachment_uuid)
    if not attachment:
        raise HTTPException(status_code=404, detail="Attachment not found")

    # Security: only allow owner to access their images
    if attachment.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")

    return Response(
        content=attachment.data,
        media_type=attachment.content_type,
    )
