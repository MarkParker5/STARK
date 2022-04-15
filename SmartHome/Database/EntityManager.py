from ABC import ABC
from .DBTable import DBTable
from General import Identifable


class EntityManager(Identifable, ABC):

    objectType: Identifable # abstract
    table: DBTable # abstract
    object: objectType

    def __init__(self, object: objectType):
        self.object = object

    # Abstract

    @abstractmethod
    @classmethod
    @property
    def table(cls) -> DBTable:
        pass

    @abstractmethod
    @classmethod
    def fromDict(cls, dict: Dict[str, Any]) -> objectType:
        pass

    @abstractmethod
    @classmethod
    def dict(self) -> Dict[str, Any]:
        pass

    # -------------------------------------

    @property
    @classmethod
    def all(cls) -> List[objectType]:
        return [cls.fromDict(dict) for dict in cls.table.all()]

    @property
    @classmethod
    def first(cls) -> List[objectType]:
        return cls.fromDict(tables.houses.first())

    @classmethod
    def get(cls, id: UUID) -> Optional[objectType]:
        return cls.fromDict(cls.table.get(id))

    def save(self):
        if self.table.get(self.object.id):
            self.table.update(self.dict)
        else:
            self.table.create(self.dict)

    @classmethod
    def clear(self):
        self.table.drop()
