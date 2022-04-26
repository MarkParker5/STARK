from uuid import UUID
from pydantic import BaseModel


class CreateDevice(BaseModel):
    name: str

class PatchDevice(BaseModel):
    name: str | None

class Device(BaseModel):
    id: UUID
    name: str

    class Config:
        orm_mode = True
