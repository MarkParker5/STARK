from uuid import UUID

from fastapi import Depends
from sqlalchemy import select, update, delete
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from API import exceptions
from API import endpoints
from API.models import User, Room
from API.dependencies import database, auth
from . import schemas


class RoomsManager:
    session: AsyncSession
    user: User

    def __init__(self, session = Depends(database.get_async_session), user = Depends(auth.validate_user)):
        self.session = session
        self.user = user

    async def get(self, id: UUID) -> Room | None:
        db: AsyncSession = self.session
        response = await db.scalars(
            select(Room).where(Room.id == id).options(selectinload(Room.devices))
        )
        return response.first()

    async def create(self, create_room: schemas.CreateRoom) -> Room:
        db: AsyncSession = self.session
        house = await endpoints.house.HouseManager(db).get()

        if not house:
            raise exceptions.not_initialized

        room = Room(name = create_room.name, house_id = house.id, devices = [])
        db.add(room)
        await db.commit()

        return room

    async def patch(self, id: UUID, room: schemas.PatchRoom):
        db: AsyncSession = self.session
        values = {key: value for key, value in room.dict().items() if key != 'id'}
        await db.execute(update(Room).values(**values).where(Room.id == id))
        await db.commit()

    async def delete(self, room_id: UUID):
        db: AsyncSession = self.session
        room = await self.get(room_id)
        if room:
            await db.delete(room)
            await db.commit()
        else:
            raise exceptions.not_found
