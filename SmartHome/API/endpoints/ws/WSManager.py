from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from Merlin import Merlin, MerlinMessage
from API.dependencies import database
from API.models import Device, DeviceModelParameter
from .schemas import MerlinData


class WSManager:
    merlin = Merlin()

    async def merlin_send(self, data: MerlinData):
        db: AsyncSession = database.create_async_session()
        try:
            if message := await self._get_message(db, data):
                self.merlin.send(message)
        finally:
            await db.close()

    async def _get_message(self, db: AsyncSession, data: MerlinData) -> MerlinMessage | None:
        device = await db.get(Device, data.device_id)

        if not device:
            return None

        response = await db.execute(
            select(DeviceModelParameter)
            .where(
                DeviceModelParameter.devicemodel_id == device.model.id,
                DeviceModelParameter.parameter_id == data.parameter_id
            )
        )

        model_parameter = response.scalar_one()

        return MerlinMessage(device.urdi, model_parameter.f, data.value)
