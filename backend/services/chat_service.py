from uuid import UUID

from openai.types.responses import ResponseTextDeltaEvent
from sqlalchemy.ext.asyncio import AsyncSession

from ai.agent import run_agent_streamed
from config.logging import logger
from repositories.conversation_repo import ConversationRepository
from repositories.user_repo import UserRepository


class ChatService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.conv_repo = ConversationRepository(session)
        self.user_repo = UserRepository(session)

    async def get_or_create_conversation(
        self, user_id: UUID, conversation_id: UUID | None
    ) -> tuple[dict, bool]:
        if conversation_id:
            conv = await self.conv_repo.get_by_id(conversation_id)
            if conv is None:
                raise ValueError("Conversation not found")
            if conv.user_id != user_id:
                raise ValueError("Conversation does not belong to user")
            return _conv_to_dict(conv), False
        conv = await self.conv_repo.create(user_id=user_id)
        await self.session.flush()
        return _conv_to_dict(conv), True

    async def add_user_message(
        self, conversation_id: UUID, content: str
    ) -> None:
        await self.conv_repo.add_message(
            conversation_id=conversation_id, role="user", content=content
        )

    async def build_agent_input(
        self, conversation_id: UUID
    ) -> list[dict]:
        messages = await self.conv_repo.get_messages(conversation_id, limit=50)
        return [
            {"role": msg.role, "content": msg.content} for msg in messages
        ]

    async def stream_chat(
        self,
        conversation_id: UUID,
        user_message: str,
        user_id: UUID,
        is_new: bool = False,
    ):
        if is_new:
            title = user_message[:60]
            if len(user_message) > 60:
                title += "..."
            await self.conv_repo.rename(conversation_id, title)

        await self.add_user_message(conversation_id, user_message)
        await self.session.commit()

        history = await self.build_agent_input(conversation_id)
        context = _ChatContext(session=self.session, user_id=user_id)

        try:
            stream_result = await run_agent_streamed(
                input=history,
                context=context,
            )
            collected = ""
            async for event in stream_result.stream_events():
                if event.type == "raw_response_event":
                    if isinstance(event.data, ResponseTextDeltaEvent):
                        delta = event.data.delta
                        if delta:
                            collected += delta
                            yield {"type": "token", "content": delta}

            await self.conv_repo.add_message(
                conversation_id=conversation_id,
                role="assistant",
                content=collected,
            )
            await self.session.commit()
            yield {"type": "done", "conversation_id": str(conversation_id)}

        except Exception as e:
            logger.error("Agent streaming failed", error=str(e))
            await self.session.rollback()
            yield {
                "type": "error",
                "content": "I encountered an error processing your request. Please try again.",
            }


class _ChatContext:
    def __init__(self, session: AsyncSession, user_id: UUID):
        self.session = session
        self.user_id = user_id


def _conv_to_dict(conv) -> dict:
    return {
        "id": conv.id,
        "user_id": conv.user_id,
        "title": conv.title,
        "created_at": conv.created_at,
    }
