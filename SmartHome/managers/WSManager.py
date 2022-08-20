from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic.error_wrappers import ValidationError

import database
from hardware.Merlin import merlin, MerlinMessage
from models import Device, DeviceModelParameter
from schemas.ws import SocketType, SocketData, MerlinData


class WSManager:
    session: AsyncSession

    def __inti__(self, session: AsyncSession):
        self.session = session

    async def handle_message(self, msg: str):
        socket = SocketData.parse_raw(msg)
        try:
            socket = SocketData.parse_raw(msg)
        except ValidationError:
            return

        match socket.type:
            case SocketType.merlin:
                merlin_data = MerlinData(**socket.data)
                # try:
                #     merlin_data = MerlinData(**socket.data)
                # except: # TODO: specify exception
                #     return
                await self.merlin_send(merlin_data)

    async def merlin_send(self, data: MerlinData):
        db: AsyncSession = self.session
        try:
            if message := await self._get_message(db, data):
                merlin.send(message)
        finally:
            await db.close()

    async def _get_message(self, db: AsyncSession, data: MerlinData) -> MerlinMessage | None:
        device = await db.get(Device, data.device_id)

        if not device:
            return None

        result = await db.execute(
            select(DeviceModelParameter)
            .where(
                DeviceModelParameter.devicemodel_id == device.model.id,
                DeviceModelParameter.parameter_id == data.parameter_id
            )
        )

        model_parameter = result.scalar_one()

        return MerlinMessage(device.urdi, model_parameter.f, int(data.value))
