from uuid import UUID

from fastapi import Depends
from sqlalchemy import select, update, delete
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from API.models import Device, DeviceParameterAssociation
from API.dependencies import database
from API import exceptions
from . import schemas
from ..schemas import DeviceParameter, Parameter


class DevicesManager:
    session: AsyncSession

    def __init__(self, session = Depends(database.get_async_session)):
        self.session = session

    async def get(self, id: UUID) -> Device | None:
        db: AsyncSession = self.session
        return await db.get(Device, id)

    async def state(self, id: UUID) -> schemas.DeviceState | None:
        db: AsyncSession = self.session
        device = await db.get(Device, id)

        if not device:
            return None

        device_state = schemas.DeviceState(**schemas.Device.from_orm(device).dict())

        async with database.async_engine.begin() as conn:
            parameters = await conn.run_sync(DevicesManager._read_parameters, device)

        device_state.parameters = list(map(DevicesManager._map_parameter, parameters))

        return device_state

    async def create(self, create_device: schemas.CreateDevice) -> Device:
        db: AsyncSession = self.session
        device = Device(
            id = create_device.id, # TODO: validate id
            name = create_device.name,
            urdi = 1, # TODO: parse from id
            room_id = create_device.room_id, # TODO: validate room
            model_id = create_device.model_id, # TODO: validate by parsed id
        )
        db.add(device)
        await db.commit()
        await db.refresh(device)
        return device

    async def patch(self, id: UUID, device: schemas.PatchDevice):
        db: AsyncSession = self.session
        values = {key: value for key, value in device.dict().items() if key != 'id'}
        await db.execute(update(Device).values(**values).where(Device.id == id))
        await db.commit()

    async def delete(self, device_id: UUID):
        db: AsyncSession = self.session
        device = await self.get(device_id)
        if device: # and device.house.owner_id == self.owner_id:
            await db.delete(device)
            await db.commit()
        else:
            raise exceptions.not_found

    @staticmethod
    def _read_parameters(_, device: Device) -> list[DeviceParameter]:
        return device.parameters

    @staticmethod
    def _map_parameter(association: DeviceParameterAssociation) -> DeviceParameter:
        parameter = Parameter.from_orm(association.parameter)
        device_parameter = DeviceParameter(**{**parameter.dict(), 'value': association.value})
        return device_parameter
