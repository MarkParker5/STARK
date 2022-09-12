from uuid import UUID
from fastapi import Depends
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import NoResultFound

import config
from exceptions.Internal import InternalException, ExceptionCode
from hardware import WiFi
from models import User, Hub
from schemas import hub as schemas
from managers import HouseManager
from server.dependencies import database, auth
from server.auth import UserToken, UserAuthManager, AuthException


class HubManager:
    session: AsyncSession
    token: auth.UserToken | None
    user: User | None = None

    def __init__(self, session: AsyncSession, token: UserToken = None):
        self.session = session
        self.token = token

    async def get(self) -> Hub | None:
        db: AsyncSession = self.session
        try:
            result = await db.scalars(select(Hub))
            return result.one()
        except NoResultFound:
            raise InternalException(ExceptionCode.not_initialized)

    async def parse_token(self, raw_token: str):
        db: AsyncSession = self.session
        try:
            self.token = UserAuthManager().validate_access(raw_token)
        except AuthException:
            raise InternalException(ExceptionCode.unauthorized)
        self.user = await db.get(User, self.token.user_id)

    async def init(self, create_hub: schemas.HubInit, raw_token: str) -> Hub:
        db: AsyncSession = self.session

        try:
            hub = await self.get()
        except InternalException:
            hub = None

        if hub:
            await self.parse_token(raw_token)
            await self.check_access()
            await db.delete(hub)
            self.save_tokens(create_hub)
        else:
            self.save_credentials(create_hub)
            await self.parse_token(raw_token)

        house_manager = HouseManager(db)
        await house_manager.create(create_hub.house_id)

        hub = Hub(id = create_hub.id, name = create_hub.name, house_id = create_hub.house_id)
        db.add(hub)

        if not self.user:
            user = User(id = self.token.user_id, name = '')
            db.add(user)

        await db.commit()
        return hub

    async def patch(self, hub: schemas.HubPatch):
        db: AsyncSession = self.session
        values = {key: value for key, value in hub.dict().items() if value != None}

        await db.execute(update(Hub).values(**values))
        await db.commit()

    def wifi(self, ssid: str, password: str):
        WiFi.save(ssid, password)

    def start_wps(self):
        WiFi.start_wps()

    def is_connected(self) -> bool:
        return WiFi.is_connected()

    def stop_hotspot(self):
        WiFi.stop_hotspot()

    def get_hotspots(self) -> list[schemas.Hotspot]:
        try:
            return list(WiFi.scan())
        except WiFi.InterfaceBusyException:
            return []

    def save_credentials(self, credentials: schemas.HubAuthItems):
        self.save_tokens(credentials)

        config.public_key = credentials.public_key
        with open(f'{config.src}/jwt.key.pub', 'w') as f:
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
            raise InternalException(ExceptionCode.access_denied)

        db: AsyncSession = self.session
        self.user = await db.get(User, self.token.user_id)

        if not self.user:
            raise InternalException(ExceptionCode.access_denied)
