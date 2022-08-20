from typing import Optional
from pydantic import BaseModel
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
import config


# sync

engine = create_engine(
    config.db_url, connect_args={'check_same_thread': False}
)

create_session = sessionmaker(
    autocommit=False, autoflush=False, bind=engine
)

# async

async_engine = create_async_engine(
    config.db_async_url, connect_args={'check_same_thread': False}
)

create_async_session = sessionmaker(
    async_engine, class_ = AsyncSession, expire_on_commit = False
)
