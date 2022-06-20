from __future__ import annotations
from uuid import UUID

from fastapi import Depends
from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import NoResultFound

from Raspberry import WiFi
import config
from API import exceptions
from API.models import Hub
from API.dependencies import database
from . import schemas


class HubManager:
    session: AsyncSession

    def __init__(self, session = Depends(database.get_async_session)):
        self.session = session

    async def init(self, create_hub: schemas.HubInit) -> Hub:
        db: AsyncSession = self.session

        if hub := await self.get():
            await db.delete(hub)

        hub = Hub(id = create_hub.id, name = create_hub.name, house_id = create_hub.house_id)
        db.add(hub)

        await db.commit()
        await db.refresh(hub)

        return hub

    async def get(self) -> Hub | None:
        db: AsyncSession = self.session
        result = await db.scalars(select(Hub))
        hub = result.first()
        return hub

    async def patch(self, hub: schemas.PatchHub):
        db: AsyncSession = self.session
        values = {key: value for key, value in hub.dict().items() if value != None}
        await db.execute(update(Hub).values(**values))
        await db.commit()

    def wifi(self, ssid: str, password: str):
        WiFi.save_and_connect(ssid, password)

    def get_hotspots(self) -> list[schemas.Hotspot]:
        return [schemas.Hotspot(**cell.__dict__) for cell in WiFi.get_list()]

    def save_tokens(self, tokens_pair: schemas.HubAuthItems):
        with open(f'{config.src}/access_token.txt', 'w') as f:
            f.write(tokens_pair.access_token)
        with open(f'{config.src}/refresh_token.txt', 'w') as f:
            f.write(tokens_pair.refresh_token)

    def save_credentials(self, credentials: schemas.HubAuthItems):
        self.save_tokens(credentials)
        with open(f'{config.src}/public_key.txt', 'w') as f:
            f.write(credentials.public_key)
