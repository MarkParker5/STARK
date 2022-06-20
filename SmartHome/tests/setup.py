from uuid import uuid1, UUID

from fastapi import FastAPI
from fastapi.testclient import TestClient

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine

from main import app
from API.dependencies.database import get_session, get_async_session
from API import models
import config


# Settings

secret_key = ''
public_key = ''

access_token = ''
hub_access_token = ''
hub_refresh_token = ''

db_url = f'sqlite:///{config.src}/test_database.sqlite3'
async_db_url = f'sqlite+aiosqlite:///{config.src}/test_database.sqlite3'

# Dependencies

    # sync db

engine = create_engine(
    db_url, connect_args={'check_same_thread': False}
)

create_session = sessionmaker(
    autocommit=False, autoflush=False, bind=engine, connect_args={'check_same_thread': False}
)

def override_get_session() -> Session:
    with create_session() as session:
        yield session

    # async db

async_engine = create_async_engine(
    async_db_url, connect_args={'check_same_thread': False}
)

create_async_session = sessionmaker(
    async_engine, class_ = AsyncSession, expire_on_commit = False
)

async def override_get_async_session() -> AsyncSession:
    async with create_async_session() as session:
        yield session

models.Base.metadata.drop_all(bind = engine)
models.Base.metadata.create_all(bind = engine)

# App

app.dependency_overrides[get_session] = override_get_session
app.dependency_overrides[get_async_session] = override_get_async_session

client = TestClient(app)

# Simulate Cloud

# TODO: auth tokens
