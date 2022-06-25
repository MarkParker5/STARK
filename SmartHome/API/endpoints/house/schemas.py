from uuid import UUID
from pydantic import BaseModel
from ..hub.schemas import Hub
from ..room.schemas import RoomInfo


class House(BaseModel):
    id: UUID
    name: str
    hubs: list[Hub]
    rooms: list[RoomInfo]

    class Config:
        orm_mode = True
