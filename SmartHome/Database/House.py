from General import UUID
from .NamedIdentifable import NamedIdentifable
from .EntityManager import EntityManager
from tables import houses as housesTable
from .UsersManager import UsersManager


class House(NamedIdentifable):
    owner_id: UUID

class HousesManager(EntityManager):

    objectType: House
    table = housesTable

    @property
    def house(self) -> House: return self.object

    @classmethod
    def fromDict(cls, dict) -> House:
        house = House()
        house.id = UUID(dict['id'])
        house.name = dict['name']
        house.owner_id = UsersManager.get(dict['owner_id'])
        return house

    @classmethod
    def dict(self) -> Dict[str, Any]:
        return {
            'id': self.house.id,
            'name': self.house.name,
            'owner_id': self.house.owner_id
        }

    @property
    def rooms() -> [Room]:
        return [cls.fromDict(dict) for dict in tables.rooms.where(f'id = {self.id}')]

    @property
    def owner(self) -> User:
        return UsersManager.get(self.owner_id)
