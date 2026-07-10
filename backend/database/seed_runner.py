import asyncio

from database.engine import engine, async_session_factory
from database.seed import seed_database


async def main():
    async with async_session_factory() as session:
        await seed_database(session)
    await engine.dispose()
    print("Seed complete")


if __name__ == "__main__":
    asyncio.run(main())
