import uuid
from datetime import datetime, timezone
from typing import Sequence

from sqlalchemy import delete, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from models.conversation import Conversation, Message


class ConversationRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def list_by_user(self, user_id: uuid.UUID) -> Sequence[Conversation]:
        result = await self.session.execute(
            select(Conversation)
            .where(Conversation.user_id == user_id)
            .order_by(Conversation.created_at.desc())
        )
        return result.scalars().all()

    async def get_by_id(self, conversation_id: uuid.UUID) -> Conversation | None:
        return await self.session.get(Conversation, conversation_id)

    async def create(
        self, user_id: uuid.UUID, title: str = "New Chat"
    ) -> Conversation:
        conv = Conversation(user_id=user_id, title=title)
        self.session.add(conv)
        await self.session.flush()
        return conv

    async def rename(self, conversation_id: uuid.UUID, title: str) -> Conversation | None:
        await self.session.execute(
            update(Conversation)
            .where(Conversation.id == conversation_id)
            .values(title=title)
        )
        await self.session.flush()
        return await self.get_by_id(conversation_id)

    async def delete(self, conversation_id: uuid.UUID) -> None:
        await self.session.execute(
            delete(Conversation).where(Conversation.id == conversation_id)
        )
        await self.session.flush()

    async def get_messages(
        self, conversation_id: uuid.UUID, skip: int = 0, limit: int = 100
    ) -> Sequence[Message]:
        result = await self.session.execute(
            select(Message)
            .where(Message.conversation_id == conversation_id)
            .order_by(Message.created_at)
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()

    async def add_message(
        self, conversation_id: uuid.UUID, role: str, content: str
    ) -> Message:
        msg = Message(
            conversation_id=conversation_id,
            role=role,
            content=content,
        )
        self.session.add(msg)
        await self.session.flush()
        return msg
