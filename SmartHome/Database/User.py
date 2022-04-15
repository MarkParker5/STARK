from General import UUID
from .NamedIdentifable import NamedIdentifable
from .EntityManager import EntityManager
from tables import users as usersTable


class User(NamedIdentifable):
    pass

class UsersManager(EntityManager):

    objectType = User
    table = usersTable

    @property
    def user(self) -> User: return self.object

    @classmethod
    def fromDict(cls, dict) -> User:
        user = User()
        user.id = UUID(dict['id'])
        user.name = dict['name']
        return user

    @classmethod
    def dict(self) -> Dict[str, Any]:
        return {
            'id': self.user.id,
            'name': self.user.name
        }

    @property
    def houses() -> [Room]:
        return [cls.fromDict(dict) for dict in tables.houses.where(f'id = {self.id}')]
