from .Database import *
from .Merlin import *

class SmartHomeManager:
    house: House

    def __init__(self, house: House):
        self.house = house

    def addDevice(name: str, room_id: UUID, urdi: bytes) -> Device:
        device = Device()
        device.name = name
        device.room_id = room_id
        device.urdi = urdi
        DevicesManager(device).save()
        return device

    def deviceSet(value: Any, parameter_id: UUID, device_id: UUID):
        device = DevicesManager.get(device_id)
        parameter = ParametersManager.get(parameter_id)
        f = device.parameters.index(parameter_id)
        x = parameter.type.toByte(value)
        Merlin.send(MerlinMessage(device.urdi, f, x))
