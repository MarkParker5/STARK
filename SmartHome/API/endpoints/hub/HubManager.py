from __future__ import annotations
from uuid import UUID

from fastapi import Depends
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import NoResultFound

from Raspberry import WiFi
import config
from API import exceptions
from API.models import User, Hub
from API.dependencies import database, auth
from API.auth import UserToken, UserAuthManager, AuthException
from API import endpoints
from . import schemas


class HubManager:
    session: AsyncSession
    token: auth.UserToken
    user: User | None = None

    def __init__(self, session = Depends(database.get_async_session), token = Depends(auth.optional_token)):
        self.session = session
        self.token = token

    async def parse_token(self, raw_token: str):
        db: AsyncSession = self.session
        try:
            self.token = UserAuthManager().validate_access(raw_token)
        except AuthException:
            raise exceptions.access_denied
        self.user = await db.get(User, self.token.user_id)

    async def init(self, create_hub: schemas.HubInit) -> Hub:
        db: AsyncSession = self.session

        if hub := await self.get():
            await self.check_access()
            await db.delete(hub)

        house_manager = endpoints.house.HouseManager(db)
        await house_manager.create(create_hub.house_id)

        hub = Hub(id = create_hub.id, name = create_hub.name, house_id = create_hub.house_id)
        db.add(hub)

        if not self.user:
            user = User(id = self.token.user_id, name = '')
            db.add(user)

        await db.commit()
        return hub

    async def get(self) -> Hub | None:
        db: AsyncSession = self.session
        result = await db.scalars(select(Hub))
        return result.first()

    async def patch(self, hub: schemas.PatchHub):
        db: AsyncSession = self.session
        values = {key: value for key, value in hub.dict().items() if value != None}

        await db.execute(update(Hub).values(**values))
        await db.commit()

    async def wifi(self, ssid: str, password: str):
        WiFi.save_and_connect(ssid, password)

    async def get_hotspots(self) -> list[schemas.Hotspot]:
        return [schemas.Hotspot(**cell.__dict__) for cell in WiFi.get_list()]

    def save_credentials(self, credentials: schemas.HubAuthItems):
        self.save_tokens(credentials)

        config.public_key = credentials.public_key
        with open(f'{config.src}/jwt-key.pub', 'w') as f:
            f.write(credentials.public_key)

    def save_tokens(self, tokens_pair: schemas.HubAuthItems):
        config.access_token = tokens_pair.access_token
        with open(f'{config.src}/jwt_access_token', 'w') as f:
            f.write(tokens_pair.access_token)

        config.refresh_token = tokens_pair.refresh_token
        with open(f'{config.src}/jwt_refresh_token', 'w') as f:
            f.write(tokens_pair.refresh_token)

    async def check_access(self):
        if self.user:
            return

        if not self.token:
            raise exceptions.access_denied

        db: AsyncSession = self.session
        self.user = await db.get(User, self.token.user_id)

        if not self.user:
            raise exceptions.access_denied
