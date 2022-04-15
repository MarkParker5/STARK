from General import UUID
from .NamedIdentifable import NamedIdentifable
from .EntityManager import EntityManager
from tables import rooms as roomsTable


class Room(NamedIdentifable):
    pass

class RoomsManager(EntityManager):

    objectType = Room
    table = roomsTable

    @property
    def room(self) -> Room: return self.object

    @classmethod
    def fromDict(cls, dict) -> Room:
        room = Room()
        room.id = UUID(dict['id'])
        room.name = dict['name']
        return room

    @classmethod
    def dict(self) -> Dict[str, Any]:
        return {
            'id': self.room.id,
            'name': self.room.name
        }

    @property
    def devices() -> List[Device]:
        [cls.fromDict(dict) for dict in tables.devices.where(f'id = {self.id}')]
