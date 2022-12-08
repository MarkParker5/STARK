from __future__ import annotations
from .UUID import UUID

class Identifable():
    id: UUID = UUID()

    def __eq__(self, other: Identifable) -> bool:
        return self.id == other.id

    def __ne__(self, other: Identifable) -> bool:
        return self.id != other.id
