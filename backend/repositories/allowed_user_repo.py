from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models.allowed_user import AllowedUser


class AllowedUserRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def is_allowed(self, email: str) -> bool:
        result = await self.session.execute(
            select(AllowedUser).where(
                AllowedUser.email == email,
                AllowedUser.is_active.is_(True),
            )
        )
        return result.scalar_one_or_none() is not None
