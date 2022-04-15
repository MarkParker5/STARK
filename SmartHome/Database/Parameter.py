from General import UUID
from .NamedIdentifable import NamedIdentifable
from .EntityManager import EntityManager
from tables import parameters as parametersTable
from .ParameterType import ParameterType

class Parameter(NamedIdentifable):
    type: ParameterType

class ParametersManager(EntityManager):

    objectType = Parameter
    table = parametersTable

    @property
    def parameter(self) -> Parameter: return self.object

    @classmethod
    def fromDict(cls, dict) -> Parameter:
        parameter = Parameter()
        parameter.id = UUID(dict['id'])
        parameter.name = dict['name']
        parameter.type = ParameterType(dict['type'])
        return deviceModel

    @classmethod
    def dict(self) -> Dict[str, Any]:
        return {
            'id': self.parameter.id,
            'name': self.parameter.name,
            'type': self.parameter.type,
        }
