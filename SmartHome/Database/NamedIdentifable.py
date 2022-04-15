from ABC import ABC
from General import Identifable


class NamedIdentifable(Identifable, ABC):
    name: str
