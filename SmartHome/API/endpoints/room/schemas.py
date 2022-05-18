from uuid import UUID
from pydantic import BaseModel
from ..device.schemas import Device


class PatchRoom(BaseModel):
    name: str

class Room(BaseModel):
    id: UUID
    name: str
    devices: list[Device]

    class Config:
        orm_mode = True
