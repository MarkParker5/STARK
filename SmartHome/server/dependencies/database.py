from database import (
    create_session,
    create_async_session,
    Session,
    AsyncSession
)

def get_session() -> Session:
    with create_session() as session:
        yield session


async def get_async_session() -> AsyncSession:
    async with create_async_session() as session:
        yield session
