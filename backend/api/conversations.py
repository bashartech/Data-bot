from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from auth.dependencies import get_current_user
from database.engine import get_session
from repositories.conversation_repo import ConversationRepository

router = APIRouter(prefix="/conversations", tags=["conversations"])


class CreateConversationRequest(BaseModel):
    title: str = "New Chat"


class RenameConversationRequest(BaseModel):
    title: str


class MessageResponse(BaseModel):
    id: UUID
    role: str
    content: str
    created_at: str


class ConversationResponse(BaseModel):
    id: UUID
    title: str
    created_at: str


@router.get("")
async def list_conversations(
    current_user: dict = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    repo = ConversationRepository(session)
    convs = await repo.list_by_user(current_user["id"])
    return [
        ConversationResponse(
            id=c.id,
            title=c.title,
            created_at=c.created_at.isoformat(),
        )
        for c in convs
    ]


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_conversation(
    body: CreateConversationRequest,
    current_user: dict = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    repo = ConversationRepository(session)
    conv = await repo.create(
        user_id=current_user["id"], title=body.title
    )
    await session.commit()
    return ConversationResponse(
        id=conv.id,
        title=conv.title,
        created_at=conv.created_at.isoformat(),
    )


@router.get("/{conversation_id}")
async def get_conversation(
    conversation_id: UUID,
    current_user: dict = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    repo = ConversationRepository(session)
    conv = await repo.get_by_id(conversation_id)
    if conv is None:
        raise HTTPException(status_code=404, detail="Conversation not found")
    if str(conv.user_id) != str(current_user["id"]):
        raise HTTPException(status_code=403, detail="Access denied")
    return ConversationResponse(
        id=conv.id,
        title=conv.title,
        created_at=conv.created_at.isoformat(),
    )


@router.patch("/{conversation_id}")
async def rename_conversation(
    conversation_id: UUID,
    body: RenameConversationRequest,
    current_user: dict = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    repo = ConversationRepository(session)
    conv = await repo.get_by_id(conversation_id)
    if conv is None:
        raise HTTPException(status_code=404, detail="Conversation not found")
    if str(conv.user_id) != str(current_user["id"]):
        raise HTTPException(status_code=403, detail="Access denied")
    conv = await repo.rename(conversation_id, body.title)
    await session.commit()
    return ConversationResponse(
        id=conv.id,
        title=conv.title,
        created_at=conv.created_at.isoformat(),
    )


@router.delete("/{conversation_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_conversation(
    conversation_id: UUID,
    current_user: dict = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    repo = ConversationRepository(session)
    conv = await repo.get_by_id(conversation_id)
    if conv is None:
        raise HTTPException(status_code=404, detail="Conversation not found")
    if str(conv.user_id) != str(current_user["id"]):
        raise HTTPException(status_code=403, detail="Access denied")
    await repo.delete(conversation_id)
    await session.commit()


@router.get("/{conversation_id}/messages")
async def get_messages(
    conversation_id: UUID,
    current_user: dict = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    repo = ConversationRepository(session)
    conv = await repo.get_by_id(conversation_id)
    if conv is None:
        raise HTTPException(status_code=404, detail="Conversation not found")
    if str(conv.user_id) != str(current_user["id"]):
        raise HTTPException(status_code=403, detail="Access denied")
    messages = await repo.get_messages(conversation_id)
    return [
        MessageResponse(
            id=m.id,
            role=m.role,
            content=m.content,
            created_at=m.created_at.isoformat(),
        )
        for m in messages
    ]
