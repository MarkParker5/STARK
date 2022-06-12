from typing import Optional
from pydantic import BaseModel
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
import config


__all__ = [
    # context
    'create_session',
    'create_async_session',
    # dependencies
    # 'get_session',
    # 'get_async_session',
]

engine = create_engine(config.db_url)
create_session = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_session() -> Session:
    with create_session() as session:
        yield session

# async_engine = create_async_engine(config.db_url)
# create_async_session = sessionmaker(
#     async_engine, class_ = AsyncSession, expire_on_commit = False
# )
#
# async def get_async_session() -> AsyncSession:
#     async with create_async_session() as session:
#         yield session