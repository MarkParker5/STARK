from uuid import UUID

from fastapi import Depends
from sqlalchemy import select, update, delete
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from exceptions.Internal import InternalException, ExceptionCode
from models import User, Room
from schemas import room as schemas
from server import endpoints


class RoomsManager:
    session: AsyncSession

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get(self, id: UUID) -> Room:
        db: AsyncSession = self.session
        result = await db.scalars(
            select(Room).where(Room.id == id).options(selectinload(Room.devices))
        )
        if room := result.first():
            return room
        else:
            raise InternalException(ExceptionCode.not_found, 'Room not found')

    async def create(self, create_room: schemas.RoomCreate) -> Room:
        db: AsyncSession = self.session
        house = await endpoints.house.HouseManager(db).get()
        room = Room(name = create_room.name, house_id = house.id, devices = [])
        db.add(room)
        await db.commit()

        return room

    async def patch(self, id: UUID, room: schemas.RoomPatch):
        db: AsyncSession = self.session
        values = {key: value for key, value in room.dict().items() if key != 'id'}
        await db.execute(update(Room).values(**values).where(Room.id == id))
        await db.commit()

    async def delete(self, room_id: UUID):
        db: AsyncSession = self.session
        room = await self.get(room_id)
        await db.delete(room)
        await db.commit()
