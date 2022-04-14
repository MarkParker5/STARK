from typing import Optional
import uuid

class UUID(uuid.UUID):

    def __new__(cls, string: Optional[str] = None):
        if string:
            return super().__new__(cls)
        else:
            return uuid.uuid1()

    def __str__(self) -> str:
        return self.hex
