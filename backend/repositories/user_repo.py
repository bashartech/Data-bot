import uuid
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models.user import User


class UserRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_email(self, email: str) -> User | None:
        result = await self.session.execute(
            select(User).where(User.email == email)
        )
        return result.scalar_one_or_none()

    async def get_by_id(self, user_id: uuid.UUID) -> User | None:
        return await self.session.get(User, user_id)

    async def create(
        self, email: str, name: str, picture: str | None = None
    ) -> User:
        user = User(email=email, name=name, picture=picture)
        self.session.add(user)
        await self.session.flush()
        return user

    async def update_last_login(self, user: User) -> User:
        user.last_login = datetime.now(timezone.utc)
        await self.session.flush()
        return user

    async def upsert(
        self, email: str, name: str, picture: str | None = None
    ) -> User:
        user = await self.get_by_email(email)
        if user:
            user.name = name
            user.picture = picture
            user.last_login = datetime.now(timezone.utc)
        else:
            user = User(email=email, name=name, picture=picture)
            self.session.add(user)
        await self.session.flush()
        return user
