import json
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from auth.dependencies import get_current_user
from database.engine import get_session
from services.chat_service import ChatService

router = APIRouter(prefix="/chat", tags=["chat"])


class ChatRequest(BaseModel):
    message: str
    conversation_id: UUID | None = None


@router.post("")
async def chat(
    body: ChatRequest,
    current_user: dict = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    if not body.message.strip():
        raise HTTPException(
            status_code=400, detail="Message cannot be empty"
        )

    service = ChatService(session)
    try:
        conv, is_new = await service.get_or_create_conversation(
            user_id=current_user["id"],
            conversation_id=body.conversation_id,
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

    from fastapi.responses import StreamingResponse

    return StreamingResponse(
        _stream_events(service, conv["id"], body.message, current_user["id"], is_new),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


async def _stream_events(
    service: ChatService,
    conversation_id: UUID,
    user_message: str,
    user_id: UUID,
    is_new: bool,
):
    async for event in service.stream_chat(
        conversation_id=conversation_id,
        user_message=user_message,
        user_id=user_id,
        is_new=is_new,
    ):
        yield f"data: {json.dumps(event)}\n\n"
