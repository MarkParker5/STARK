from typing import Any
from uuid import uuid1, UUID
import os

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
    autocommit=False, autoflush=False, bind=engine
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

models.Base.metadata.drop_all(bind = engine) # os.remove(f'{config.src}/test_database.sqlite3')
models.Base.metadata.create_all(bind = engine)

# App

app.dependency_overrides[get_session] = override_get_session
app.dependency_overrides[get_async_session] = override_get_async_session

client = TestClient(app)

# Simulate Cloud

# TODO: auth tokens

# Fill DB

house_id = uuid1()

def init_hub():
    hub_id = uuid1()
    default_name = 'Inited Hub'

    response = client.post('/api/hub', json = {
        'id': str(hub_id),
        'name': default_name,
        'house_id': str(house_id),
        'access_token': hub_access_token,
        'refresh_token': hub_refresh_token,
        'public_key': public_key,
    })
    assert response.status_code == 200, f'{response.status_code}{response.text}'
    return response.json()

def get_house() -> dict[str, Any]:
    response = client.get(f'/api/house/')
    assert response.status_code == 200
    return response.json()

def create_device_model() -> models.DeviceModel:
    with create_session() as session:
        device_model = models.DeviceModel(name = 'TestModel')
        session.add(device_model)
        session.commit()
        session.refresh(device_model)
        return device_model

def create_room():
    with create_session() as session:
        room = models.Room(house_id = house_id, name = 'TestModel')
        session.add(room)
        session.commit()
        session.refresh(room)
        return room
