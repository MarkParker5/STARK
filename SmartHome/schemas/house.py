from uuid import UUID
from pydantic import BaseModel
from .hub import Hub
from .room import RoomInfo


class HousePatch(BaseModel):
    id: UUID
    name: str

    class Config:
        orm_mode = True

class House(HousePatch):
    hubs: list[Hub]
    rooms: list[RoomInfo]
