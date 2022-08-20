from uuid import UUID
from fastapi import Depends
from sqlalchemy import select, delete, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import NoResultFound

from exceptions.Internal import InternalException, ExceptionCode
from models import House
from server.dependencies import database
from schemas.house import HousePatch


class HouseManager:
    session: AsyncSession

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get(self) -> House:
        db: AsyncSession = self.session
        try:
            result = await db.scalars(select(House))
            return result.one()
        except NoResultFound:
            raise InternalException(ExceptionCode.not_initialized)

    async def create(self, house_id: UUID) -> House:
        db: AsyncSession = self.session

        try:
            await db.delete(await self.get())
        except InternalException:
            pass

        house = House(id = house_id, name = '')
        db.add(house)
        await db.commit()
        return house

    async def patch(self, house: HousePatch):
        db: AsyncSession = self.session
        await db.execute(
            update(House)
            .values(**house.dict())
        )
