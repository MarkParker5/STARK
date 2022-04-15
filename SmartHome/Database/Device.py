from General import UUID
from .NamedIdentifable import NamedIdentifable
from .EntityManager import EntityManager
from tables import device as devicesTable


class Device(NamedIdentifable):
    urdi: bytes
    room_id: UUID
    model_id: UUID
    parameters: List[UUID]

class DevicesManager(EntityManager):

    objectType = Device
    table = devicesTable

    @property
    def device(self) -> Device: return self.object

    @classmethod
    def fromDict(cls, dict) -> Device:
        device = Device()
        device.id = UUID(dict['id'])
        device.name = dict['name']
        device.urdi = dict['urdi']
        device.room_id = UUID(dict['room_id'])
        device.model_id = UUID(dict['model_id'])
        device.parameters = dict['parameters'][1:-1].replace(' ', '').split(',')
        return device

    @classmethod
    def dict(self) -> Dict[str, Any]:
        return {
            'id': self.device.id,
            'name': self.device.name,
            'urdi': self.device.urdi,
            'room_id': self.device.room_id,
            'model_id': self.device.model_id,
            'parameters': self.device.parameters
        }

    @property
    def room(self) -> Room:
        return RoomsManager.get(self.device.room_id)

    @property
    def model(self) -> DeviceModel:
        return DeviceModelsManager.get(self.device.model_id)
