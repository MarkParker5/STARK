from uuid import UUID
from pydantic import BaseModel


class CreateRoom(BaseModel):
    name: str

class PatchRoom(BaseModel):
    name: str

class Room(BaseModel):
    id: UUID
    name: str

    class Config:
        orm_mode = True
