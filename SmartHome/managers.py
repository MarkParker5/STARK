from .DBTable import DBTable
from . import tables
from .models import *

class UsersManager:
    user: User

    def __init__(self, user: User):
        self.user = user

    @property
    @classmethod
    def all(cls) -> List[Room]:
        return [cls.fromDict(dict) for dict in tables.houses.all()]

    @classmethod
    def get(cls, id: UUID) -> Optional[House]:
        return cls.fromDict(tables.houses.get(id))

    @classmethod
    def fromDict(cls, dict) -> User:
        user = User()
        user.id = UUID(dict['id'])
        user.name = dict['name']
        return user

    @property
    def houses() -> [Room]:
        return [cls.fromDict(dict) for dict in tables.houses.where(f'id = {self.id}')]

class HousesManager:
    house: House

    def __init__(self, house: House):
        self.house = house

    @property
    @classmethod
    def all(cls) -> List[Room]:
        return [cls.fromDict(dict) for dict in tables.houses.all()]

    @classmethod
    def get(cls, id: UUID) -> Optional[House]:
        return cls.fromDict(tables.houses.get(id))

    @classmethod
    def fromDict(cls, dict) -> House:
        house = House()
        house.id = UUID(dict['id'])
        house.name = dict['name']
        house.owner_id = UsersManager.get(dict['owner_id'])
        return house

    @property
    def rooms() -> [Room]:
        return [cls.fromDict(dict) for dict in tables.rooms.where(f'id = {self.id}')]

    @property
    def owner(self) -> User:
        return UsersManager.get(self.owner_id)

class RoomsManager:
    room: Room

    def __init__(self, room: Room):
        self.room = room

    @property
    @classmethod
    def all(cls) -> List[Room]:
        return [cls.fromDict(dict) for dict in tables.rooms.all()]

    @classmethod
    def get(cls, id: UUID) -> Room:
        return cls.fromDict(tables.rooms.get(id))

    @classmethod
    def fromDict(cls, dict) -> Room:
        room = Room()
        room.id = UUID(dict['id'])
        room.name = dict['name']
        return room

    @property
    def devices() -> List[Device]:
        [cls.fromDict(dict) for dict in tables.devices.where(f'id = {self.id}')]

class DevicesManager:
    device: Device

    def __init__(self, device: Device):
        self.device = device

    @property
    @classmethod
    def all(cls) -> List[Device]:
        return [cls.fromDict(dict) for dict in tables.devices.all()]

    @classmethod
    def get(cls, id: UUID) -> Optional[Device]:
        return cls.fromDict(tables.devices.get(id))

    @classmethod
    def fromDict(cls, dict) -> Device:
        device = Device()
        device.id = UUID(dict['id'])
        device.name = dict['name']
        device.urdi = dict['urdi']
        device.room_id = UUID(dict['room_id'])
        device.model_id = UUID(dict['model_id'])
        return device

    @property
    def room(self) -> Room:
        return RoomsManager.get(self.room_id)

    @property
    def model(self) -> DeviceModel:
        return DeviceModelsManager.get(self.model_id)

class DeviceModelsManager:
    deviceModel: DeviceModel

    def __init__(self, deviceModel: DeviceModel):
        self.deviceModel = deviceModel

    @property
    @classmethod
    def all(cls) -> List[DeviceModel]:
        return [cls.fromDict(dict) for dict in tables.deviceModels.all()]

    @classmethod
    def get(cls, id: UUID) -> Optional[DeviceModel]:
        return cls.fromDict(tables.deviceModels.get(id))

    @classmethod
    def fromDict(cls, dict) -> DeviceModel:
        deviceModel = DeviceModel()
        deviceModel.id = UUID(dict['id'])
        deviceModel.name = dict['name']
        return deviceModel

    @property
    def parameters() -> List[Parameter]:
        [cls.fromDict(dict) for dict in tables.parameters.where(f'id = {self.id}')]

class ParametersManager:
    parameter: Parameter

    def __init__(self, parameter: Parameter):
        self.parameter = parameter

    @property
    @classmethod
    def all(cls) -> List[Parameter]:
        return [cls.fromDict(dict) for dict in tables.parameters.all()]

    @classmethod
    def get(cls, id: UUID) -> Optional[Parameter]:
        return cls.fromDict(tables.parameters.get(id))

    @classmethod
    def fromDict(cls, dict) -> Parameter:
        parameter = Parameter()
        parameter.id = UUID(dict['id'])
        parameter.name = dict['name']
        parameter.type = ParameterType(dict['type'])
        return deviceModel
