from uuid import UUID

from fastapi import Depends
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession

from API.models import House
from API.dependencies import database
from . import schemas


class HouseManager:
    session: AsyncSession

    def __init__(self, session = Depends(database.get_async_session)):
        self.session = session

    async def get(self) -> House:
        db: AsyncSession = self.session
        result = await db.scalars(select(House))
        return result.first()

    async def create(self, house_id: UUID) -> House: # TODO: remove
        db: AsyncSession = self.session

        if house := await self.get():
            await db.delete(house)

        house = House(id = house_id, name = '')
        db.add(house)
        await db.commit()
        return house
