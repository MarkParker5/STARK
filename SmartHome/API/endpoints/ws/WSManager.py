from SmartHome.Merlin import Merlin, MerlinMessage
from SmartHome.API.dependencies import database
from SmartHome.API.models import Device
from . import schemas


class WSManager:
    merlin = Merlin()

    def merlin_send(self, data: schemas.MerlinData):
        print(data)
        return
        # raise Exception('Not implemented')

        db = database.get_session()

        device = db.get(Device, data.device_id)
        if not device:
            return

        parameter = next([p for p in device.parameters if p.id == data.parameter_id], None)
        if not parameter:
            return

        # f = #device.parameters.index(parameter)
        x = data.value
        self.merlin.send(MerlinMessage(device.urdi, f, x))

    def merlin_send_raw(self, data: schemas.MerlinRaw):
        self.merlin.send(MerlinMessage(data.urdi, data.f, data.x))
