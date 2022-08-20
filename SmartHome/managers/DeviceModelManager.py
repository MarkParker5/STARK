from uuid import UUID
from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession

import database
from models import DeviceModel, Parameter, DeviceModelParameter
from schemas.device import DeviceModelInfo, DeviceModel as DeviceModelScheme


class DeviceModelManager:
    session: AsyncSession

    def __init__(self, session: AsyncSession):
        self.session = session

    async def save(self, scheme: DeviceModelInfo | DeviceModelScheme):
        db: AsyncSession = self.session

        device_model = DeviceModel(id = scheme.id, name = scheme.name)
        db.add(device_model)
        # if device_model := await db.get(DeviceModel, scheme.id):
        #     device_model.name = scheme.name
        # else:

        if isinstance(scheme, DeviceModelScheme):
            for parameter_scheme in scheme.parameters:
                # if parameter := await db.get(Parameter, parameter_scheme.id):
                #     pass
                # else:
                db.add(Parameter(parameter_scheme.id, parameter_scheme.name, parameter_scheme.value_type))
                db.add(DeviceModelParameter(devicemodel_id = scheme.id, parameter_id = parameter_scheme.id))

        await db.commit()
