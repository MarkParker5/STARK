from typing import Any
from uuid import uuid1, UUID
import os
import time

from jose import jwt

from fastapi import FastAPI
from fastapi.testclient import TestClient

from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine

from main import app
from API.dependencies.database import get_session, get_async_session
from API import models
import config

from .faker import Faker


# Settings

with open(f'{config.path}/SmartHome/tests/jwt-key', 'r') as f:
    secret_key = f.read()
with open(f'{config.path}/SmartHome/tests/jwt-key.pub', 'r') as f:
    public_key = f.read()

user_id = UUID('f085ef73-f599-11ec-acda-58961df87e73')

access_token = ''
hub_access_token = ''
hub_refresh_token = ''

db_url = f'sqlite:///{config.src}/test_database.sqlite3'
async_db_url = f'sqlite+aiosqlite:///{config.src}/test_database.sqlite3'

# Simulate Cloud Auth

access_token = jwt.encode({
    'type': 'access',
    'user_id': str(user_id),
    'is_admin': False,
    'exp': time.time() + 60
}, secret_key, algorithm = 'RS256')

# Sync DB

engine = create_engine(
    db_url, connect_args = {'check_same_thread': False}
)

create_session = sessionmaker(
    autocommit = False, autoflush = False, bind = engine
)

def override_get_session() -> Session:
    with create_session() as session:
        yield session

# Async DB

async_engine = create_async_engine(
    async_db_url, connect_args = {'check_same_thread': False}
)

create_async_session = sessionmaker(
    async_engine, class_ = AsyncSession, expire_on_commit = False
)

async def override_get_async_session() -> AsyncSession:
    async with create_async_session() as session:
        yield session

# App

models.Base.metadata.drop_all(bind = engine)
models.Base.metadata.create_all(bind = engine)

app.dependency_overrides[get_session] = override_get_session
app.dependency_overrides[get_async_session] = override_get_async_session
client = TestClient(app)

# Faker

faker = Faker(client, create_session)
faker.hub_access_token = hub_access_token
faker.hub_refresh_token = hub_refresh_token
faker.public_key = public_key
faker.user_access_token = access_token

#

auth_headers = {
    'Authorization': f'Bearer {access_token}'
}
