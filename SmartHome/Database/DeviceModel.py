from General import UUID
from .NamedIdentifable import NamedIdentifable
from .EntityManager import EntityManager
from tables import deviceModels as deviceModelsTable


class DeviceModel(NamedIdentifable):
    pass

class DeviceModelsManager(EntityManager):

    objectType = DeviceModel
    table = deviceModelsTable

    @property
    def deviceModel(self) -> DeviceModel: return self.object

    @classmethod
    def fromDict(cls, dict) -> DeviceModel:
        deviceModel = DeviceModel()
        deviceModel.id = UUID(dict['id'])
        deviceModel.name = dict['name']
        return deviceModel

    @classmethod
    def dict(self) -> Dict[str, Any]:
        return {
            'id': self.deviceModel.id,
            'name': self.deviceModel.name,
        }

    @property
    def parameters() -> List[Parameter]:
        [cls.fromDict(dict) for dict in tables.parameters.where(f'id = {self.id}')]
