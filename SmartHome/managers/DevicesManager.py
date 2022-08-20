from uuid import UUID
from fastapi import Depends
from sqlalchemy import select, update, delete
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from exceptions.Internal import InternalException, ExceptionCode
from AUID import AUID
import database
from models import (
    User,
    Device,
    DeviceModel,
    DeviceParameterAssociation,
    DeviceParameterAssociation
)
from schemas.device import (
    DeviceParameter,
    Parameter,
    DeviceState,
    DevicePatch,
    DeviceCreate,
    Device as DeviceScheme
)


class DevicesManager:
    session: AsyncSession

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get(self, id: UUID) -> Device:
        db: AsyncSession = self.session
        if device := await db.get(Device, id):
            return device
        else:
            raise InternalException(ExceptionCode.not_found, 'Device not found')

    async def state(self, id: UUID) -> DeviceState | None:
        db: AsyncSession = self.session
        device = await self.get(id)

        device_state = DeviceState(**DeviceScheme.from_orm(device).dict())

        async with database.async_engine.begin() as conn:
            parameters = await conn.run_sync(DevicesManager._read_parameters, device)

        device_state.parameters = list(map(DevicesManager._map_parameter, parameters))

        return device_state

    async def create(self, create_device: DeviceCreate) -> Device:
        db: AsyncSession = self.session

        id = AUID(bytes=create_device.id.bytes)
        model_id = AUID.new(model=id.items.model, now=None)
        urdi = id.items.urdi

        model = await db.get(DeviceModel, model_id)

        if not model:
            raise InternalException(
                code = ExceptionCode.invalid_format,
                msg = 'Unknown device id',
                debug = f'Unknown model in auid"{id}"'
            )

        if (await db.scalars(select(Device).where(Device.urdi == urdi))).first():
            raise InternalException(
                code = ExceptionCode.invalid_format,
                msg = 'Device with this id already exist'
            )

        device = Device(
            id = create_device.id,
            name = create_device.name,
            urdi = urdi,
            room_id = create_device.room_id,
            model_id = model_id
        )

        for model_parameter in model.parameters:
            device_parameter = DeviceParameterAssociation(
                device_id = device.id,
                parameter_id = model_parameter.parameter.id
            )
            db.add(device_parameter)

        db.add(device)
        await db.commit()
        await db.refresh(device)

        return device

    async def patch(self, id: UUID, device: DevicePatch):
        db: AsyncSession = self.session
        values = {key: value for key, value in device.dict().items() if key != 'id'}
        await db.execute(update(Device).values(**values).where(Device.id == id))
        await db.commit()

    async def delete(self, device_id: UUID):
        db: AsyncSession = self.session
        device = await self.get(device_id)
        if device:
            await db.delete(device)
            await db.commit()
        else:
            raise InternalException(
                code = ExceptionCode.not_found,
                msg = 'Device not found'
            )

    @staticmethod
    def _read_parameters(_, device: Device) -> list[DeviceParameter]:
        return device.parameters

    @staticmethod
    def _map_parameter(association: DeviceParameterAssociation) -> DeviceParameter:
        parameter = Parameter.from_orm(association.parameter)
        device_parameter = DeviceParameter(**{**parameter.dict(), 'value': association.value})
        return device_parameter
