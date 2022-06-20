from sqlalchemy import select

from Merlin import Merlin, MerlinMessage
from API.dependencies import database
from API.models import Device, DeviceModelParameter
from . import schemas


class WSManager:
    merlin = Merlin()

    def merlin_send(self, data: schemas.MerlinData):
        db = database.get_session()

        try:
            device = db.get(Device, data.device_id)
            model_parameter = db.execute(
                select(DeviceModelParameter)
                .where(
                    DeviceModelParameter.devicemodel_id == device.model.id,
                    DeviceModelParameter.parameter_id == data.parameter_id
                )
            ).scalar_one()
        except: # TODO: Specify exceptions
            return

        self.merlin.send(MerlinMessage(device.urdi, model_parameter.f, data.value))
